// Show modal function
function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

// Redirect to login after success
function redirectToLogin() {
    window.location.href = "{% url 'admin_login' %}";
}

// Check password strength
function checkPasswordStrength(password) {
    const lengthCriteria = /.{8,}/;
    const digitCriteria = /\d/;
    const lowercaseCriteria = /[a-z]/;
    const uppercaseCriteria = /[A-Z]/;

    if (password.match(lengthCriteria) && password.match(digitCriteria) && password.match(lowercaseCriteria) && password.match(uppercaseCriteria)) {
        return 'Strong';
    } else if (password.length >= 6) {
        return 'Medium';
    } else {
        return 'Weak';
    }
}

// Validate password
function validatePassword(password, confirmPassword) {
    if (password !== confirmPassword) {
        return 'Passwords do not match.';
    }

    const strength = checkPasswordStrength(password);
    if (strength === 'Weak') {
        return 'Your password is too weak. Please choose a stronger password.';
    }

    return null;
}

// Handle form submission
document.getElementById('password-setup-form')?.addEventListener('submit', async function (event) {
    event.preventDefault();

    const form = event.target;
    const password = form.querySelector('input[name="new_password1"]').value;
    const confirmPassword = form.querySelector('input[name="new_password2"]').value;

    const validationError = validatePassword(password, confirmPassword);
    if (validationError) {
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = validationError;
        errorMessage.classList.remove('d-none');
        return;
    }

    showModal('loadingModal');

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new FormData(form),
        });

        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        loadingModal.hide();

        if (response.ok) {
            showModal('successModal');
        } else {
            showModal('errorModal');
        }
    } catch (error) {
        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        loadingModal.hide();
        showModal('errorModal');
    }
});

// Update password strength indicator on input
document.querySelector('input[name="new_password1"]')?.addEventListener('input', function () {
    const password = this.value;
    const strengthIndicator = document.getElementById('password-strength-indicator');

    const strength = checkPasswordStrength(password);
    strengthIndicator.textContent = `Password strength: ${strength}`;
    strengthIndicator.className = '';
    strengthIndicator.classList.add(strength.toLowerCase());
});
