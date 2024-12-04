document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const emailField = document.querySelector('input[type="email"]');
    const fullNameField = document.querySelector('input[name="full_name"]');
    const fileInput = document.querySelector('input[type="file"]');
    const submitButton = document.querySelector('button[type="submit"]');

    // Modal elements
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));

    // Simple email validation (regex-based)
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Form validation function
    function validateForm(event) {
        let isValid = true;

        // Full name validation (not empty)
        if (fullNameField.value.trim() === '') {
            alert('Full Name is required.');
            isValid = false;
        }

        // Email validation
        if (!validateEmail(emailField.value)) {
            alert('Please enter a valid email address.');
            isValid = false;
        }

        // Prevent form submission if any validation fails
        if (!isValid) {
            event.preventDefault();  // Prevent form submission
        }
    }

    // Attach validation function to form submission
    form.addEventListener('submit', function (event) {
        // Show the loading modal when the form is submitted
        loadingModal.show();

        // Validate form inputs before proceeding
        validateForm(event);
        if (event.defaultPrevented) {
            loadingModal.hide();  // Hide loading modal if validation fails
            return;  // Prevent submission if validation fails
        }

        // Simulate server processing with setTimeout (replace with real form submission logic)
        setTimeout(function () {
            // Simulate success response from server
            const isSuccess = true; // Change this based on actual response

            // Hide loading modal after form submission processing
            loadingModal.hide();

            if (isSuccess) {
                // Show success modal on successful submission
                successModal.show();
            } else {
                // Show error modal if submission failed
                errorModal.show();
            }
        }, 2000);  // Simulated server delay (2 seconds)
    });

    // Success Modal Handler
    const okButton = document.querySelector('#successModal .btn-primary');
    if (okButton) {
        okButton.addEventListener('click', function () {
            successModal.hide(); // Close the success modal
            location.reload(); // Refresh the page
        });
    }

    // Error Modal Handler
    const closeButton = document.querySelector('#errorModal .btn-danger');
    if (closeButton) {
        closeButton.addEventListener('click', function () {
            errorModal.hide(); // Close the error modal
        });
    }

    // Optional: File input preview (for images)
    fileInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            // Only show a preview for image files
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const previewImage = document.createElement('img');
                    previewImage.src = e.target.result;
                    previewImage.style.maxWidth = '100px';
                    previewImage.style.marginTop = '10px';
                    fileInput.insertAdjacentElement('afterend', previewImage);
                };
                reader.readAsDataURL(file);
            } else {
                alert('Only image files can be previewed.');
            }
        }
    });

    // Adding an event listener to the button to navigate to admin login
    document.getElementById('adminLoginButton').addEventListener('click', function () {
        window.location.href = '/auth/admin_login/';  // Replace '/admin-login' with the correct URL for your admin login page
    });
});
