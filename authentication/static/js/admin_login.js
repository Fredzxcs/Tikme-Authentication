document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    // Function to get the CSRF token from the cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const employeeNumber = document.getElementById('employee_number').value;
            const password = document.getElementById('password').value;

            fetch('/admin_login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken, // Add the CSRF token to the header
                },
                body: JSON.stringify({
                    employee_number: employeeNumber,
                    password: password,
                }),
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.detail || 'Login failed. Please try again.');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.jwt && data.redirect_to) {
                        document.cookie = `jwt=${data.jwt}; httponly`;
                        window.location.href = data.redirect_to;
                    } else {
                        throw new Error('Invalid response from server.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    errorMessage.textContent = error.message || 'An unexpected error occurred.';
                    errorMessage.style.display = 'block';
                });
        });
    }

    window.togglePassword = function () {
        const passwordInput = document.getElementById('password');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    };
});
