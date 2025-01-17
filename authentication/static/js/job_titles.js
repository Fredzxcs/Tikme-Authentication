document.addEventListener("DOMContentLoaded", () => {
    const addEditJobTitleForm = document.getElementById("add-edit-job-title-form");
    const jobTitleTableBody = document.getElementById("job-title-table-body");
    const jobTitleNameInput = document.getElementById("job-title-name");
    const jobTitleIdInput = document.getElementById("job-title-id");

    const showAlert = (icon, title, text) => {
        Swal.fire({
            icon,
            title,
            text,
        });
    };

    // Fetch Job Titles from Backend
    async function fetchJobTitles() {
        try {
            const response = await fetch("/job-titles/");
            if (!response.ok) throw new Error("Failed to fetch job titles.");
            const jobTitles = await response.json();

            jobTitleTableBody.innerHTML = jobTitles
                .map(jobTitle => `
                    <tr>
                        <td>${jobTitle.id}</td>
                        <td>${jobTitle.title_name}</td>
                        <td>
                            <button class="btn btn-warning btn-sm edit-job-title-btn" data-id="${jobTitle.id}">Edit</button>
                            <button class="btn btn-danger btn-sm delete-job-title-btn" data-id="${jobTitle.id}">Delete</button>
                        </td>
                    </tr>
                `)
                .join("");

            attachEventListeners();
        } catch (error) {
            console.error("Error fetching job titles:", error);
            showAlert("error", "Error", "Failed to fetch job titles.");
        }
    }

    // Handle Adding/Updating a Job Title
    async function handleAddEditJobTitle(event) {
        event.preventDefault();
        const jobTitleName = jobTitleNameInput.value.trim();
        const jobTitleId = jobTitleIdInput.value; // Hidden input to track ID for editing

        if (!jobTitleName) {
            showAlert("warning", "Validation Error", "Job title name cannot be empty.");
            return;
        }

        const url = jobTitleId ? `/job-titles/${jobTitleId}/` : "/job-titles/";
        const method = jobTitleId ? "PUT" : "POST";

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title_name: jobTitleName }),
            });

            if (response.ok) {
                showAlert("success", "Success", jobTitleId ? "Job title updated successfully!" : "Job title added successfully!");
                fetchJobTitles();
                addEditJobTitleForm.reset();
                jobTitleIdInput.value = ""; // Clear the hidden input after operation
            } else {
                const errorData = await response.json();
                showAlert("error", "Error", errorData.error || "Failed to save job title.");
            }
        } catch (error) {
            console.error("Error saving job title:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    }

    // Handle Editing a Job Title
    async function handleEditJobTitle(jobTitleId) {
        try {
            const response = await fetch(`/job-titles/${jobTitleId}/`);
            if (!response.ok) throw new Error("Failed to fetch job title for editing.");
            const jobTitle = await response.json();

            jobTitleNameInput.value = jobTitle.title_name;
            jobTitleIdInput.value = jobTitle.id; // Set the hidden input for ID tracking
        } catch (error) {
            console.error("Error fetching job title:", error);
            showAlert("error", "Error", "Failed to fetch job title details.");
        }
    }

    // Handle Deleting a Job Title
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

    // Attach Event Listeners
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

    // Initialize
    addEditJobTitleForm.onsubmit = handleAddEditJobTitle;
    fetchJobTitles();
});
