document.addEventListener("DOMContentLoaded", function() {
    fetch('/profile/', {
        method: 'GET',
        headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('User profile not found');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // ✅ Ensure all fields are correctly populated
            const setText = (id, value, defaultValue = "Not provided") => {
                const element = document.getElementById(id);
                if (element) element.textContent = value || defaultValue;
            };

            setText("fullName", data.user.full_name);
            setText("email", data.user.email);
            setText("phone", data.user.phone_number);
            setText("userNumber", data.user.user_number);
            setText("module", data.user.module);
            setText("role", data.user.role);
            setText("status", data.user.status);
            setText("jobTitle", data.user.job_title);

            // ✅ Ensure profile picture displays correctly
            const profilePicturePreview = document.querySelector(".img-thumbnail");
            if (profilePicturePreview) {
                profilePicturePreview.src = data.user.profile_picture;
                profilePicturePreview.onerror = function() {
                    this.src = "/static/img/default-profile.jpg"; // Fallback image
                };
            }
        } else {
            console.error("Failed to load user data:", data.message);
        }
    })
    .catch(error => console.error("Error fetching user data:", error));

    // ✅ Handle cancel button click
    const cancelButton = document.querySelector(".btn-secondary");
    if (cancelButton) {
        cancelButton.addEventListener("click", function() {
            if (confirm("Are you sure you want to cancel the changes?")) {
                window.location.href = "/profile"; // Redirect to profile page
            }
        });
    }
});
