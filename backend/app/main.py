import os
import shutil
from .reports import generate_bill_pdf
from .auth import get_current_user
from .auth import create_access_token
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models, schemas
from .auth import hash_password, verify_password
from .email_utils import send_reset_email
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# 👇 YE LINE VERY IMPORTANT HAI
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Radhekrishna Engineering Billing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/forgot-password")
def forgot_password(data: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_access_token({"sub": user.email})

    send_reset_email(user.email, reset_token)

    return {"message": "Password reset email sent"}


@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {
        "message": "You are authorized",
        "user": current_user
    }

@app.post("/factories", response_model=schemas.FactoryResponse)
def add_factory(
    factory: schemas.FactoryCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_factory = models.Factory(
        name=factory.name,
        address=factory.address
    )
    db.add(new_factory)
    db.commit()
    db.refresh(new_factory)
    return new_factory

@app.get("/factories", response_model=list[schemas.FactoryResponse])
def list_factories(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return db.query(models.Factory).all()

@app.post("/bills")
def create_bill(
    bill: schemas.BillCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Create bill
    new_bill = models.Bill(factory_id=bill.factory_id)
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    grand_total = 0

    # Create bill items
    for item in bill.items:
        item_total = item.quantity * item.rate
        grand_total += item_total

        bill_item = models.BillItem(
            bill_id=new_bill.id,
            item_name=item.item_name,
            quantity=item.quantity,
            rate=item.rate,
            total=item_total
        )
        db.add(bill_item)

    db.commit()

    gst_amount = 0

    # agar GST ON hai
    if getattr(new_bill, "gst_enabled", 0) == 1:
        gst_amount = int(grand_total * new_bill.gst_percent / 100)

    return {
        "bill_id": new_bill.id,
        "sub_total": grand_total,
        "gst_amount": gst_amount,
        "grand_total": grand_total + gst_amount
    }


@app.get("/bills/{factory_id}", response_model=list[schemas.BillResponse])
def list_bills(
    factory_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return db.query(models.Bill).filter(
        models.Bill.factory_id == factory_id
    ).all()


@app.put("/bills/{bill_id}")
def update_bill(
    bill_id: int,
    payload: schemas.BillUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # purane items delete
    db.query(models.BillItem).filter(models.BillItem.bill_id == bill_id).delete()

    grand_total = 0
    for item in payload.items:
        item_total = item.quantity * item.rate
        grand_total += item_total
        db.add(models.BillItem(
            bill_id=bill_id,
            item_name=item.item_name,
            quantity=item.quantity,
            rate=item.rate,
            total=item_total
        ))

    db.commit()
    return {"message": "Bill updated", "grand_total": grand_total}


@app.get("/bills/{bill_id}/pdf")
def bill_pdf(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    items = db.query(models.BillItem).filter(models.BillItem.bill_id == bill_id).all()
    sub_total = sum(i.total for i in items)
    gst_amount = int(sub_total * bill.gst_percent / 100) if bill.gst_enabled else 0

    path = f"bill_{bill_id}.pdf"
    generate_bill_pdf(
        bill_id,
        [i.__dict__ for i in items],
        {
            "sub_total": sub_total,
            "gst_amount": gst_amount,
            "grand_total": sub_total + gst_amount
        },
        path
    )
    return {"pdf": os.path.abspath(path)}


@app.get("/bills/{bill_id}/pdf")
def generate_pdf(
    bill_id: int,
    db: Session = Depends(get_db),
    #current_user: str = Depends(get_current_user)
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    items = db.query(models.BillItem).filter(
        models.BillItem.bill_id == bill_id
    ).all()

    sub_total = sum(i.total for i in items)
    gst_amount = int(sub_total * bill.gst_percent / 100) if bill.gst_enabled else 0

    pdf_path = f"bill_{bill_id}.pdf"

    generate_bill_pdf(
        bill_id=bill_id,
        items=[i.__dict__ for i in items],
        totals={
            "sub_total": sub_total,
            "gst_amount": gst_amount,
            "grand_total": sub_total + gst_amount
        },
        file_path=pdf_path
    )
    # ===== AUTO BACKUP START =====
    backup_folder = "backup_pdfs"
    os.makedirs(backup_folder, exist_ok=True)

    backup_path = os.path.join(backup_folder, os.path.basename(pdf_path))
    shutil.copy(pdf_path, backup_path)
    # ===== AUTO BACKUP END =====

    return {
        "message": "PDF generated",
        "file_path": os.path.abspath(pdf_path)
    }

@app.get("/bills/{bill_id}/whatsapp")
def whatsapp_link(
    bill_id: int,
    current_user: str = Depends(get_current_user)
):
    message = f"Bill #{bill_id} - Radhekrishna Engineering"
    link = f"https://wa.me/?text={message}"
    return {"whatsapp_link": link}



@app.get("/reports/monthly/{factory_id}")
def monthly_report(
    factory_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    bills = db.query(models.Bill).filter(
        models.Bill.factory_id == factory_id
    ).all()

    total = 0
    for bill in bills:
        items = db.query(models.BillItem).filter(
            models.BillItem.bill_id == bill.id
        ).all()
        total += sum(i.total for i in items)

    return {
        "factory_id": factory_id,
        "year": year,
        "month": month,
        "total_amount": total
    }
