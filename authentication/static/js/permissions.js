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

    // ✅ Fix: Show Modal Properly Without Accessibility Issues
    const showModalSafely = () => {
        const modal = document.getElementById("permissionsModal");

        if (!modal) {
            console.error("❌ Error: Modal element not found.");
            return;
        }

        // ✅ Remove aria-hidden before showing
        modal.removeAttribute("aria-hidden");

        // ✅ Show modal using Bootstrap
        $("#permissionsModal").modal("show");

        // ✅ Wait for modal transition, then set focus
        setTimeout(() => {
            const closeButton = modal.querySelector(".btn-secondary");
            if (closeButton) {
                closeButton.focus(); // Set focus on close button (or any safe element inside modal)
            }
        }, 300); // Adjust timing based on animation speed
    };

    // ✅ Add Permission Form Submission Handling
    if (addPermissionForm) {
        addPermissionForm.addEventListener("submit", async (event) => {
            event.preventDefault(); // ✅ Prevent default form submission

            const permissionName = permissionNameInput.value.trim(); // ✅ Get input value

            if (!permissionName) {
                showAlert("warning", "Validation Error", "Permission name cannot be empty.");
                return;
            }

            try {
                console.log(`📡 Adding new permission: ${permissionName}`);

                const response = await fetch("/permissions/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ name: permissionName }), // ✅ Send the permission name
                });

                if (response.ok) {
                    showAlert("success", "Success", "Permission added successfully!");
                    permissionNameInput.value = ""; // ✅ Clear input field
                    fetchPermissions(); // ✅ Refresh the permissions table
                } else {
                    showAlert("error", "Error", "Failed to add permission.");
                }
            } catch (error) {
                console.error("❌ Error adding permission:", error);
                showAlert("error", "Error", "An unexpected error occurred.");
            }
        });
    } else {
        console.error("❌ Error: addPermissionForm not found in the DOM.");
    }

    const fetchPermissions = async () => {
        try {
            console.log("📡 Fetching permissions...");
    
            const response = await fetch("/permissions/");
            const text = await response.text(); // Read response text
            console.log("📡 Raw Permissions Response:", text);
    
            if (!response.ok) throw new Error(`Failed to fetch permissions: ${text}`);
    
            const permissions = JSON.parse(text);
    
            // ✅ Clear previous content
            permissionsTableBody.innerHTML = "";
            availablePermissions.innerHTML = "";
    
            permissions.forEach((permission, index) => {
                // ✅ Populate the permissions table
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
                permissionsTableBody.insertAdjacentHTML("beforeend", row);
    
                // ✅ Populate the available permissions dropdown
                let option = document.createElement("option");
                option.value = permission.id;
                option.textContent = permission.name;
                availablePermissions.appendChild(option);
            });
    
            attachDeleteHandlers(); // ✅ Ensure delete handlers are re-attached
            console.log("✅ Permissions populated successfully!");
    
        } catch (error) {
            console.error("❌ Error fetching permissions:", error);
            showAlert("error", "Error", "Failed to load permissions.");
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

    // ✅ Function to Display Assigned Permissions in Modal
    const displayAssignedPermissions = (permissions, jobTitleId) => {
        const permissionsList = document.getElementById("permissionsList");
        permissionsList.innerHTML = ""; // Clear previous content

        if (!permissions || permissions.length === 0) {
            Swal.fire({
                icon: "info",
                title: "No Permissions Assigned",
                text: "This job title has no assigned permissions yet.",
                confirmButtonColor: "#6f42c1",
            });
            return;
        }

        permissions.forEach(permission => {
            const listItem = document.createElement("li");
            listItem.classList.add("d-flex", "justify-content-between", "align-items-center");

            listItem.innerHTML = `
                <span><i class="fa fa-check-circle text-success"></i> ${permission.name}</span>
                <button class="btn btn-danger btn-sm remove-permission" data-permission-id="${permission.id}" data-job-title-id="${jobTitleId}">
                    <i class="fa fa-trash"></i>
                </button>
            `;

            permissionsList.appendChild(listItem);
        });

        attachRemovePermissionHandlers(); // ✅ Attach event handlers to remove permissions
        showModalSafely(); // ✅ Use the safe modal function
    };

    
    // ✅ Attach View Handlers (AFTER defining displayAssignedPermissions)
    const attachViewHandlers = () => {
        document.querySelectorAll(".view-job-title").forEach(button => {
            button.addEventListener("click", async (event) => {
                const jobTitleId = event.target.dataset.id;

                try {
                    const response = await fetch(`/api/job-titles/${jobTitleId}/permissions/`);

                    if (response.status === 404) {
                        Swal.fire({
                            icon: "info",
                            title: "No Permissions Assigned",
                            text: "This job title has no assigned permissions yet.",
                            confirmButtonColor: "#6f42c1",
                        });
                        return;
                    }

                    if (!response.ok) throw new Error("Failed to fetch assigned permissions.");

                    const permissions = await response.json();
                    displayAssignedPermissions(permissions, jobTitleId);
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
            console.log("📡 Fetching job titles..."); // Debugging log
    
            const response = await fetch("/job-titles/");
            const text = await response.text(); // Read response
    
            console.log("📡 Raw Response:", text); // Debugging: log full response
    
            if (!response.ok) throw new Error(`Failed to fetch job titles: ${text}`);
    
            const jobTitles = JSON.parse(text);
    
            jobTitleDropdown.innerHTML = ""; // ✅ Clear old options
            jobTitleDropdown.innerHTML += `<option value="" disabled selected>-- Select Job Title --</option>`;
    
            jobTitles.forEach(jobTitle => {
                let option = document.createElement("option");
                option.value = jobTitle.id;
                option.textContent = jobTitle.title_name;
                jobTitleDropdown.appendChild(option);
            });
    
            console.log("✅ Job titles populated successfully!");
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

    const fetchAssignedPermissions = async (jobTitleId) => {
        if (!jobTitleId || jobTitleId.trim() === "") {
            showAlert("warning", "Invalid Job Title", "Please select a valid job title.");
            return;
        }
        
        try {
            const response = await fetch(`/api/job-titles/${jobTitleId}/permissions/`);
    
            if (response.status === 404) {
                // ✅ Handle case where no permissions are assigned
                Swal.fire({
                    icon: "info",
                    title: "No Permissions Assigned",
                    text: "This job title has no assigned permissions yet.",
                    confirmButtonColor: "#6f42c1",
                });
                return;
            }
    
            if (!response.ok) {
                throw new Error("Failed to fetch assigned permissions.");
            }
    
            const assignedPermissions = await response.json();
            const permissionsList = document.getElementById("permissionsList");
            permissionsList.innerHTML = ""; // Clear previous content
    
            if (assignedPermissions.length === 0) {
                Swal.fire({
                    icon: "info",
                    title: "No Permissions Assigned",
                    text: "This job title has no assigned permissions yet.",
                    confirmButtonColor: "#6f42c1",
                });
                return;
            }
    
            assignedPermissions.forEach(permission => {
                const listItem = document.createElement("li");
                listItem.classList.add("permission-item", "d-flex", "justify-content-between", "align-items-center");
    
                listItem.innerHTML = `
                    <span><i class="fa fa-check-circle text-success"></i> ${permission.name}</span>
                    <button class="btn btn-danger btn-sm remove-permission" data-permission-id="${permission.id}" data-job-title-id="${jobTitleId}">
                        <i class="fa fa-trash"></i>
                    </button>
                `;
                permissionsList.appendChild(listItem);
            });
    
            attachRemovePermissionHandlers();
            $("#permissionsModal").modal("show"); // Show modal
    
        } catch (error) {
            console.error("❌ Error fetching assigned permissions:", error);
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Failed to load assigned permissions.",
                confirmButtonColor: "#6f42c1",
            });
        }
    };
    
    // ✅ Attach Click Event for Removing Assigned Permissions
    const attachRemovePermissionHandlers = () => {
        document.querySelectorAll(".remove-permission").forEach(button => {
            button.addEventListener("click", async (event) => {
                const button = event.target.closest("button");
                if (!button) return;
                
                const permissionId = button.dataset.permissionId;
                const jobTitleId = button.dataset.jobTitleId;
    
                if (!jobTitleId || !permissionId) {
                    showAlert("error", "Error", "Invalid Job Title or Permission ID.");
                    return;
                }
    
                Swal.fire({
                    title: "Are you sure?",
                    text: "This will remove the permission from the job title.",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#dc3545",
                    cancelButtonColor: "#6c757d",
                    confirmButtonText: "Yes, remove it!"
                }).then(async (result) => {
                    if (result.isConfirmed) {
                        try {
                            console.log(`📡 Removing Permission ID: ${permissionId} from Job Title ID: ${jobTitleId}`);
                            const response = await fetch(`/job-titles/${jobTitleId}/remove-permission/${permissionId}/`, {
                                method: "DELETE",
                                headers: { "X-CSRFToken": getCSRFToken() },
                            });
    
                            if (response.ok) {
                                showAlert("success", "Removed!", "Permission removed successfully.");
                                fetchAssignedPermissions(jobTitleId); // Refresh list
                            } else {
                                showAlert("error", "Error", "Failed to remove permission.");
                            }
                        } catch (error) {
                            console.error("❌ Error removing permission:", error);
                            showAlert("error", "Error", "An unexpected error occurred.");
                        }
                    }
                });
            });
        });
    };

    document.getElementById("remove-all-permissions").addEventListener("click", async () => {
        const jobTitleId = document.querySelector(".remove-permission")?.dataset.jobTitleId;
    
        if (!jobTitleId) {
            showAlert("warning", "Invalid Job Title", "No job title found.");
            return;
        }
    
        Swal.fire({
            title: "Are you sure?",
            text: "This will remove ALL permissions from this job title.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Yes, remove all!"
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    console.log(`📡 Removing all permissions from Job Title ID: ${jobTitleId}`);
                    const response = await fetch(`/job-titles/${jobTitleId}/remove-all-permissions/`, {
                        method: "DELETE",
                        headers: { "X-CSRFToken": getCSRFToken() },
                    });
    
                    if (response.ok) {
                        Swal.fire({
                            icon: "success",
                            title: "Removed!",
                            text: "All permissions removed successfully.",
                            confirmButtonColor: "#6f42c1",
                        }).then(() => {
                            location.reload(); // ✅ Reload page after removing all permissions
                        });
                    } else {
                        showAlert("error", "Error", "Failed to remove all permissions.");
                    }
                } catch (error) {
                    console.error("❌ Error removing all permissions:", error);
                    showAlert("error", "Error", "An unexpected error occurred.");
                }
            }
        });
    });
    

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
