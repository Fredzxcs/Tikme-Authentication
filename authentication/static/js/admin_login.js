document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const errorMessageDiv = document.getElementById('errorMessage');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default form submission

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            // Clear error messages and show loading indicator
            errorMessageDiv.style.display = 'none';
            errorMessageDiv.textContent = '';
            if (loadingIndicator) loadingIndicator.style.display = 'block'; // Show loading spinner

            // Send login request to the server
            fetch('/auth/admin_login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ username, password }),
            })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    } else {
                        throw new Error('Login failed');
                    }
                })
                .catch(error => {
                    // Hide loading spinner and display error
                    if (loadingIndicator) loadingIndicator.style.display = 'none';
                    errorMessageDiv.style.display = 'block';
                    errorMessageDiv.textContent = error.message;
                });
        });
    }

    // Function to get CSRF token for Django
    function getCSRFToken() {
        let csrfToken = null;
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
            }
        });
        return csrfToken;
    }
});
