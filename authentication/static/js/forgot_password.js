document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("forgot-password-form");
    const emailField = document.getElementById("email");

    // Function to validate email format
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
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
                // Display error message from server
                await Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: result.error || "Failed to send the reset link. Please try again.",
                });
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
