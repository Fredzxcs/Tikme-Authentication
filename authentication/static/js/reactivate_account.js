// Function to get the JWT token from local storage
function getToken() {
    return localStorage.getItem('jwtToken'); // Assuming the JWT is stored in local storage
}

// Function to validate the JWT token
function isTokenValid(token) {
    if (!token) return false;

    const payload = JSON.parse(atob(token.split('.')[1])); // Decode the payload
    const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds

    // Check if the token is expired
    return payload.exp > currentTime;
}

// Function to handle page load
function onPageLoad() {
    const token = getToken();

    // Check if the token is present and valid
    if (!token || !isTokenValid(token)) {
        alert("Your session has expired or you are not logged in. Please log in again.");
        window.location.href = '/login'; // Redirect to the login page
    }
}

// Function to toggle password visibility
function toggleVisibility(inputId) {
    const inputField = document.getElementById(inputId);
    inputField.type = inputField.type === "password" ? "text" : "password"; // Toggle the password visibility
}

// Function to show the password section after answering security questions
function showPasswordSection() {
    const securityQuestionsSection = document.getElementById('security-questions');
    const passwordSection = document.getElementById('password-section');

    // Optionally, you can validate the security questions' answers here before proceeding
    // If all checks pass, show the password section
    securityQuestionsSection.style.display = 'none';
    passwordSection.style.display = 'block';
}

// Call onPageLoad when the document is ready
document.addEventListener('DOMContentLoaded', onPageLoad);
