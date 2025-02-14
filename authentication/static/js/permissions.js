document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ DOM Fully Loaded.");

    // ✅ Select Elements
    const permissionsTableBody = document.getElementById("permissions-table-body");
    const jobTitlesPermissionsTableBody = document.getElementById("job-titles-permissions-table-body");
    const addPermissionForm = document.getElementById("add-permission-form");
    const permissionNameInput = document.getElementById("permission-name");
    const availablePermissions = document.getElementById("available-permissions");
    const chosenPermissions = document.getElementById("chosen-permissions");
    const moveRightBtn = document.getElementById("move-right");
    const moveLeftBtn = document.getElementById("move-left");
    const chooseAllBtn = document.getElementById("choose-all");
    const removeAllBtn = document.getElementById("remove-all");
    const jobTitleDropdown = document.getElementById("job-title-dropdown");
    const assignPermissionsBtn = document.getElementById("assign-permissions-btn");
    
    // ✅ Select Filter Inputs
    const filterAvailableInput = document.getElementById("filter-available");
    const filterChosenInput = document.getElementById("filter-chosen");

    // ✅ Ensure Filter Inputs Exist
    if (!filterAvailableInput || !filterChosenInput) {
        console.error("❌ Error: One or more filter inputs not found in the DOM.");
        return;
    }

    // ✅ CSRF Token Fetching
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

    // ✅ Show SweetAlert Notifications
    const showAlert = (icon, title, text) => {
        Swal.fire({ icon, title, text });
    };

    // ✅ Fetch and Populate Permissions Table
    const fetchPermissions = async () => {
        try {
            const response = await fetch("/permissions/");
            if (!response.ok) throw new Error("Failed to fetch permissions");
            const permissions = await response.json();

            permissionsTableBody.innerHTML = "";
            availablePermissions.innerHTML = ""; // Clear available permissions dropdown
            updatePermissionsUI(permissions);

            permissions.forEach((permission, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${permission.name}</td>
                        <td>
                            <button class="btn btn-danger btn-sm delete-permission" data-id="${permission.id}">
                                <i class="fa fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
                permissionsTableBody.innerHTML += row;

                // Populate Available Permissions Dropdown
                let option = document.createElement("option");
                option.value = permission.id;
                option.textContent = permission.name;
                availablePermissions.appendChild(option);
            });

            attachDeleteHandlers();
        } catch (error) {
            console.error("❌ Error fetching permissions:", error);
            showAlert("error", "Error", "Failed to fetch permissions.");
        }
    };

    // ✅ Fetch and Populate Job Titles
    const fetchJobTitles = async () => {
        try {
            const response = await fetch("/job-titles/");
            if (!response.ok) throw new Error("Failed to fetch job titles");
            const jobTitles = await response.json();

            jobTitlesPermissionsTableBody.innerHTML = "";

            jobTitles.forEach(jobTitle => {
                const row = `
                    <tr>
                        <td>${jobTitle.title_name}</td>
                        <td>
                            <button class="btn btn-info btn-sm view-job-title" data-id="${jobTitle.id}">
                                <i class="bi bi-eye"></i> <!-- View Icon -->
                            </button>
                        </td>
                    </tr>
                `;
                jobTitlesPermissionsTableBody.innerHTML += row;
            });

            attachViewHandlers(); // Attach View Handlers
        } catch (error) {
            showAlert("error", "Error", "Failed to fetch job titles.");
        }
    };


    const updatePermissionsUI = (permissions) => {
        permissionsTableBody.innerHTML = "";
        availablePermissions.innerHTML = ""; 

        permissions.forEach((permission, index) => {
            const row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${permission.name}</td>
                    <td>
                        <button class="btn btn-danger btn-sm delete-permission" data-id="${permission.id}">
                            <i class="fa fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            permissionsTableBody.innerHTML += row;

            let option = document.createElement("option");
            option.value = permission.id;
            option.textContent = permission.name;
            availablePermissions.appendChild(option);
        });

        attachDeleteHandlers();
    };

    // ✅ Attach Delete Handlers
    const attachDeleteHandlers = () => {
        document.querySelectorAll(".delete-permission").forEach(button => {
            button.addEventListener("click", async (event) => {
                const permissionId = event.target.dataset.id;

                Swal.fire({
                    title: "Are you sure?",
                    text: "This action cannot be undone!",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#dc3545",
                    cancelButtonColor: "#6c757d",
                    confirmButtonText: "Yes, delete it!"
                }).then(async (result) => {
                    if (result.isConfirmed) {
                        try {
                            const response = await fetch(`/permissions/${permissionId}/`, {
                                method: "DELETE",
                                headers: { "X-CSRFToken": getCSRFToken() },
                            });

                            if (response.ok) {
                                fetchPermissions();
                                showAlert("success", "Deleted!", "Permission deleted successfully!");
                            } else {
                                showAlert("error", "Error", "Failed to delete permission.");
                            }
                        } catch (error) {
                            showAlert("error", "Error", "An unexpected error occurred.");
                        }
                    }
                });
            });
        });
    };

    // ✅ Attach View Handlers
    const attachViewHandlers = () => {
        document.querySelectorAll(".view-job-title").forEach(button => {
            button.addEventListener("click", async (event) => {
                const jobTitleId = event.target.dataset.id;
                try {
                    const response = await fetch(`/api/job-titles/${jobTitleId}/permissions/`);
                    if (!response.ok) throw new Error("Failed to fetch assigned permissions.");

                    const permissions = await response.json();
                    const permissionsList = permissions.map(p => `• ${p.name}`).join("\n");

                    showAlert("info", "Assigned Permissions", permissionsList);
                } catch (error) {
                    console.error("❌ Error fetching assigned permissions:", error);
                    showAlert("error", "Error", "Failed to load assigned permissions.");
                }
            });
        });
    };

    // ✅ Fetch and Populate Job Titles Dropdown
    const fetchJobTitlesDropdown = async () => {
        try {
            const response = await fetch("/job-titles/");
            if (!response.ok) throw new Error("Failed to fetch job titles");
            const jobTitles = await response.json();

            jobTitleDropdown.innerHTML = `<option value="" disabled selected>-- Select Job Title --</option>`;

            jobTitles.forEach(jobTitle => {
                let option = document.createElement("option");
                option.value = jobTitle.id;
                option.textContent = jobTitle.title_name;
                jobTitleDropdown.appendChild(option);
            });
        } catch (error) {
            console.error("❌ Error fetching job titles for dropdown:", error);
            showAlert("error", "Error", "Failed to load job titles.");
        }
    };

    const assignPermissionsToJobTitle = async () => {
        const jobTitleId = jobTitleDropdown.value;
        if (!jobTitleId) {
            showAlert("warning", "Validation Error", "Please select a job title first.");
            return;
        }
    
        const selectedPermissions = [...chosenPermissions.options].map(option => option.value);
        if (selectedPermissions.length === 0) {
            showAlert("warning", "Validation Error", "Please select at least one permission.");
            return;
        }
    
        try {
            console.log("📡 Sending request to assign permissions:", JSON.stringify({ permission_ids: selectedPermissions }));
    
            const response = await fetch(`/job-titles/${jobTitleId}/assign-permission/`, { // ✅ Ensure correct URL
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ permission_ids: selectedPermissions }), // ✅ Sending array
            });
    
            const responseText = await response.text();  // Fix: Read response before parsing JSON
            try {
                const jsonData = JSON.parse(responseText);  // Fix: Parse JSON properly
                if (response.ok) {
                    showAlert("success", "Success", jsonData.message || "Permissions assigned successfully!");
                    fetchAssignedPermissions(jobTitleId);
                } else {
                    throw new Error(jsonData.error || "Failed to assign permissions.");
                }
            } catch (jsonError) {
                console.error("❌ Response is not valid JSON:", responseText);
                showAlert("error", "Error", "Received invalid JSON response from server.");
            }
            
        } catch (error) {
            console.error("❌ Error assigning permissions:", error);
            showAlert("error", "Error", error.message || "An unexpected error occurred.");
        }
    };
    
    assignPermissionsBtn.addEventListener("click", assignPermissionsToJobTitle);

    // ✅ Fetch Assigned Permissions
    const fetchAssignedPermissions = async (jobTitleId) => {
        if (!jobTitleId) return;
    
        try {
            const response = await fetch(`/api/job-titles/${jobTitleId}/permissions/`);
            if (!response.ok) throw new Error("Failed to fetch assigned permissions.");

            const assignedPermissions = await response.json();
            chosenPermissions.innerHTML = ""; 

            assignedPermissions.forEach(permission => {
                let option = document.createElement("option");
                option.value = permission.id;
                option.textContent = permission.name;
                chosenPermissions.appendChild(option);
            });

        } catch (error) {
            console.error("❌ Error fetching assigned permissions:", error);
            showAlert("error", "Error", "Failed to load assigned permissions.");
        }
    };
    
    // ✅ Filter Available Permissions
    filterAvailableInput.addEventListener("input", () => {
        let filterText = filterAvailableInput.value.toLowerCase();
        [...availablePermissions.options].forEach(option => {
            option.style.display = option.textContent.toLowerCase().includes(filterText) ? "" : "none";
        });
    });

    // ✅ Filter Chosen Permissions
    filterChosenInput.addEventListener("input", () => {
        let filterText = filterChosenInput.value.toLowerCase();
        [...chosenPermissions.options].forEach(option => {
            option.style.display = option.textContent.toLowerCase().includes(filterText) ? "" : "none";
        });
    });

    // ✅ Move Selected Permissions to Chosen List
    moveRightBtn.addEventListener("click", () => {
        [...availablePermissions.selectedOptions].forEach(option => {
            chosenPermissions.appendChild(option);
        });
    });

    // ✅ Move Selected Permissions Back to Available List
    moveLeftBtn.addEventListener("click", () => {
        [...chosenPermissions.selectedOptions].forEach(option => {
            availablePermissions.appendChild(option);
        });
    });

    // ✅ Choose All Permissions
    chooseAllBtn.addEventListener("click", () => {
        [...availablePermissions.options].forEach(option => {
            chosenPermissions.appendChild(option);
        });
    });

    // ✅ Remove All Chosen Permissions
    removeAllBtn.addEventListener("click", () => {
        [...chosenPermissions.options].forEach(option => {
            availablePermissions.appendChild(option);
        });
    });

    // ✅ Initialize Data Fetching
    fetchPermissions();
    fetchJobTitles();
    fetchJobTitlesDropdown();
});
