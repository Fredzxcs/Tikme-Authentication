document.addEventListener("DOMContentLoaded", () => {
    const addEditJobTitleForm = document.getElementById("add-edit-job-title-form");
    const jobTitleTableBody = document.getElementById("job-title-table-body");
    const jobTitleNameInput = document.getElementById("job-title-name");
    const jobTitleIdInput = document.getElementById("job-title-id");
    const jobTitlePermissionsInput = document.getElementById("job-title-permissions"); // ✅ Ensure this exists

    // ✅ Function to Get CSRF Token from Cookies
    function getCSRFToken() {
        let csrfToken = null;
        document.cookie.split(";").forEach(cookie => {
            const [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") {
                csrfToken = value;
            }
        });
        return csrfToken;
    }

    // ✅ Show Alerts with SweetAlert
    const showAlert = (icon, title, text) => {
        Swal.fire({
            icon,
            title,
            text,
        });
    };

    // ✅ Fetch Job Titles from Backend
    async function fetchJobTitles() {
        try {
            const response = await fetch("/job-titles/");
            if (!response.ok) throw new Error("Failed to fetch job titles.");
            const jobTitles = await response.json();

            jobTitleTableBody.innerHTML = "";
            jobTitles.forEach(jobTitle => {
                const row = `
                    <tr>
                        <td>${jobTitle.id}</td>
                        <td>${jobTitle.title_name}</td>
                        <td>
                            <button class="btn btn-warning btn-sm edit-job-title-btn" data-id="${jobTitle.id}">Edit</button>
                            <button class="btn btn-danger btn-sm delete-job-title-btn" data-id="${jobTitle.id}">Delete</button>
                        </td>
                    </tr>
                `;
                jobTitleTableBody.innerHTML += row;
            });

            attachEventListeners();
        } catch (error) {
            console.error("Error fetching job titles:", error);
            showAlert("error", "Error", "Failed to fetch job titles.");
        }
    }

    // ✅ Handle Adding/Updating a Job Title (Fixed permissions field)
    async function handleAddEditJobTitle(event) {
        event.preventDefault();

        const jobTitleName = jobTitleNameInput.value.trim();
        const jobTitleId = jobTitleIdInput.value;
        const permissions = jobTitlePermissionsInput ? Array.from(jobTitlePermissionsInput.selectedOptions).map(option => option.value) : []; // ✅ Extract selected permissions

        if (!jobTitleName) {
            showAlert("warning", "Validation Error", "Job title name cannot be empty.");
            return;
        }

        const url = jobTitleId ? `/job-titles/${jobTitleId}/` : "/job-titles/";
        const method = jobTitleId ? "PUT" : "POST";
        const csrfToken = getCSRFToken();

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ 
                    title_name: jobTitleName,
                    permissions: permissions // ✅ Include permissions field
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Response Error:", errorData);
                showAlert("error", "Error", errorData.permissions ? errorData.permissions.join(", ") : "Failed to save job title.");
                return;
            }

            showAlert("success", "Success", jobTitleId ? "Job title updated successfully!" : "Job title added successfully!");
            fetchJobTitles();
            addEditJobTitleForm.reset();
            jobTitleIdInput.value = "";
        } catch (error) {
            console.error("Error saving job title:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    }

    // ✅ Handle Editing a Job Title
    async function handleEditJobTitle(jobTitleId) {
        try {
            const response = await fetch(`/job-titles/${jobTitleId}/`);
            if (!response.ok) throw new Error("Failed to fetch job title for editing.");
            const jobTitle = await response.json();

            jobTitleNameInput.value = jobTitle.title_name;
            jobTitleIdInput.value = jobTitle.id; // Set the hidden input for ID tracking

            // ✅ Populate permissions
            if (jobTitlePermissionsInput) {
                const selectedPermissions = new Set(jobTitle.permissions.map(p => p.id));
                for (let option of jobTitlePermissionsInput.options) {
                    option.selected = selectedPermissions.has(option.value);
                }
            }
        } catch (error) {
            console.error("Error fetching job title:", error);
            showAlert("error", "Error", "Failed to fetch job title details.");
        }
    }

    // ✅ Handle Deleting a Job Title
    async function handleDeleteJobTitle(jobTitleId) {
        const confirmation = await Swal.fire({
            title: "Are you sure?",
            text: "This action cannot be undone.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "No, cancel",
        });

        if (confirmation.isConfirmed) {
            try {
                const response = await fetch(`/job-titles/${jobTitleId}/`, {
                    method: "DELETE",
                    headers: { "X-CSRFToken": getCSRFToken() },
                });

                if (response.ok) {
                    showAlert("success", "Success", "Job title deleted successfully!");
                    fetchJobTitles();
                } else {
                    showAlert("error", "Error", "Failed to delete job title.");
                }
            } catch (error) {
                console.error("Error deleting job title:", error);
                showAlert("error", "Error", "An unexpected error occurred.");
            }
        }
    }

    // ✅ Attach Event Listeners
    function attachEventListeners() {
        document.querySelectorAll(".edit-job-title-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                const jobTitleId = event.target.dataset.id;
                handleEditJobTitle(jobTitleId);
            });
        });

        document.querySelectorAll(".delete-job-title-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                const jobTitleId = event.target.dataset.id;
                handleDeleteJobTitle(jobTitleId);
            });
        });
    }

    // ✅ Initialize
    addEditJobTitleForm.onsubmit = handleAddEditJobTitle;
    fetchJobTitles();
});
