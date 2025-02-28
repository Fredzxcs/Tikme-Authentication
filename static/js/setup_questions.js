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


// Helper function to validate security answers **only on submit**
function validateSecurityAnswersOnSubmit() {
    const questions = Array.from(document.querySelectorAll('select[name^="security_question"]')).map(select => select.value);
    const answers = Array.from(document.querySelectorAll('input[name^="security_answer"]')).map(input => input.value.trim().toLowerCase());
    
    const uniqueQuestions = new Set(questions);

    if (questions.length !== uniqueQuestions.size) {
        return "Please choose different questions for each field.";
    }

    if (answers.some(answer => answer.trim() === '')) {
        return "Please answer all security questions.";
    }

    return null;  // No errors
}

// Automatically convert input to lowercase as the user types
function enforceLowercaseInput() {
    document.querySelectorAll('input[name^="security_answer"]').forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.toLowerCase(); // Convert input to lowercase in real-time
        });
    });
}

// Handle form submission
async function submitSecurityAnswers(event) {
    event.preventDefault(); // Prevent default form submission

    const form = document.getElementById('security-questions-form');
    const token = form.querySelector('input[name="token"]').value;
    const uidb64 = form.querySelector('input[name="uidb64"]').value;

    // 🔹 **Run validation only on form submission**
    const validationError = validateSecurityAnswersOnSubmit();
    if (validationError) {
        showError(validationError);
        return;
    }

    const questions = Array.from(form.querySelectorAll('select[name^="security_question"]')).map(field => field.value);
    const answers = Array.from(form.querySelectorAll('input[name^="security_answer"]')).map(input => input.value.trim().toLowerCase());

    const payload = {
        answers: questions.map((question, index) => ({
            question: question,
            answer: answers[index],
        })),
    };

    try {
        Swal.fire({
            title: 'Submitting...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        const response = await fetch(`/setup-account/${uidb64}/${token}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            const result = await response.json();

            // Save security answers in localStorage
            localStorage.setItem('securityAnswers', JSON.stringify(payload.answers));

            showSuccess(
                'Security questions saved successfully!',
                `/setup-password/${uidb64}/${token}/`
            );
        } else {
            const errorData = await response.json();
            if (errorData.errors) {
                showError(`Some errors occurred: ${JSON.stringify(errorData.errors)}`);
            } else {
                showError(errorData.error || 'Failed to submit security questions.');
            }
        }
    } catch (error) {
        console.error('Error occurred while submitting security answers:', error);
        showError('An error occurred while submitting your answers. Please try again.');
    }
}


// Add event listener to the form submission
document.getElementById('security-questions-form')?.addEventListener('submit', submitSecurityAnswers);

// Real-time input validation for answers
document.querySelectorAll('input[name^="security_answer"]').forEach(input => {
    input.addEventListener('input', () => {
        if (input.value.trim() !== '') {
            input.classList.remove('is-invalid');
        }
    });
});


// 🔹 Modify question selection validation
document.querySelectorAll('select[name^="security_question"]').forEach(select => {
    select.addEventListener('change', () => {
        const selectedQuestions = Array.from(
            document.querySelectorAll('select[name^="security_question"]')
        ).map(select => select.value);

        const uniqueQuestions = new Set(selectedQuestions);

        // 🔹 Run validation **only if all fields are selected**
        if (selectedQuestions.length === uniqueQuestions.size && !selectedQuestions.includes("")) {
            Swal.close(); // Close any open error messages
        }
    });
});


// Enforce lowercase input
enforceLowercaseInput();
