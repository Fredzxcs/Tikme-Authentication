document.addEventListener("DOMContentLoaded", () => {
    const addUserForm = document.getElementById("addUserForm");
    const userTableBody = document.getElementById("userTableBody");
    const employeeNumberInput = document.getElementById("employeeNumber");
    const roleSelect = document.getElementById("role");
    const moduleSelect = document.getElementById("module");
    const jobTitleSelect = document.getElementById("jobTitle");
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    
    const firstNameInput = document.getElementById("firstName");
    const lastNameInput = document.getElementById("lastName");
    const emailInput = document.getElementById("email");

    const firstNameError = document.getElementById("firstNameError");
    const lastNameError = document.getElementById("lastNameError");
    const emailError = document.getElementById("emailError");

    const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
    const closeModalButton = document.getElementById("closeModalButton");


    if (closeModalButton) {
        closeModalButton.addEventListener("click", () => {
            modal.hide(); // Bootstrap's method to hide the modal
        });
    } else {
        console.warn("Close Modal Button not found!");
    }
    
    // Ensuring backdrop removal when modal is hidden
    document.getElementById('addUserModal').addEventListener('hidden.bs.modal', () => {
        const backdrop = document.querySelector(".modal-backdrop");
        if (backdrop) {
            backdrop.remove(); // Clean up the backdrop manually
        }
    });

    document.querySelectorAll(".scrollable-dropdown select").forEach(select => {
        select.addEventListener("click", (event) => {
            let container = event.target.closest(".scrollable-dropdown").querySelector(".scrollable-dropdown-container");
            if (container) {
                container.style.display = "block"; // Show dropdown
            }
        });

        select.addEventListener("blur", (event) => {
            let container = event.target.closest(".scrollable-dropdown").querySelector(".scrollable-dropdown-container");
            if (container) {
                setTimeout(() => {
                    container.style.display = "none"; // Hide dropdown
                }, 200);
            }
        });
    });

    const csrfToken = csrfTokenElement.value;

    const showAlert = (icon, title, text) => {
        Swal.fire({
            icon,
            title,
            text,
        });
    };

    async function fetchUsers() {
        try {
            const response = await fetch("/manage-users/");
            if (!response.ok) throw new Error("Failed to fetch users.");
            const data = await response.json();
    
            userTableBody.innerHTML = data.employees.map(user => {
                const isSuperAdmin = user.role === "Super Admin";
    
                return `
                <tr>
                    <td>${user.employee_number}</td>
                    <td>${user.first_name}</td>
                    <td>${user.last_name}</td>
                    <td>${user.module || "N/A"}</td>
                    <td>${user.role}</td>
                    <td>${user.status}</td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-warning edit-user-btn" data-id="${user.id}" ${isSuperAdmin ? "disabled" : ""}>
                            <i class="fa fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-danger delete-user-btn" data-id="${user.id}" ${isSuperAdmin ? "disabled" : ""}>
                            <i class="fa fa-trash"></i> Delete
                        </button>
                    </td>
                </tr>`;
            }).join("");
    
            attachEventListeners();
        } catch (error) {
            console.error("Error fetching users:", error);
            showAlert("error", "Error", "Failed to fetch users.");
        }
    }
    
    async function fetchRoles(isEditing = false, currentRole = "") {
        try {
            const response = await fetch("/roles/");
            if (!response.ok) throw new Error("Failed to fetch roles.");
    
            const roles = await response.json();
            roleSelect.innerHTML = `<option value="">Select Role</option>`;
    
            roles.forEach(role => {
                if (isEditing || role.role_name !== "Super Admin") {
                    roleSelect.innerHTML += `<option value="${role.role_name}">${role.role_name}</option>`;
                }
            });
    
        } catch (error) {
            console.error("Error fetching roles:", error);
            Swal.fire("Error", "Failed to load roles.", "error");
        }
    }
    
    
    
    function disableRoleIfSuperAdmin() {
        if (roleSelect.value === "Super Admin") {
            roleSelect.setAttribute("disabled", "true");
        } else {
            roleSelect.removeAttribute("disabled");
        }
    }
    
    async function fetchUserDetails(userId) {
        try {
            const response = await fetch(`/manage-users/${userId}/edit/`);
            if (!response.ok) throw new Error("Failed to fetch user details.");
            const user = await response.json();
    
            document.getElementById("employeeNumber").value = user.employee_number;
            document.getElementById("firstName").value = user.first_name;
            document.getElementById("lastName").value = user.last_name;
            document.getElementById("email").value = user.email;
            document.getElementById("jobTitle").value = user.job_title || "";
    
            // ✅ Fetch roles with editing mode enabled
            await fetchRoles(true, user.role);
    
            // ✅ Set the selected role
            roleSelect.value = user.role;
            document.getElementById("hiddenRole").value = user.role; // Store it in the hidden field
    
            if (user.role === "Super Admin") {
                roleSelect.style.pointerEvents = "none"; // Disable selection
                roleSelect.style.background = "#e9ecef";
            } else {
                roleSelect.style.pointerEvents = "auto";
                roleSelect.style.background = "#fff";
            }
    
            moduleSelect.value = user.module || "";
    
        } catch (error) {
            console.error("Error fetching user details:", error);
        }
    }
    
    
    
    function syncHiddenRole() {
        document.getElementById("hiddenRole").value = roleSelect.value;
    }
    
    addUserForm.addEventListener("submit", syncHiddenRole);
    
    
    // Fetch user details when editing
    if (roleSelect) {
        const userId = roleSelect.dataset.userId;
        if (userId) {
            fetchUserDetails(userId);
        }
    }

    roleSelect.addEventListener("change", disableRoleIfSuperAdmin);
    // Call function when the form is loaded
    disableRoleIfSuperAdmin();

    // If the role changes, check again (only needed for edit mode)
    roleSelect.addEventListener("change", disableRoleIfSuperAdmin);

    function validateInput(input, errorElement, pattern, errorMessage) {
        if (!pattern.test(input.value)) {
            errorElement.textContent = errorMessage;
            input.classList.add("is-invalid");
            return false;
        } else {
            errorElement.textContent = "";
            input.classList.remove("is-invalid");
            return true;
        }
    }

    firstNameInput.addEventListener("input", () => {
        validateInput(firstNameInput, firstNameError, /^[A-Za-z\s]+$/, "Only letters allowed (Min: 2 characters)");
    });

    lastNameInput.addEventListener("input", () => {
        validateInput(lastNameInput, lastNameError, /^[A-Za-z\s]+$/, "Only letters allowed (Min: 2 characters)");
    });

    emailInput.addEventListener("input", () => {
        validateInput(emailInput, emailError, /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/, "Enter a valid email (example@mail.com)");
    });

    async function fetchDropdownData(url, selectElement, placeholder, nameField) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Failed to fetch ${placeholder}`);
            const data = await response.json();

            selectElement.innerHTML = `<option value="">${placeholder}</option>`;
            data.forEach(item => {
                selectElement.innerHTML += `<option value="${item[nameField]}">${item[nameField]}</option>`;
            });

            console.log(`${placeholder} dropdown updated successfully.`);
        } catch (error) {
            console.error(`Error fetching ${placeholder}:`, error);
            Swal.fire("Error", `Failed to load ${placeholder}.`, "error");
        }
    }


    // Auto-Generate Employee Number (On Submission)
    function generateEmployeeNumber() {
        const role = roleSelect.value;
        let rolePrefix = "USR"; // Default prefix
    
        if (role === "Manager") {
            rolePrefix = "MGR";
        } else if (role === "Employee") {
            rolePrefix = "EMP";
        } else if (role === "System Admin") {
            rolePrefix = "SYS"; // System Admin should not depend on module
        }
    
        const modulePrefix = role !== "System Admin" && moduleSelect.value ? moduleSelect.value.substring(0, 3).toUpperCase() : "";
        const randomNum = Math.floor(1000 + Math.random() * 9000);
        
        if (role === "System Admin") {
            return `${rolePrefix}-${randomNum}`; // System Admins should have a different format
        }
        return `${rolePrefix}-${modulePrefix}-${randomNum}`;
    }
    
    roleSelect.addEventListener("change", () => {
        employeeNumberInput.value = generateEmployeeNumber(); // ✅ Fix: Now properly references the input
    });
    
    moduleSelect.addEventListener("change", () => {
        employeeNumberInput.value = generateEmployeeNumber(); // ✅ Fix: Now properly references the input
    });
    
    function attachEventListeners() {
        document.querySelectorAll(".edit-user-btn").forEach(button => {
            button.addEventListener("click", () => handleEditUser(button.dataset.id));
        });
    }

    // Handle Adding a User
    addUserForm.onsubmit = async (event) => {
        event.preventDefault();
    
        const formData = new FormData(addUserForm);
        const payload = Object.fromEntries(formData.entries());
    
        // ✅ Ensure employee_number is included
        payload.employee_number = employeeNumberInput.value;
    
        if (!payload.employee_number) {
            showAlert("error", "Validation Error", "Employee Number is required.");
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
                showAlert("error", "Error", responseData.error || "Failed to save user.");
            }
        } catch (error) {
            console.error("Error:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    };
    
    // Fetch Dropdown Data and Make Scrollable
    async function fetchDropdownData(url, selectElement, placeholder, nameField) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Failed to fetch ${placeholder}`);
            const data = await response.json();

            selectElement.innerHTML = `<option value="">${placeholder}</option>`;
            data.forEach(item => {
                selectElement.innerHTML += `<option value="${item[nameField]}">${item[nameField]}</option>`;
            });

            console.log(`${placeholder} dropdown updated successfully.`);
        } catch (error) {
            console.error(`Error fetching ${placeholder}:`, error);
            Swal.fire("Error", `Failed to load ${placeholder}.`, "error");
        }
    }
    
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
                    <td>${user.employee_number}</td>
                    <td>${user.first_name}</td>
                    <td>${user.last_name}</td>
                    <td>${user.module || "N/A"}</td>
                    <td>${user.role}</td>
                    <td>${user.status}</td>
                    <td class="text-center d-flex justify-content-center gap-2">
                        <!-- Actions Dropdown (Edit & Delete) -->
                        <div class="dropdown">
                            <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="fa fa-cog"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li>
                                    <button class="dropdown-item edit-user-btn" data-id="${user.id}"}>
                                        <i class="fa fa-edit"></i> Edit
                                    </button>
                                </li>
                                <li>
                                    <button class="dropdown-item delete-user-btn" data-id="${user.id}" ${isSuperAdmin ? "disabled" : ""}>
                                        <i class="fa fa-trash"></i> Delete
                                    </button>
                                </li>
                            </ul>
                        </div>
    
                        <!-- Email Actions Dropdown -->
                        <div class="dropdown">
                            <button class="btn btn-sm btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="fa fa-envelope"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li>
                                    <button class="dropdown-item email-onboarding-btn" data-id="${user.id}" data-email-type="onboarding" ${!isPending ? "disabled" : ""}>
                                        <i class="fa fa-paper-plane"></i> Onboarding 
                                    </button>
                                </li>
                                <li>
                                    <button class="dropdown-item email-locked-btn" data-id="${user.id}" data-email-type="locked" ${!isInactive ? "disabled" : ""}>
                                        <i class="fa fa-lock"></i> Locked 
                                    </button>
                                </li>
                                <li>
                                    <button class="dropdown-item email-reactivation-btn" data-id="${user.id}" data-email-type="reactivation" ${!isSuspended ? "disabled" : ""}>
                                        <i class="fa fa-sync"></i> Reactivation 
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </td>
                </tr>`;
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
        } else if (selectedRole === "Manager" || selectedRole === "Employee") {
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
        
        const userId = addUserForm.dataset.userId; // Get stored user ID if editing
        
        const apiUrl = userId ? `/manage-users/${userId}/edit/` : "/add-employee/";
        const method = userId ? "PUT" : "POST"; // Use PUT for updates, POST for new users
        
        try {
            const response = await fetch(apiUrl, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
            });
    
            const responseData = await response.json();
    
            if (response.ok) {
                showAlert("success", "Success", userId ? "User updated successfully!" : "User added successfully!");
                fetchUsers(); // Refresh the table
                addUserForm.reset();
                delete addUserForm.dataset.userId; // Remove stored user ID after update
    
                const modal = bootstrap.Modal.getInstance(document.getElementById("addUserModal"));
                modal.hide();
            } else {
                showAlert("error", "Error", responseData.error || "Failed to save user.");
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
    
            addUserForm.dataset.userId = userId; // Store user ID for updates
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

        document.querySelectorAll(".dropdown-toggle").forEach(button => {
            button.addEventListener("click", (event) => {
                event.stopPropagation(); // Prevent closing immediately when clicking the button
                let dropdownMenu = button.nextElementSibling;

                // Close all other dropdowns
                document.querySelectorAll(".dropdown-menu").forEach(menu => {
                    if (menu !== dropdownMenu) {
                        menu.classList.remove("show");
                    }
                });

                // Toggle the current dropdown
                dropdownMenu.classList.toggle("show");
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", () => {
            document.querySelectorAll(".dropdown-menu").forEach(menu => {
                menu.classList.remove("show");
            });
        });

        // Prevent dropdown from closing when clicking inside
        document.querySelectorAll(".dropdown-menu").forEach(menu => {
            menu.addEventListener("click", (event) => {
                event.stopPropagation();
            });
        });
    }

    // Initialize the page
    addUserForm.onsubmit = handleAddEditUser;
    fetchRoles();
    fetchDropdownData("/modules/", document.getElementById("module"), "Select Module", "module_name");
    fetchDropdownData("/job-titles/", document.getElementById("jobTitle"), "Select Job Title", "title_name");
    fetchUsers();
    roleSelect.addEventListener("change", generateEmployeeNumber);
    moduleSelect.addEventListener("change", generateEmployeeNumber);
});
    