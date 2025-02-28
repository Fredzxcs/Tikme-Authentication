// Check the token status and show appropriate alert
document.addEventListener('DOMContentLoaded', function () {
    const tokenStatus = document.getElementById('token-status').value; // Pass token status via a hidden input field

    if (tokenStatus === 'used') {
        Swal.fire({
            title: 'Link Already Used',
            text: 'The link you used has already been completed or activated. If you believe this is an error, please contact your system administrator for assistance.',
            icon: 'warning',
            confirmButtonText: 'Back to Login'
        }).then(() => {
            window.location.href = '/admin_login/';
        });
    } else if (tokenStatus === 'invalid') {
        Swal.fire({
            title: 'Invalid Link',
            text: 'The link you used is invalid or expired. Please contact your system administrator for assistance.',
            icon: 'error',
            confirmButtonText: 'Back to Login'
        }).then(() => {
            window.location.href = '/admin_login/';
        });
    } else {
        Swal.fire({
            title: 'Unknown Error',
            text: 'An unknown error has occurred. Please try again later.',
            icon: 'error',
            confirmButtonText: 'Back to Login'
        }).then(() => {
            window.location.href = '/admin_login/';
        });
    }
});
