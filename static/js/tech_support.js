document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const emailField = document.querySelector('input[type="email"]');
    const fullNameField = document.querySelector('input[name="full_name"]');
    const phoneField = document.querySelector('input[name="phone"]');
    const descriptionField = document.querySelector('textarea[name="description"]');
    const fileInput = document.querySelector('input[type="file"]');
    const previewContainer = document.getElementById('preview-container');

    // File storage
    let fileList = [];

    // Function to validate email format
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Form validation with SweetAlert
    async function validateForm() {
        let isValid = true;

        if (fullNameField.value.trim() === '') {
            await Swal.fire({
                icon: 'error',
                title: 'Validation Error',
                text: 'Full Name is required.',
            });
            isValid = false;
        }

        if (!validateEmail(emailField.value)) {
            await Swal.fire({
                icon: 'error',
                title: 'Validation Error',
                text: 'Please enter a valid email address.',
            });
            isValid = false;
        }

        if (phoneField.value.trim() !== '') {
            const phoneRegex = /^[0-9]+$/;
            if (!phoneRegex.test(phoneField.value)) {
                await Swal.fire({
                    icon: 'error',
                    title: 'Validation Error',
                    text: 'Phone number must contain only digits.',
                });
                isValid = false;
            }
        }

        if (descriptionField.value.trim() === '') {
            await Swal.fire({
                icon: 'error',
                title: 'Validation Error',
                text: 'Please describe your issue in detail.',
            });
            isValid = false;
        }

        return isValid;
    }

    // Update file preview
    function updatePreview(files) {
        previewContainer.innerHTML = '';

        files.forEach((file, index) => {
            const reader = new FileReader();

            reader.onload = function (e) {
                const wrapper = document.createElement('div');
                wrapper.className = 'preview-wrapper';

                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = `File Preview ${index + 1}`;

                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn';
                removeBtn.innerText = 'X';

                removeBtn.addEventListener('click', function () {
                    fileList.splice(index, 1);
                    updatePreview(fileList);
                });

                wrapper.appendChild(img);
                wrapper.appendChild(removeBtn);
                previewContainer.appendChild(wrapper);
            };

            reader.readAsDataURL(file);
        });
    }

    // File input change event
    fileInput.addEventListener('change', function () {
        const newFiles = Array.from(fileInput.files);

        if (fileList.length + newFiles.length > 3) {
            Swal.fire({
                icon: 'error',
                title: 'File Limit Exceeded',
                text: 'You can only upload up to 3 files.',
            });
            fileInput.value = '';
            return;
        }

        fileList = [...fileList, ...newFiles];
        updatePreview(fileList);

        fileInput.value = '';
    });

    // Form submit event
    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const isValid = await validateForm();

        if (isValid) {
            Swal.fire({
                title: 'Submitting...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            const formData = new FormData(form);

            fileList.forEach((file) => {
                formData.append('attachments[]', file);
            });

            // Debug: Log all form data
            for (let pair of formData.entries()) {
                console.log(pair[0], pair[1]);
            }

            try {
                const response = await fetch('/tech_support/', {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    const result = await response.json();
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: result.success || 'Your tech support request has been submitted!',
                    });
                    form.reset();
                    fileList = [];
                    updatePreview(fileList);
                } else {
                    const error = await response.json();
                    Swal.fire({
                        icon: 'error',
                        title: 'Server Error',
                        text: error.error || 'An error occurred while submitting your request.',
                    });
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Network Error',
                    text: 'Unable to submit your request. Please try again later.',
                });
                console.error('Fetch Error:', error);
            }
        }
    });

    // Back button functionality
    const backButton = document.getElementById('adminLoginButton');
    backButton.addEventListener('click', function () {
        window.location.href = '/admin_login/';
    });
});
