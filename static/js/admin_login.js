document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const userNumberInput = document.getElementById("user_number");
    const passwordInput = document.getElementById("password");
    const unlockButton = document.getElementById("unlockButton");
    const lockMessage = document.getElementById("lockMessage");

    let loginAttempts = 0;
    let lockedUntil = null;

    // ✅ Function to get CSRF Token
    function getCSRFToken() {
        let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : getCookie("csrftoken");
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ✅ Function to show alerts
    function showAlert(icon, title, text) {
        Swal.fire({ icon, title, text });
    }

    // ✅ Function to check lock status & show countdown
    async function checkLockStatus() {
        if (!userNumberInput.value) return;

        try {
            const response = await fetch(`/check-lock-status/${userNumberInput.value}/`);
            const data = await response.json();

            if (data.status === "Temporarily Locked" && data.locked_until) {
                lockedUntil = new Date(data.locked_until);
                startCountdown();
                lockMessage.innerText = `Account locked until ${lockedUntil.toLocaleTimeString()}.`;
            } else {
                lockedUntil = null;
                lockMessage.innerText = "";
            }
        } catch (error) {
            console.error("Error checking lock status:", error);
        }
    }

    // ✅ Countdown Timer for Temporary Lock
    function startCountdown() {
        if (!lockedUntil) return;

        const interval = setInterval(() => {
            const now = new Date();
            const timeRemaining = Math.max(0, Math.floor((lockedUntil - now) / 1000));

            if (timeRemaining <= 0) {
                clearInterval(interval);
                location.reload(); // Reload page after countdown ends
            } else {
                lockMessage.innerText = `Account locked. Try again in ${timeRemaining} seconds.`;
            }
        }, 1000);
    }

    // ✅ Handle Login Form Submission
    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();
        handleLogin();
    });

    // ✅ Function to handle login request
    function handleLogin() {
        console.log("🔹 Submitting login request...");

        const formData = new FormData(loginForm);
        const payload = Object.fromEntries(formData.entries());

        Swal.fire({
            title: "Logging in...",
            text: "Please wait while we process your request.",
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        fetch("/admin_login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(payload),
        })
        .then(async (response) => {
            if (!response.ok) {
                const errorText = await response.text();
                console.error("🔴 Fetch error:", response.status, errorText);
                throw new Error(`HTTP Error: ${response.status} - ${errorText}`);
            }
            return response.json();
        })
        .then((data) => {
            console.log("✅ Server Response:", data);

            if (data.redirect_to) {
                Swal.fire({
                    icon: "success",
                    title: "Login Successful",
                    text: "Redirecting to your dashboard...",
                    timer: 2000,
                    showConfirmButton: false,
                }).then(() => {
                    window.location.href = data.redirect_to;
                });
            } else {
                showAlert("error", "Login Failed", data.error || "Invalid credentials!");
            }
        })
        .catch(error => {
            console.error("🔴 Error during login:", error);
            showAlert("error", "Login Error", "An unexpected error occurred.");
        });
    }

    // ✅ Handle Manual Unlock by Admin
    if (unlockButton) {
        unlockButton.addEventListener("click", async () => {
            try {
                const response = await fetch(`/unlock-user/${userNumberInput.value}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert("success", "User Unlocked", data.message);
                    location.reload();
                } else {
                    showAlert("error", "Unlock Failed", data.error || "Could not unlock user.");
                }
            } catch (error) {
                console.error("Error unlocking user:", error);
                showAlert("error", "Unlock Error", "An unexpected error occurred.");
            }
        });
    }

    // ✅ Function to toggle password visibility
    window.togglePassword = function () {
        const passwordInput = document.getElementById("password");
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
    };

    checkLockStatus(); // ✅ Check lock status on page load
});
