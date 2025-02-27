document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form');
    const currentPassword = document.getElementById('currentPassword');
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    const profilePictureInput = document.getElementById('profilePicture');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // CSRF token

    // Password validation guide elements
    const lengthGuide = document.getElementById('length');
    const uppercaseGuide = document.getElementById('uppercase');
    const lowercaseGuide = document.getElementById('lowercase');
    const digitGuide = document.getElementById('digit');

    // Real-time validation fields
    const fullName = document.getElementById('fullName');
    const email = document.getElementById('email');
    const phone = document.getElementById('phone');

    const fullNameError = document.getElementById('fullNameError');
    const emailError = document.getElementById('emailError');
    const phoneError = document.getElementById('phoneError');

    const nameRegex = /^[A-Za-z]+$/;
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    const phoneRegex = /^(09)[0-9]{9}$/;

    // Password visibility toggle function
    window.toggleVisibility = function(id) {
        const inputField = document.getElementById(id);
        if (inputField.type === "password") {
            inputField.type = "text";
        } else {
            inputField.type = "password";
        }
    }

    // Password validation
    function validatePassword() {
        const password = newPassword.value;
        let isValid = true;

        // Length validation
        if (password.length >= 8) {
            lengthGuide.classList.remove("invalid");
            lengthGuide.classList.add("valid");
        } else {
            lengthGuide.classList.remove("valid");
            lengthGuide.classList.add("invalid");
            isValid = false;
        }

        // Uppercase validation
        if (/[A-Z]/.test(password)) {
            uppercaseGuide.classList.remove("invalid");
            uppercaseGuide.classList.add("valid");
        } else {
            uppercaseGuide.classList.remove("valid");
            uppercaseGuide.classList.add("invalid");
            isValid = false;
        }

        // Lowercase validation
        if (/[a-z]/.test(password)) {
            lowercaseGuide.classList.remove("invalid");
            lowercaseGuide.classList.add("valid");
        } else {
            lowercaseGuide.classList.remove("valid");
            lowercaseGuide.classList.add("invalid");
            isValid = false;
        }

        // Digit validation
        if (/\d/.test(password)) {
            digitGuide.classList.remove("invalid");
            digitGuide.classList.add("valid");
        } else {
            digitGuide.classList.remove("valid");
            digitGuide.classList.add("invalid");
            isValid = false;
        }

        return isValid;
    }

    // Confirm password matching validation
    function confirmPasswordValidation() {
        if (newPassword.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords do not match");
        } else {
            confirmPassword.setCustomValidity("");
        }
    }

    // Real-time Validation for Personal Information fields
    fullName.addEventListener("input", () => {
        if (!nameRegex.test(fullName.value) || fullName.value.length < 2) {
            showError(fullName, "Only letters allowed (Min: 2 characters)", fullNameError);
        } else {
            clearError(fullName, fullNameError);
        }
    });

    email.addEventListener("input", () => {
        if (!emailRegex.test(email.value)) {
            showError(email, "Enter a valid email (example@mail.com)", emailError);
        } else {
            clearError(email, emailError);
        }
    });

    phone.addEventListener("input", () => {
        if (!phoneRegex.test(phone.value)) {
            showError(phone, "Enter a valid phone number", phoneError);
        } else {
            clearError(phone, phoneError);
        }
    });

    // Helper functions for error handling
    function showError(element, message, errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        element.classList.add('is-invalid');
    }

   // ✅ Fetch user details and populate fields
   fetch('/account_settings/', {
    method: 'GET',
    headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fullName.value = data.user.full_name || "";
            email.value = data.user.email;
            phone.value = data.user.phone_number || "";
        } else {
            console.error("Failed to load user settings:", data.message);
        }
    })
    .catch(error => console.error("Error fetching user settings:", error));


    function clearError(element, errorElement) {
        errorElement.style.display = 'none';
        element.classList.remove('is-invalid');
    }

    // ✅ Handle form submission (PATCH request)
    form.addEventListener('submit', function(e) {
        e.preventDefault();  // Prevent default form submission

        const formData = new FormData(form);
        const nameParts = fullName.value.trim().split(" ");
        formData.append("first_name", nameParts[0] || "");
        formData.append("last_name", nameParts.slice(1).join(" ") || "");

        fetch('/account_settings/', {
            method: 'PATCH',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({ icon: 'success', title: 'Success!', text: data.message });

                // ✅ Update UI after success
                fullName.value = formData.get("full_name");
                phone.value = formData.get("phone_number");
            } else {
                Swal.fire({ icon: 'error', title: 'Error!', text: data.message || "Something went wrong!" });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({ icon: 'error', title: 'Server Error', text: 'An unexpected error occurred. Please try again later.' });
        });
    });

    // Validate password matching on input change
    newPassword.addEventListener('input', validatePassword);
    confirmPassword.addEventListener('input', confirmPasswordValidation);

    // ✅ Preview profile picture before uploading
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', function() {
            const file = profilePictureInput.files[0];
            const reader = new FileReader();

            reader.onloadend = function() {
                const imgPreview = document.querySelector('.img-thumbnail');
                if (imgPreview) {
                    imgPreview.src = reader.result;
                }
            };

            if (file) {
                reader.readAsDataURL(file);
            }
        });
    }


    // Handle cancel button click
    const cancelButton = document.querySelector('.btn-secondary');
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            if (confirm("Are you sure you want to cancel the changes?")) {
                window.location.href = "/profile"; // Redirect to profile or other relevant page
            }
        });
    }
});
