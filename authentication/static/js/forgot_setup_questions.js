// ✅ Helper function to show error messages with SweetAlert
function showError(message) {
    Swal.fire({
        icon: "error",
        title: "Error",
        text: message,
        confirmButtonText: "OK",
    });
}

// ✅ Helper function to show success messages with SweetAlert
function showSuccess(message, redirectUrl) {
    Swal.fire({
        icon: "success",
        title: "Success",
        text: message,
        confirmButtonText: "Next",
    }).then(() => {
        if (redirectUrl) {
            window.location.href = redirectUrl;
        }
    });
}

// ✅ Show lock message in SweetAlert and update the page UI
function showTemporaryLock(timeRemaining) {
    let countdown = timeRemaining;

    // ✅ Show SweetAlert with countdown
    Swal.fire({
        icon: "warning",
        title: "Account Locked",
        html: `<p>Too many failed attempts.</p><p>Try again in <strong id="lock-timer">${countdown}</strong> minutes.</p>`,
        allowOutsideClick: false,
        showConfirmButton: false,
    });

    // ✅ Also update lock message inside the page
    const lockMessageDiv = document.getElementById("lock-message");
    const lockTimerDisplay = document.getElementById("lock-timer-display");

    if (lockMessageDiv && lockTimerDisplay) {
        lockMessageDiv.classList.remove("d-none"); // Show the lock message
        lockTimerDisplay.innerText = countdown; // Set initial time

        const timerInterval = setInterval(() => {
            countdown--;
            lockTimerDisplay.innerText = countdown; // Update display
            document.getElementById("lock-timer").innerText = countdown; // Update SweetAlert
            if (countdown <= 0) {
                clearInterval(timerInterval);
                location.reload(); // Reload page when countdown ends
            }
        }, 60000); // Update every minute
    }

    // ✅ Disable form submission while locked
    document.getElementById("forgot-security-questions-form").classList.add("disabled");
}

// ✅ Automatically convert input to lowercase
function enforceLowercaseInput() {
    document.querySelectorAll('input[type="text"]').forEach((input) => {
        input.addEventListener("input", function () {
            this.value = this.value.toLowerCase();
        });
    });
}

// ✅ Fetch and populate security questions
async function fetchSecurityQuestions(uidb64, token) {
    try {
        Swal.fire({
            title: "Loading security questions...",
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/forgot-setup-questions/${uidb64}/${token}/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        const data = await response.json();
        Swal.close();

        // ✅ If locked, prevent further actions
        if (response.status === 403 && data.locked_until) {
            const lockedUntil = new Date(data.locked_until);
            const now = new Date();
            const timeRemaining = Math.max(0, Math.ceil((lockedUntil - now) / 60000)); // Convert to minutes
            showTemporaryLock(timeRemaining);
            return;
        }

        // ✅ Populate security questions if not locked
        document.getElementById("security-question-1").innerText = data.question_1;
        document.getElementById("security-question-2").innerText = data.question_2;
        document.getElementById("security-question-3").innerText = data.question_3;

        document.querySelector('input[name="question_id_1"]').value = data.question_1_id;
        document.querySelector('input[name="question_id_2"]').value = data.question_2_id;
        document.querySelector('input[name="question_id_3"]').value = data.question_3_id;

    } catch (error) {
        console.error("Error fetching security questions:", error);
        showError("An error occurred while loading security questions.");
    }
}

// ✅ Handle form submission
async function submitForgotSecurityAnswers(event) {
    event.preventDefault();

    const form = document.getElementById("forgot-security-questions-form");
    const token = form.querySelector('input[name="token"]').value;
    const uidb64 = form.querySelector('input[name="uidb64"]').value;

    const answers = [
        {
            question_id: form.querySelector('input[name="question_id_1"]').value,
            answer: form.querySelector('input[name="security_answer_1"]').value.trim().toLowerCase(),
        },
        {
            question_id: form.querySelector('input[name="question_id_2"]').value,
            answer: form.querySelector('input[name="security_answer_2"]').value.trim().toLowerCase(),
        },
        {
            question_id: form.querySelector('input[name="question_id_3"]').value,
            answer: form.querySelector('input[name="security_answer_3"]').value.trim().toLowerCase(),
        },
    ];

    if (answers.some((item) => item.answer === "" || !item.question_id)) {
        showError("Please answer all security questions.");
        return;
    }

    try {
        Swal.fire({
            title: "Submitting...",
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/forgot-setup-questions/${uidb64}/${token}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: JSON.stringify({ answers }),
        });

        const result = await response.json();

        if (response.ok) {
            showSuccess("Answers verified! Redirecting to password reset.", result.redirect);
        } else {
            console.error("Verification Failed:", result);

            if (result.error.includes("Try again in")) {
                // ✅ Extract the minutes from the error message
                const minutesMatch = result.error.match(/\d+/);
                if (minutesMatch) {
                    const minutes = parseInt(minutesMatch[0]);
                    showTemporaryLock(minutes); // Show countdown alert
                } else {
                    showError(result.error || "Account temporarily locked.");
                }
            } else {
                showError(result.error || "Failed to validate answers.");
            }
        }
    } catch (error) {
        console.error("Error occurred:", error);
        showError("An error occurred while submitting answers.");
    }
}

// ✅ Check if user is temporarily locked
async function checkLockStatus(uidb64, token) {
    try {
        const response = await fetch(`/forgot-setup-questions/${uidb64}/${token}/lock-status/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        const data = await response.json();

        if (data.status === "Temporarily Locked" && data.locked_until) {
            const lockedUntil = new Date(data.locked_until);
            const now = new Date();
            const timeRemaining = Math.max(0, Math.ceil((lockedUntil - now) / 60000)); // Convert to minutes

            if (timeRemaining > 0) {
                showTemporaryLock(timeRemaining);
            }
        }
    } catch (error) {
        console.error("Error checking lock status:", error);
    }
}

// ✅ Initialize page
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("forgot-security-questions-form");
    const token = form.querySelector('input[name="token"]').value;
    const uidb64 = form.querySelector('input[name="uidb64"]').value;

    fetchSecurityQuestions(uidb64, token);
    enforceLowercaseInput();
    checkLockStatus(uidb64, token); // Check if the user is locked
    form.addEventListener("submit", submitForgotSecurityAnswers);
});
