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

    const strengthIndicator = document.getElementById('password-strength-indicator');
    const requirementElements = {
        length: document.getElementById('length'),
        uppercase: document.getElementById('uppercase'),
        lowercase: document.getElementById('lowercase'),
        digit: document.getElementById('digit'),
    };

    // Update requirements list
    Object.entries(requirements).forEach(([key, isValid]) => {
        requirementElements[key].className = isValid ? 'valid' : 'invalid';
    });

    // Update password strength indicator
    const strength = Object.values(requirements).filter(Boolean).length;
    let strengthText = 'Weak';
    let strengthColor = 'red';

    if (strength === 4) {
        strengthText = 'Strong';
        strengthColor = 'green';
    } else if (strength === 3) {
        strengthText = 'Medium';
        strengthColor = 'orange';
    }

    strengthIndicator.textContent = `Password strength: ${strengthText}`;
    strengthIndicator.style.color = strengthColor;
}

// Show error messages using SweetAlert
function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message,
    });
}

// Show success messages using SweetAlert
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

// Handle form submission
async function submitPassword(event) {
    event.preventDefault();

    const form = document.getElementById('password-setup-form');

    // Safely retrieve form elements
    const passwordField = form.querySelector('input[name="new_password1"]');
    const confirmPasswordField = form.querySelector('input[name="new_password2"]');
    const tokenField = form.querySelector('input[name="token"]');
    const uidb64Field = form.querySelector('input[name="uidb64"]');

    if (!passwordField || !confirmPasswordField || !tokenField || !uidb64Field) {
        console.error('Form fields missing.');
        showError('A required field is missing. Please contact support.');
        return;
    }

    const password = passwordField.value;
    const confirmPassword = confirmPasswordField.value;
    const token = tokenField.value;
    const uidb64 = uidb64Field.value;

    // Retrieve security answers from localStorage
    const securityAnswers = localStorage.getItem('securityAnswers');
    if (!securityAnswers) {
        showError('Security answers are missing. Please restart the setup process.');
        return;
    }

    if (!validatePasswords(password, confirmPassword)) return;

    try {
        Swal.fire({
            title: 'Submitting...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/setup-password/${uidb64}/${token}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({
                new_password1: password,
                new_password2: confirmPassword,
                security_answers: JSON.parse(securityAnswers),
            }),
        });

        if (response.ok) {
            showSuccess('Password set successfully!', '/admin_login/');
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Failed to set password.');
        }
    } catch (error) {
        console.error('Error occurred while setting password:', error);
        showError('An error occurred while setting your password. Please try again.');
    }
}

// Add real-time password strength indicator
document.getElementById('new-password1')?.addEventListener('input', function (e) {
    updatePasswordStrengthIndicator(e.target.value);
});

// Add event listener for form submission
document.getElementById('password-setup-form')?.addEventListener('submit', submitPassword);

console.log({
    new_password1: password,
    new_password2: confirmPassword,
    security_answers: JSON.parse(securityAnswers),
});
