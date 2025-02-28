document.addEventListener("DOMContentLoaded", () => {
    const addUserForm = document.getElementById("addUserForm");
    const searchInput = document.getElementById("searchInput");
    const userTableBody = document.getElementById("userTableBody");
    const userNumberInput = document.getElementById("userNumber");
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

    document.querySelectorAll(".dropdown-toggle").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent the dropdown from closing immediately when clicked
    
            let dropdownMenu = this.nextElementSibling; // Get the associated dropdown menu
            dropdownMenu.classList.toggle("show"); // Toggle visibility
    
            // Close other dropdowns when one is opened
            document.querySelectorAll(".dropdown-menu.show").forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.classList.remove("show");
                }
            });
        });
    });
    
    // Close the dropdown when clicking outside
    document.addEventListener("click", function () {
        document.querySelectorAll(".dropdown-menu.show").forEach(menu => {
            menu.classList.remove("show");
        });
    });
    
    // Prevent closing when clicking inside the dropdown
    document.querySelectorAll(".dropdown-menu").forEach(menu => {
        menu.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent dropdown from closing when clicking inside
        });
    });
    
    // Function to filter users based on search input
    function filterUsers() {
        const searchTerm = searchInput.value.toLowerCase();
        const rows = userTableBody.getElementsByTagName("tr");

        for (let row of rows) {
            const cells = row.getElementsByTagName("td");
            let found = false;

            for (let cell of cells) {
                if (cell.textContent.toLowerCase().includes(searchTerm)) {
                    found = true;
                    break;
                }
            }

            row.style.display = found ? "" : "none";
        }
    }

    
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
    
            document.getElementById("userNumber").value = user.user_number;
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

    // Auto-Generate User Number (On Submission)
    function generateUserNumber() {
        const role = roleSelect.value;
        let rolePrefix = "USR"; // Default prefix
    
        if (role === "Manager") {
            rolePrefix = "MGR";
        } else if (role === "User") {
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
        userNumberInput.value = generateUserNumber(); // ✅ Fix: Now properly references the input
    });
    
    moduleSelect.addEventListener("change", () => {
        userNumberInput.value = generateUserNumber(); // ✅ Fix: Now properly references the input
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
    
        // ✅ Ensure user_number is included
        payload.user_number = userNumberInput.value;
    
        if (!payload.user_number) {
            showAlert("error", "Validation Error", "User Number is required.");
            return;
        }
    
        console.log("Payload being sent:", JSON.stringify(payload)); // Debugging
    
        try {
            const response = await fetch("/add-user/", {
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
    
    // Floating Dropdown Fix
    document.querySelectorAll(".dropdown-toggle").forEach(button => {
        button.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent closing when clicking inside
            
            const dropdownMenu = this.nextElementSibling;
            const rect = this.getBoundingClientRect(); // Get button position
            
            // Set dropdown position relative to viewport
            dropdownMenu.style.position = "absolute";
            dropdownMenu.style.top = `${rect.bottom + window.scrollY}px`;
            dropdownMenu.style.left = `${rect.left + window.scrollX}px`;
            
            // Ensure dropdown stays within viewport
            const viewportWidth = window.innerWidth;
            const dropdownWidth = dropdownMenu.offsetWidth;
            if (rect.left + dropdownWidth > viewportWidth) {
                dropdownMenu.style.left = `${viewportWidth - dropdownWidth - 10}px`; // Shift left if overflow
            }

            dropdownMenu.classList.toggle("show");

            // Close other dropdowns
            document.querySelectorAll(".dropdown-menu.show").forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.classList.remove("show");
                }
            });
        });
    });

    // Hide dropdown when clicking outside
    document.addEventListener("click", function () {
        document.querySelectorAll(".dropdown-menu.show").forEach(menu => {
            menu.classList.remove("show");
        });
    });

    document.querySelectorAll(".dropdown-menu").forEach(menu => {
        menu.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent dropdown from closing when clicking inside
        });
    });

    // ✅ Fetch Users
    async function fetchUsers() {
        try {
            const response = await fetch("/manage-users/");
            if (!response.ok) throw new Error("Failed to fetch users.");
            const data = await response.json();

            userTableBody.innerHTML = data.users.map(user => {
                const isActive = user.status === "Active";
                const isSuperAdmin = user.role === "Super Admin";
                const isLocked = user.status === "Temporarily Locked" || user.status === "Permanently Locked";
                const isSuspended = user.status === "Suspended";

                return `
                <tr>
                    <td>${user.user_number}</td>
                    <td>${user.first_name}</td>
                    <td>${user.last_name}</td>
                    <td>${user.module || "N/A"}</td>
                    <td>${user.role}</td>
                    <td>${user.status}</td>
                    <td class="text-center d-flex justify-content-center gap-2">
                        <!-- Actions Dropdown -->
                        <div class="dropdown">
                            <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fa fa-cog"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><button class="dropdown-item edit-user-btn" data-id="${user.id}"><i class="fa fa-edit"></i> Edit</button></li>
                                <li><button class="dropdown-item delete-user-btn" data-id="${user.id}" ${isSuperAdmin ? "disabled" : ""}><i class="fa fa-trash"></i> Delete</button></li>
                                ${isLocked ? `<li><button class="dropdown-item unlock-user-btn" data-id="${user.id}"><i class="fa fa-unlock"></i> Unlock</button></li>` : ""}
                                ${!isSuperAdmin && !isSuspended ? `<li><button class="dropdown-item suspend-user-btn" data-id="${user.id}"><i class="fa fa-user-slash"></i> Suspend</button></li>` : ""}
                            </ul>
                        </div>

                        <!-- Email Actions -->
                        <div class="dropdown">
                            <button class="btn btn-sm btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fa fa-envelope"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><button class="dropdown-item email-onboarding-btn" data-id="${user.id}" data-email-type="onboarding"><i class="fa fa-paper-plane"></i> Onboarding</button></li>
                                ${isLocked ? `<li><button class="dropdown-item email-locked-btn" data-id="${user.id}" data-email-type="locked"><i class="fa fa-lock"></i> Locked</button></li>` : ""}
                                ${isSuspended ? `<li><button class="dropdown-item email-reactivation-btn" data-id="${user.id}" data-email-type="reactivation"><i class="fa fa-sync"></i> Reactivation</button></li>` : ""}
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

    // ✅ Handle Unlock User Action
    async function handleUnlockUser(userId) {
        try {
            const response = await fetch(`/manage-users/${userId}/unlock/`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
            });

            const data = await response.json();
            if (response.ok) {
                showAlert("success", "Success", "User unlocked successfully!");
                fetchUsers();
            } else {
                showAlert("error", "Error", data.error || "Failed to unlock user.");
            }
        } catch (error) {
            console.error("Error unlocking user:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    }

    // ✅ Handle Suspend User Action
    async function handleSuspendUser(userId) {
        const confirmation = await Swal.fire({
            title: "Suspend User?",
            text: "This action will suspend the user.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Yes, suspend",
        });

        if (confirmation.isConfirmed) {
            try {
                const response = await fetch(`/manage-users/${userId}/suspend/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
                });

                const data = await response.json();
                if (response.ok) {
                    showAlert("success", "User Suspended", "User has been suspended successfully.");
                    fetchUsers();
                } else {
                    showAlert("error", "Error", data.error || "Failed to suspend user.");
                }
            } catch (error) {
                console.error("Error suspending user:", error);
                showAlert("error", "Error", "An unexpected error occurred.");
            }
        }
    }

    // ✅ Handle Email Actions
    async function handleEmailAction(userId, emailType) {
        try {
            const response = await fetch(`/email-actions/${userId}/`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
                body: JSON.stringify({ email_type: emailType }),
            });

            const data = await response.json();
            if (response.ok) {
                showAlert("success", "Email Sent", data.message);
            } else {
                showAlert("error", "Error", data.error || "Failed to send email.");
            }
        } catch (error) {
            console.error("Error sending email action:", error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    }

    /** ✅ Validate Email & User Number to Prevent Duplicates */
    async function checkDuplicate(field, value) {
        try {
            const response = await fetch(`/validate-user/?${field}=${value}`);
            if (!response.ok) throw new Error("Failed to validate.");
            const data = await response.json();
            return data.exists; // Returns true if exists
        } catch (error) {
            console.error(`Error checking ${field}:`, error);
            return false;
        }
    }

    emailInput.addEventListener("input", async () => {
        if (await checkDuplicate("email", emailInput.value)) {
            emailError.textContent = "This email is already in use.";
            emailInput.classList.add("is-invalid");
        } else {
            emailError.textContent = "";
            emailInput.classList.remove("is-invalid");
        }
    });

    userNumberInput.addEventListener("input", async () => {
        if (await checkDuplicate("user_number", userNumberInput.value)) {
            Swal.fire("Error", "User number already exists.", "error");
        }
    });


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

    /** ✅ Fix Search Bar Overlapping Sidebar */
    function fixSearchBar() {
        const sidebar = document.querySelector(".sidebar");
        if (sidebar) {
            searchInput.style.marginLeft = sidebar.offsetWidth + "px";
        }
    }

    window.addEventListener("resize", fixSearchBar);
    fixSearchBar();

    // Handle adding or editing a user
    async function handleAddEditUser(event) {
        event.preventDefault();
        
        const formData = new FormData(addUserForm);
        const payload = Object.fromEntries(formData.entries());
        
        const userId = addUserForm.dataset.userId; // Get stored user ID if editing
        
        const apiUrl = userId ? `/manage-users/${userId}/edit/` : "/add-user/";
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
            addUserForm.user_number.value = user.user_number;
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

    // Attach event listeners to dynamic buttons
    function attachEventListeners() {
        document.querySelectorAll(".edit-user-btn").forEach(button => {
            button.addEventListener("click", () => handleEditUser(button.dataset.id));
        });

        document.querySelectorAll(".delete-user-btn").forEach(button => {
            button.addEventListener("click", () => handleDeleteUser(button.dataset.id));
        });

        document.querySelectorAll(".unlock-user-btn").forEach(button =>
            button.addEventListener("click", () => handleUnlockUser(button.dataset.id))
        );

        document.querySelectorAll(".suspend-user-btn").forEach(button =>
            button.addEventListener("click", () => handleSuspendUser(button.dataset.id))
        );

        document.querySelectorAll(".email-onboarding-btn, .email-locked-btn, .email-reactivation-btn").forEach(button =>
            button.addEventListener("click", () => handleEmailAction(button.dataset.id, button.dataset.emailType))
        );
        
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
    attachEventListeners();
    fetchUsers();
    roleSelect.addEventListener("change", generateUserNumber);
    moduleSelect.addEventListener("change", generateUserNumber);
    searchInput.addEventListener("keyup", filterUsers);
});
    