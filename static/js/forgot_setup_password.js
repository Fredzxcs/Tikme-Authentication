// Helper function to show error messages with SweetAlert
function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message,
        confirmButtonText: 'OK',
    });
}

// Helper function to show success messages with SweetAlert
function showSuccess(message, redirectUrl) {
    Swal.fire({
        icon: 'success',
        title: 'Success',
        text: message,
        confirmButtonText: 'Next',
    }).then(() => {
        if (redirectUrl) {
            window.location.href = redirectUrl;
        }
    });
}

// Toggle visibility of password fields
function toggleVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    const eyeIcon = field.nextElementSibling.querySelector('i');

    if (field.type === 'password') {
        field.type = 'text';
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
    } else {
        field.type = 'password';
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
    }
}

// Update password strength and requirements
function updatePasswordStrengthIndicator(password) {
    const lengthCriteria = /.{8,}/;
    const uppercaseCriteria = /[A-Z]/;
    const lowercaseCriteria = /[a-z]/;
    const digitCriteria = /\d/;

    const requirements = {
        length: lengthCriteria.test(password),
        uppercase: uppercaseCriteria.test(password),
        lowercase: lowercaseCriteria.test(password),
        digit: digitCriteria.test(password),
    };

    const requirementElements = {
        length: document.getElementById('length'),
        uppercase: document.getElementById('uppercase'),
        lowercase: document.getElementById('lowercase'),
        digit: document.getElementById('digit'),
    };

    // Update each requirement's validity
    Object.entries(requirements).forEach(([key, isValid]) => {
        if (isValid) {
            requirementElements[key].classList.add('valid');
            requirementElements[key].classList.remove('invalid');
        } else {
            requirementElements[key].classList.add('invalid');
            requirementElements[key].classList.remove('valid');
        }
    });

    // Update strength indicator
    const strengthIndicator = document.getElementById('password-strength-indicator');
    const strength = Object.values(requirements).filter(Boolean).length;

    if (strength === 4) {
        strengthIndicator.textContent = 'Password strength: Strong';
        strengthIndicator.className = 'text-success';
    } else if (strength === 3) {
        strengthIndicator.textContent = 'Password strength: Medium';
        strengthIndicator.className = 'text-warning';
    } else {
        strengthIndicator.textContent = 'Password strength: Weak';
        strengthIndicator.className = 'text-danger';
    }
}

// Validate passwords
function validatePasswords(password, confirmPassword) {
    if (!password || !confirmPassword) {
        showError('Both password fields are required.');
        return false;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match.');
        return false;
    }

    const strengthIndicator = document.getElementById('password-strength-indicator');
    if (strengthIndicator.textContent.includes('Weak')) {
        showError('Your password is too weak. Please choose a stronger password.');
        return false;
    }

    return true;
}

// Function to validate the password via the server
async function validatePassword(password, uidb64, token) {
    try {
        const response = await fetch(`/validate-password/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ password, uidb64, token }),
        });

        if (response.ok) {
            const data = await response.json();
            return data.is_old_password;
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Validation failed.');
        }
    } catch (error) {
        console.error('Error validating password:', error);
        showError('An error occurred while validating the password.');
        return null;
    }
}

// Handle form submission
async function submitForgotSetupPassword(event) {
    event.preventDefault();

    const form = document.getElementById('forgot-setup-password-form');
    const passwordField = form.querySelector('input[name="new_password1"]');
    const confirmPasswordField = form.querySelector('input[name="new_password2"]');
    const tokenField = form.querySelector('input[name="token"]');
    const uidb64Field = form.querySelector('input[name="uidb64"]');

    if (!passwordField || !confirmPasswordField || !tokenField || !uidb64Field) {
        console.error('One or more fields are missing.');
        showError('A required field is missing. Please contact support.');
        return;
    }

    const password = passwordField.value;
    const confirmPassword = confirmPasswordField.value;
    const token = tokenField.value;
    const uidb64 = uidb64Field.value;

    if (!validatePasswords(password, confirmPassword)) return;

    try {
        // Validate password via the server
        const isOldPassword = await validatePassword(password, uidb64, token);
        if (isOldPassword) {
            showError('You cannot reuse a previously used password.');
            return;
        }

        Swal.fire({
            title: 'Submitting...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/reset-password/${uidb64}/${token}/change-password/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({
                new_password1: password,
                new_password2: confirmPassword,
            }),
        });

        if (response.ok) {
            showSuccess('Password reset successfully!', '/admin_login/');
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Failed to reset your password.');
        }
    } catch (error) {
        console.error('Error occurred while resetting password:', error);
        showError('An error occurred while resetting your password. Please try again.');
    }
}

// Add event listeners for password strength validation
document.getElementById('new-password').addEventListener('input', (e) => {
    updatePasswordStrengthIndicator(e.target.value);
});

// Add event listener for form submission
document
    .getElementById('forgot-setup-password-form')
    ?.addEventListener('submit', submitForgotSetupPassword);
 