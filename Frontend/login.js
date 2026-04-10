/*=============== SHOW HIDE PASSWORD LOGIN ===============*/
const passwordAccess = (loginPass, loginEye) => {
  const input = document.getElementById(loginPass),
    iconEye = document.getElementById(loginEye);

  iconEye.addEventListener("click", () => {
    // Change password to text
    input.type === "password"
      ? (input.type = "text")
      : (input.type = "password");

    // Icon change
    iconEye.classList.toggle("ri-eye-fill");
    iconEye.classList.toggle("ri-eye-off-fill");
  });
};
passwordAccess("password", "loginPassword");

/*=============== SHOW HIDE PASSWORD CREATE ACCOUNT ===============*/
const passwordRegister = (loginPass, loginEye) => {
  const input = document.getElementById(loginPass),
    iconEye = document.getElementById(loginEye);

  iconEye.addEventListener("click", () => {
    // Change password to text
    input.type === "password"
      ? (input.type = "text")
      : (input.type = "password");

    // Icon change
    iconEye.classList.toggle("ri-eye-fill");
    iconEye.classList.toggle("ri-eye-off-fill");
  });
};
passwordRegister("passwordRegister", "loginPasswordCreate");
passwordRegister("confirmPassword", "confirmPasswordEye");

/*=============== SHOW HIDE LOGIN & CREATE ACCOUNT ===============*/
const loginAcessRegister = document.getElementById("loginAccessRegister"),
  buttonRegister = document.getElementById("loginButtonRegister"),
  buttonAccess = document.getElementById("loginButtonAccess");

buttonRegister.addEventListener("click", () => {
  loginAcessRegister.classList.add("active");
});

buttonAccess.addEventListener("click", () => {
  loginAcessRegister.classList.remove("active");
});

// ==========================
// BACKEND URL
// ==========================
const BASE_URL = "http://127.0.0.1:8000";

// ==========================
// LOGIN CONNECT
// ==========================
document
  .getElementById("loginForm")
  ?.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const captcha = document.getElementById("captchaInput").value;

    // ✅ GET SELECTED ROLE
    const selectedRole = document.querySelector(
      'input[name="loginRole"]:checked',
    )?.value;

    if (!selectedRole) {
      alert("Please select a role");
      return;
    }

    try {
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
          captcha: captcha,
          role: selectedRole, // ✅ SEND ROLE
        }),
      });

      const data = await response.json();

      if (response.ok && !data.error) {
        // ✅ Store role + name
        localStorage.setItem("userRole", data.role);
        localStorage.setItem("userName", data.name);

        window.location.href = "dashboard.html";
      } else {
        alert(data.error || "Login failed");
      }
    } catch (error) {
      console.error(error);
      alert("Server connection failed");
    }
  });

// ==========================
// REGISTER CONNECT
// ==========================
document
  .getElementById("registerForm")
  ?.addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const surname = document.getElementById("surname").value;
    const email = document.getElementById("emailRegister").value;
    const password = document.getElementById("passwordRegister").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    // ✅ GET SELECTED ROLE HERE (outside fetch)
    const selectedRole = document.querySelector(
      'input[name="registerRole"]:checked',
    )?.value;

    if (!selectedRole) {
      alert("Please select a role");
      return;
    }

    try {
      const response = await fetch(`${BASE_URL}/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name,
          surname: surname,
          email: email,
          password: password,
          confirm_password: confirmPassword,
          role: selectedRole,
        }),
      });

      const data = await response.json();

      if (response.ok && !data.error) {
        alert("Account created successfully!");
        document
          .getElementById("loginAccessRegister")
          .classList.remove("active");
      } else {
        alert(data.error || "Signup failed");
      }
    } catch (error) {
      console.error(error);
      alert("Server connection failed");
    }
  });

document.addEventListener("DOMContentLoaded", function () {
  refreshCaptcha();
});

function refreshCaptcha() {
  const BASE_URL = "http://127.0.0.1:8000";
  document.getElementById("captchaImage").src =
    BASE_URL + "/auth/generate-captcha?" + new Date().getTime();
}

// ==========================
// PASSWORD STRENGTH CHECK
// ==========================
const passwordInput = document.getElementById("passwordRegister");

passwordInput?.addEventListener("input", function () {
  const password = passwordInput.value;

  const lengthRule = document.getElementById("ruleLength");
  const upperRule = document.getElementById("ruleUpper");
  const numberRule = document.getElementById("ruleNumber");

  // Length
  if (password.length >= 8) {
    lengthRule.classList.add("valid");
    lengthRule.classList.remove("invalid");
  } else {
    lengthRule.classList.add("invalid");
    lengthRule.classList.remove("valid");
  }

  // Uppercase
  if (/[A-Z]/.test(password)) {
    upperRule.classList.add("valid");
    upperRule.classList.remove("invalid");
  } else {
    upperRule.classList.add("invalid");
    upperRule.classList.remove("valid");
  }

  // Number
  if (/[0-9]/.test(password)) {
    numberRule.classList.add("valid");
    numberRule.classList.remove("invalid");
  } else {
    numberRule.classList.add("invalid");
    numberRule.classList.remove("valid");
  }
});
