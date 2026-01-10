// Page load होते ही factories load हों
document.addEventListener("DOMContentLoaded", () => {
  loadFactories();
});

async function loadFactories() {

  // 1️⃣ Token लो
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    window.location.href = "index.html";
    return;
  }

  try {
    // 2️⃣ Backend call
    const response = await fetch("http://127.0.0.1:8000/factories", {
      method: "GET",
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    // 3️⃣ Token invalid
    if (response.status === 401) {
      alert("Session expired, login again");
      localStorage.removeItem("token");
      window.location.href = "index.html";
      return;
    }

    // 4️⃣ Data लो
    const factories = await response.json();

    // 5️⃣ HTML element लो
    const list = document.getElementById("factoryList");
    list.innerHTML = "";

    // 6️⃣ Loop करके UI बनाओ
    factories.forEach(factory => {

      const card = document.createElement("div");
      card.className = "factory-card";

      card.innerHTML = `
        <h3>${factory.name}</h3>
        <p>${factory.location ? factory.location : ""}</p>
      `;

      // 7️⃣ Factory select
      card.onclick = function () {
        localStorage.setItem("factory_id", factory.id);
        window.location.href = "bill_list.html";
      };

      list.appendChild(card);
    });

  } catch (error) {
    console.error(error);
    alert("Backend error: factories load nahi hui");
  }
}
