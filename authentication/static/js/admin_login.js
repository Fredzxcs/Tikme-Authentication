document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');

    // Function to get the CSRF token from the cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
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

            const employeeNumber = document.getElementById('employee_number').value.trim();
            const password = document.getElementById('password').value.trim();

            // Validate inputs before making a request
            if (!employeeNumber || !password) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Missing Information',
                    text: 'Please fill in both Employee Number and Password fields.',
                });
                return;
            }

            // Display loading animation
            Swal.fire({
                title: 'Logging in...',
                text: 'Please wait while we process your request.',
                allowOutsideClick: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

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
                        Swal.fire({
                            icon: 'success',
                            title: 'Login Successful',
                            text: 'Redirecting to your dashboard...',
                            timer: 2000,
                            showConfirmButton: false,
                        }).then(() => {
                            // Redirect to the dashboard
                            window.location.href = data.redirect_to;
                        });
                    } else {
                        throw new Error('Invalid response from server.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);

                    // Handle specific error cases
                    let errorMessage = 'An unexpected error occurred.';
                    if (error.message.includes('Invalid credentials')) {
                        errorMessage = 'Incorrect Employee Number or Password.';
                    } else if (error.message.includes('Session expired')) {
                        errorMessage = 'Your session has expired. Please log in again.';
                    }

                    Swal.fire({
                        icon: 'error',
                        title: 'Login Failed',
                        text: errorMessage,
                    });
                });
        });
    }

    // Function to toggle password visibility
    window.togglePassword = function () {
        const passwordInput = document.getElementById('password');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    };
});
