document.addEventListener("DOMContentLoaded", () => {
    const addUserForm = document.getElementById("addUserForm");
    const userTableBody = document.getElementById("userTableBody");
    const roleSelect = document.getElementById("role");
    const moduleSelect = document.getElementById("module");
    const jobTitleSelect = document.getElementById("jobTitle");
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    

    const csrfToken = csrfTokenElement.value;

    const showAlert = (icon, title, text) => {
        Swal.fire({
            icon,
            title,
            text,
        });
    };

    // Fetch roles and exclude "Super Admin" if it already exists
    async function fetchRoles() {
        try {
            const response = await fetch("/roles/");
            if (!response.ok) throw new Error("Failed to fetch roles.");
            const roles = await response.json();

            // Check if "Super Admin" already exists in the user table
            const hasSuperAdmin = Array.from(userTableBody.querySelectorAll("td"))
                .some(td => td.textContent.trim() === "Super Admin");

            roleSelect.innerHTML = `<option value="">Select Role</option>`;
            roles.forEach(role => {
                if (role.role_name !== "Super Admin" || !hasSuperAdmin) {
                    roleSelect.innerHTML += `<option value="${role.role_name}">${role.role_name}</option>`;
                }
            });
        } catch (error) {
            console.error("Error fetching roles:", error);
            showAlert("error", "Error", "Failed to fetch roles.");
        }
    }

    // Generic function to fetch data for dropdowns
    async function fetchData(url, selectElement, placeholder, nameField) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Failed to fetch data from ${url}`);
            const data = await response.json();
            selectElement.innerHTML = `<option value="">${placeholder}</option>` +
                data.map(item => `<option value="${item[nameField]}">${item[nameField]}</option>`).join("");
        } catch (error) {
            console.error(`Error fetching data from ${url}:`, error);
            showAlert("error", "Error", `Failed to fetch ${placeholder.toLowerCase()}.`);
        }
    }
    
    // Fetch users and populate the user table
    async function fetchUsers() {
        try {
            const response = await fetch("/manage-users/");
            if (!response.ok) throw new Error("Failed to fetch users.");
            const data = await response.json();

            userTableBody.innerHTML = data.employees.map(user => {
                const isSuperAdmin = user.role === "Super Admin";
                const isPending = user.status === "Pending";
                const isInactive = user.status === "Inactive";
                const isSuspended = user.status === "Suspended";

                return `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.employee_number}</td>
                    <td>${user.first_name}</td>
                    <td>${user.last_name}</td>
                    <td>${user.email}</td>
                    <td>${user.module || "N/A"}</td> 
                    <td>${user.role}</td>
                    <td>${user.job_title || "N/A"}</td> 
                    <td>${user.status}</td>
                    <td>
                        <div class="dropdown">
                            <button class="btn btn-secondary dropdown-toggle btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                Actions
                            </button>
                            <ul class="dropdown-menu">
                                <li><button class="dropdown-item edit-user-btn" data-id="${user.id}">Edit</button></li>
                                <li><button class="dropdown-item delete-user-btn" data-id="${user.id}">Delete</button></li>
                            </ul>
                        </div>
                    </td>
                    <td>
                        <div class="dropdown">
                            <button class="btn btn-primary dropdown-toggle btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                Email Actions
                            </button>
                            <ul class="dropdown-menu">
                                <li>
                                    <button class="dropdown-item email-onboarding-btn ${isSuperAdmin || !isPending ? "disabled" : ""}" 
                                        data-id="${user.id}" data-email-type="onboarding">
                                        Onboarding Email
                                    </button>
                                </li>
                                <li>
                                    <button class="dropdown-item email-locked-btn ${isSuperAdmin || !isInactive ? "disabled" : ""}" 
                                        data-id="${user.id}" data-email-type="locked">
                                        Locked Email
                                    </button>
                                </li>
                                <li>
                                    <button class="dropdown-item email-reactivation-btn ${isSuperAdmin || !isSuspended ? "disabled" : ""}" 
                                        data-id="${user.id}" data-email-type="reactivation">
                                        Reactivation Email
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </td>
                </tr>
                `;
            }).join("");

            attachEventListeners();
        } catch (error) {
            console.error("Error fetching users:", error);
            showAlert("error", "Error", "Failed to fetch users.");
        }
    }

    // Show or hide the "Module" dropdown based on role selection
    function toggleModuleDropdown(selectedRole) {
        const moduleGroup = moduleSelect.closest(".mb-3");
        if (selectedRole === "System Admin") {
            moduleGroup.style.display = "none";
            moduleSelect.value = "";
        } else if (selectedRole === "Manager") {
            moduleGroup.style.display = "block";
        } else {
            moduleGroup.style.display = "none";
            moduleSelect.value = "";
        }
    }

    // Attach event listener for role changes
    roleSelect.addEventListener("change", (event) => {
        const selectedRole = event.target.value;
        toggleModuleDropdown(selectedRole);
    });

    // Handle adding or editing a user
    async function handleAddEditUser(event) {
        event.preventDefault();
        const formData = new FormData(addUserForm);
        const payload = Object.fromEntries(formData.entries());

        if (payload.role === "Manager" && !payload.module) {
            showAlert("error", "Validation Error", "Module is required for the Manager role.");
            return;
        }

        console.log("Payload being sent:", JSON.stringify(payload)); // Debugging

        try {
            const response = await fetch("/add-employee/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
            });

            const responseData = await response.json();
            if (response.ok) {
                showAlert("success", "Success", "User added successfully!");
                fetchUsers();
                addUserForm.reset();
                const modal = bootstrap.Modal.getInstance(document.getElementById("addUserModal"));
                modal.hide();
            } else {
                // Handle backend validation errors, including module issues
                const errorMessage = typeof responseData.error === "object"
                    ? Object.entries(responseData.error).map(([key, value]) => `${key}: ${value}`).join("\n")
                    : responseData.error;
                showAlert("error", "Error", errorMessage || "Failed to save user.");
            }
        } catch (error) {
            console.error("Error:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    }
    
    // Handle persistent backdrop removal
    document.addEventListener("hidden.bs.modal", function () {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
    });

    // Handle editing a user
    async function handleEditUser(userId) {
        try {
            const response = await fetch(`/manage-users/${userId}/edit/`);
            if (!response.ok) throw new Error("Failed to fetch user for editing.");
            const user = await response.json();

            addUserForm.dataset.userId = user.id; // Store the user ID for updating
            addUserForm.employee_number.value = user.employee_number;
            addUserForm.first_name.value = user.first_name;
            addUserForm.last_name.value = user.last_name;
            addUserForm.email.value = user.email;
            roleSelect.value = user.role;
            moduleSelect.value = user.module || "";
            jobTitleSelect.value = user.job_title || "";

            toggleModuleDropdown(user.role);

            const modal = new bootstrap.Modal(document.getElementById("addUserModal"));
            modal.show();
        } catch (error) {
            console.error("Error fetching user for editing:", error);
            showAlert("error", "Error", "Failed to fetch user details.");
        }
    }

    // Handle deleting a user
    async function handleDeleteUser(userId) {
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
                const response = await fetch(`/manage-users/${userId}/delete/`, {
                    method: "DELETE",
                    headers: { "X-CSRFToken": csrfToken },
                });

                if (response.ok) {
                    showAlert("success", "Success", "User deleted successfully!");
                    fetchUsers();
                } else {
                    showAlert("error", "Error", "Failed to delete user.");
                }
            } catch (error) {
                console.error("Error deleting user:", error);
                showAlert("error", "Error", "An unexpected error occurred.");
            }
        }
    }


    // Send email action
    async function handleEmailAction(userId, emailType) {
        try {
            const response = await fetch(`/email-actions/${userId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ email_type: emailType }),
            });

            const responseData = await response.json();
            if (response.ok) {
                showAlert("success", "Success", responseData.message);
                fetchUsers(); // Refresh the table
            } else {
                showAlert("error", "Error", responseData.error || "Failed to send email.");
            }
        } catch (error) {
            console.error("Error sending email action:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    }

    // Attach event listeners to dynamic buttons
    function attachEventListeners() {
        document.querySelectorAll(".edit-user-btn").forEach(button => {
            button.addEventListener("click", () => handleEditUser(button.dataset.id));
        });

        document.querySelectorAll(".delete-user-btn").forEach(button => {
            button.addEventListener("click", () => handleDeleteUser(button.dataset.id));
        });

        document.querySelectorAll(".email-onboarding-btn").forEach(button => {
            button.addEventListener("click", () => {
                if (!button.classList.contains("disabled")) {
                    handleEmailAction(button.dataset.id, "onboarding");
                }
            });
        });

        document.querySelectorAll(".email-locked-btn").forEach(button => {
            button.addEventListener("click", () => {
                if (!button.classList.contains("disabled")) {
                    handleEmailAction(button.dataset.id, "locked");
                }
            });
        });

        document.querySelectorAll(".email-reactivation-btn").forEach(button => {
            button.addEventListener("click", () => {
                if (!button.classList.contains("disabled")) {
                    handleEmailAction(button.dataset.id, "reactivation");
                }
            });
        });
    }

    // Initialize the page
    addUserForm.onsubmit = handleAddEditUser;
    fetchRoles();
    fetchData("/modules/", moduleSelect, "Select Module", "module_name");
    fetchData("/job-titles/", jobTitleSelect, "Select Job Title", "title_name");
    fetchUsers();
});
