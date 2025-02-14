document.addEventListener("DOMContentLoaded", function() {
    // Fetch user profile data from the backend and populate the profile fields
    fetch('/get_user_profile_data/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate profile details with user data
                document.getElementById("fullName").textContent = data.user.first_name + " " + data.user.last_name;
                document.getElementById("email").textContent = data.user.email;
                document.getElementById("phone").textContent = data.user.phone_number || "Not provided";
                document.getElementById("employeeNumber").textContent = data.user.employee_number || "Not assigned";
                document.getElementById("module").textContent = data.user.module || "Not assigned";
                document.getElementById("role").textContent = data.user.role || "Not assigned";
                document.getElementById("status").textContent = data.user.status || "Active";

                // Display current profile picture
                const profilePicturePreview = document.querySelector(".img-thumbnail");
                if (data.user.profile_picture_url) {
                    profilePicturePreview.src = data.user.profile_picture_url;
                } else {
                    profilePicturePreview.src = "/static/img/default-profile.jpg"; // Default image
                }
            }
        })
        .catch(error => console.error("Error fetching user data:", error));

    // Handle the cancel button click
    const cancelButton = document.querySelector(".btn-secondary");
    if (cancelButton) {
        cancelButton.addEventListener("click", function() {
            if (confirm("Are you sure you want to cancel the changes?")) {
                window.location.href = "/profile"; // Redirect to profile or other relevant page
            }
        });
    }
});
