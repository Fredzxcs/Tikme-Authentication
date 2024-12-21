document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const emailField = document.querySelector('input[type="email"]');
    const fullNameField = document.querySelector('input[name="full_name"]');
    const fileInput = document.querySelector('input[type="file"]');
    const previewContainer = document.getElementById('preview-container');

    // Modal elements
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));

    // Function to validate email format
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Form validation
    function validateForm(event) {
        let isValid = true;

        if (fullNameField.value.trim() === '') {
            alert('Full Name is required.');
            isValid = false;
        }

        if (!validateEmail(emailField.value)) {
            alert('Please enter a valid email address.');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault(); // Prevent form submission if invalid
        }
    }

    // File upload preview and limit functionality
    let fileList = []; // Array to store the files

    function updatePreview() {
        previewContainer.innerHTML = ''; // Clear the preview

        fileList.forEach((file, index) => {
            const reader = new FileReader();

            reader.onload = function (e) {
                const wrapper = document.createElement('div');
                wrapper.className = 'preview-wrapper';

                const img = document.createElement('img');
                img.src = e.target.result;

                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn';
                removeBtn.innerText = 'X';

                removeBtn.addEventListener('click', function () {
                    fileList.splice(index, 1); // Remove the file from the array
                    updatePreview(); // Refresh the preview
                });

                wrapper.appendChild(img);
                wrapper.appendChild(removeBtn);
                previewContainer.appendChild(wrapper);
            };

            reader.readAsDataURL(file);
        });
    }

    fileInput.addEventListener('change', function () {
        const newFiles = Array.from(fileInput.files);

        if (fileList.length + newFiles.length > 3) {
            alert('You can only upload up to 3 files.');
            return;
        }

        fileList = [...fileList, ...newFiles]; // Append new files to the file list
        updatePreview();

        // Clear the input to allow adding the same file again if needed
        fileInput.value = '';
    });

    // Handle form submission
    form.addEventListener('submit', function (event) {
        validateForm(event);

        if (!event.defaultPrevented) {
            loadingModal.show();

            // Simulate form submission
            setTimeout(() => {
                loadingModal.hide();
                successModal.show();
            }, 2000);
        }
    });

    // Back button functionality
    const backButton = document.getElementById('adminLoginButton');
    backButton.addEventListener('click', function () {
        window.location.href = '/admin_login/'; // Replace with your desired URL
    });
});
