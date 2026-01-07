from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===== COMPANY DETAILS (SAFE TEXT) =====
COMPANY_NAME = "Radhekrishna Engineering"
COMPANY_ADDRESS = "Gujarat, India"
COMPANY_PHONE = "9XXXXXXXXX"
# =====================================


BILL_HEADINGS = {
    "company_name": "RADHEKRISHNA ENGINEERING",
    "invoice_title": "TAX INVOICE",
    "bold_defaults": [
        "Product Name", "Qty", "Rate", "Amount",
        "Sub Total", "GST", "Grand Total"
    ]
}
# Company Info (SAFE TEXT)
COMPANY_INFO = {
    "name": "Radhekrishna Engineering",
    "address": "Gujarat, India",
    "phone": "9XXXXXXXXX"
}




def generate_bill_pdf(bill_id: int, items: list, totals: dict, file_path: str):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    # Company Heading (BOLD)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, COMPANY_NAME)
    y -= 15
    c.drawString(50, y, COMPANY_ADDRESS)
    y -= 15
    c.drawString(50, y, f"Phone: {COMPANY_PHONE}")

    y -= 30

    # Table Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qty")
    c.drawString(300, y, "Rate")
    c.drawString(360, y, "Amount")
    y -= 20

    # Table Content
    c.setFont("Helvetica", 10)
    for item in items:
        c.drawString(50, y, item["item_name"])
        c.drawString(250, y, str(item["quantity"]))
        c.drawString(300, y, str(item["rate"]))
        c.drawString(360, y, str(item["total"]))
        y -= 15

    y -= 20

    # Totals (BOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, f"Sub Total: {totals['sub_total']}")
    y -= 15
    c.drawString(50, y, f"GST: {totals['gst_amount']}")
    y -= 15
    c.drawString(50, y, f"Grand Total: {totals['grand_total']}")

    c.showPage()
    c.save()
