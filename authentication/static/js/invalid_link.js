// Function to get the JWT token from local storage 
function getToken() {
    return localStorage.getItem('jwtToken'); // Assuming the JWT is stored in local storage
}

// Function to validate the JWT token
function isTokenValid(token) {
    if (!token) return false;

    // Decode the payload from the token
    const payload = JSON.parse(atob(token.split('.')[1])); // Base64 decode the payload

    const currentTime = Math.floor(Date.now() / 1000); // Get current time in seconds

    // Check if the token is expired
    return payload.exp > currentTime; // Return true if token is not expired
}

// Function to handle page load
function onPageLoad() {
    const token = getToken();

    // Check if the token is present and valid
    if (token && isTokenValid(token)) {
        alert("Your session is still valid.");
        // Optionally redirect to another page or perform other actions
    } else {
        alert("Your session has expired or you are not logged in. Please log in again.");
        window.location.href = '/admin_login/'; // Redirect to the login page
    }
}

// Call onPageLoad when the document is ready
document.addEventListener('DOMContentLoaded', onPageLoad);
