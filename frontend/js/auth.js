async function login() {

  const email = document.querySelector('input[type="email"]').value;
  const password = document.querySelector('input[type="password"]').value;

  if (!email || !password) {
    alert("Email aur Password dono bharo");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    if (!response.ok) {
      alert("Login failed ❌");
      return;
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token);

    window.location.href = "home.html";

  } catch (error) {
    alert("Server error");
    console.error(error);
  }
}
