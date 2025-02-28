document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("forgot-password-form");
    const emailField = document.getElementById("email");

    // Function to validate email format
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Function to handle cooldown messages
    function handleCooldown(response) {
        if (response.error && response.error.includes("wait")) {
            const minutesRemaining = response.error.match(/\d+/)[0];
            Swal.fire({
                icon: "info",
                title: "Cooldown in Effect",
                text: `You need to wait ${minutesRemaining} minute(s) before requesting another reset link.`,
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: response.error || "Failed to send the reset link. Please try again.",
            });
        }
    }

    // Form submission event listener
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = emailField.value.trim();

        // Validate email field
        if (!validateEmail(email)) {
            await Swal.fire({
                icon: "error",
                title: "Validation Error",
                text: "Please enter a valid email address.",
            });
            return;
        }

        // Show submitting alert
        Swal.fire({
            title: "Submitting...",
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading(),
        });

        // Prepare form data
        const formData = new FormData();
        formData.append("email", email);

        try {
            const response = await fetch("/forgot_password/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
            });

            const result = await response.json();

            if (response.ok) {
                // Display the success message
                await Swal.fire({
                    icon: "success",
                    title: "Success",
                    text: result.success || "A reset link has been sent to your email.",
                });
                form.reset();
            } else {
                // Handle cooldown or other errors
                handleCooldown(result);
            }
        } catch (error) {
            // Handle network or unexpected errors
            await Swal.fire({
                icon: "error",
                title: "Error",
                text: "An unexpected error occurred. Please try again later.",
            });
            console.error("Error submitting form:", error);
        }
    });
});
