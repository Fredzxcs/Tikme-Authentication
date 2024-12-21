document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // Send login request to the server
            fetch('/auth/admin_login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Login failed: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                // Store tokens and redirect
                sessionStorage.setItem('accessToken', data.access_token);
                sessionStorage.setItem('refreshToken', data.refresh_token);
                window.location.href = data.redirect_url;
            })
            .catch(error => {
                console.error('Error:', error);
                errorMessage.innerText = error.message;
            });
        });
    }

    // Function to refresh the access token
    function refreshAccessToken() {
        const refreshToken = sessionStorage.getItem('refreshToken');
        if (refreshToken) {
            fetch('/auth/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to refresh token');
                }
                return response.json();
            })
            .then(data => {
                sessionStorage.setItem('accessToken', data.access_token);
            })
            .catch(error => {
                console.error('Error refreshing token:', error);
                handleLogout();
            });
        }
    }

    // Function to handle API calls
    function handleAPICall(url, method = 'GET', body = null) {
        const token = sessionStorage.getItem('accessToken');
        if (!token) {
            handleLogout();
            return;
        }

        fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: body ? JSON.stringify(body) : null,
        })
        .then(response => {
            if (response.status === 401) {
                // If the token is expired, try to refresh it
                refreshAccessToken().then(() => {
                    // Retry the original API call
                    handleAPICall(url, method, body);
                });
            } else if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            // Handle successful data
            console.log(data);
        })
        .catch(error => {
            console.error('API call error:', error);
            handleLogout();
        });
    }

    // Logout function to clear tokens and redirect
    function handleLogout() {
        sessionStorage.removeItem('accessToken');
        sessionStorage.removeItem('refreshToken');
        window.location.href = '/auth/system_admin_login/'; // Redirect to login page
    }

    // Example of calling a protected resource on dashboard load
    const dashboardButton = document.getElementById('dashboard-button');
    if (dashboardButton) {
        dashboardButton.addEventListener('click', function () {
            handleAPICall('/auth/system_admin_dashboard/');
        });
    }

    // Password toggle visibility function
    window.togglePassword = function() {
        const passwordInput = document.getElementById('password');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
    }
});
