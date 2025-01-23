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

// Helper function to show temporary lock alert
function showTemporaryLock(message) {
    Swal.fire({
        icon: 'warning',
        title: 'Account Locked',
        text: message,
        confirmButtonText: 'OK',
    }).then(() => {
        window.location.reload();
    });
}

// Automatically convert input to lowercase
function enforceLowercaseInput() {
    document.querySelectorAll('input[type="text"]').forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.toLowerCase();
        });
    });
}

// Fetch and populate security questions
async function fetchSecurityQuestions(uidb64, token) {
    try {
        Swal.fire({
            title: 'Loading security questions...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/forgot-setup-questions/${uidb64}/${token}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        Swal.close();

        if (response.ok) {
            const data = await response.json();

            document.getElementById('security-question-1').innerText = data.question_1;
            document.getElementById('security-question-2').innerText = data.question_2;
            document.getElementById('security-question-3').innerText = data.question_3;

            document.querySelector('input[name="question_id_1"]').value = data.question_1_id;
            document.querySelector('input[name="question_id_2"]').value = data.question_2_id;
            document.querySelector('input[name="question_id_3"]').value = data.question_3_id;
        } else {
            const errorData = await response.json();
            showError(errorData.error || 'Failed to load security questions.');
        }
    } catch (error) {
        console.error('Error fetching security questions:', error);
        showError('An error occurred while loading security questions.');
    }
}

// Handle form submission
async function submitForgotSecurityAnswers(event) {
    event.preventDefault();

    const form = document.getElementById('forgot-security-questions-form');
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

    if (answers.some(item => item.answer === '' || !item.question_id)) {
        showError('Please answer all security questions.');
        return;
    }

    try {
        Swal.fire({
            title: 'Submitting...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/forgot-setup-questions/${uidb64}/${token}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ answers }),
        });

        if (response.ok) {
            const result = await response.json();
            showSuccess('Answers verified! Redirecting to password reset.', result.redirect);
        } else {
            const errorData = await response.json();
            if (errorData.error.includes('locked')) {
                showTemporaryLock(errorData.error);
            } else {
                showError(errorData.error || 'Failed to validate answers.');
            }
        }
    } catch (error) {
        console.error('Error occurred:', error);
        showError('An error occurred while submitting answers.');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('forgot-security-questions-form');
    const token = form.querySelector('input[name="token"]').value;
    const uidb64 = form.querySelector('input[name="uidb64"]').value;

    fetchSecurityQuestions(uidb64, token);
    enforceLowercaseInput();
    form.addEventListener('submit', submitForgotSecurityAnswers);
});
