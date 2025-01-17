document.addEventListener("DOMContentLoaded", () => {
    const permissionsTableBody = document.getElementById("permissions-table-body");
    const rolesPermissionsTableBody = document.getElementById("roles-permissions-table-body");
    const addPermissionForm = document.getElementById("add-permission-form");
    const permissionNameInput = document.getElementById("permission-name");
    const assignPermissionForm = document.getElementById("assign-permission-form");
    const rolesDropdown = document.getElementById("roles");
    const permissionsDropdown = document.getElementById("permissions");

    // SweetAlert helper
    const showAlert = (icon, title, text) => {
        Swal.fire({
            icon,
            title,
            text,
        });
    };

    // Fetch and render permissions
    const fetchPermissions = async () => {
        try {
            const response = await fetch("/permissions/");
            if (!response.ok) throw new Error("Failed to fetch permissions");
            const permissions = await response.json();

            permissionsTableBody.innerHTML = ""; // Clear table body
            permissions.forEach((permission, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${permission.name}</td>
                        <td>
                            <button class="btn btn-danger btn-sm delete-permission" data-id="${permission.id}">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
                permissionsTableBody.innerHTML += row;
            });
            attachDeleteHandlers();
            populatePermissionsDropdown(permissions);
        } catch (error) {
            console.error(error);
            showAlert("error", "Error", "Failed to fetch permissions.");
        }
    };

    // Populate permissions dropdown
    const populatePermissionsDropdown = (permissions) => {
        permissionsDropdown.innerHTML = permissions
            .map((permission) => `<option value="${permission.id}">${permission.name}</option>`)
            .join("");
    };

    // Fetch and render roles
    const fetchRoles = async () => {
        try {
            const response = await fetch("/roles/");
            if (!response.ok) throw new Error("Failed to fetch roles");
            const roles = await response.json();

            rolesDropdown.innerHTML = roles
                .map((role) => `<option value="${role.id}">${role.role_name}</option>`)
                .join("");
            fetchRolesWithPermissions();
        } catch (error) {
            console.error(error);
            showAlert("error", "Error", "Failed to fetch roles.");
        }
    };

    // Fetch roles and their permissions
    const fetchRolesWithPermissions = async () => {
        try {
            const response = await fetch("/roles-with-permissions/");
            if (!response.ok) throw new Error("Failed to fetch roles and permissions");
            const rolesPermissions = await response.json();

            rolesPermissionsTableBody.innerHTML = ""; // Clear table body
            rolesPermissions.forEach((role) => {
                const row = `
                    <tr>
                        <td>${role.role_name}</td>
                        <td>${role.permissions.join(", ")}</td>
                    </tr>
                `;
                rolesPermissionsTableBody.innerHTML += row;
            });
        } catch (error) {
            console.error(error);
            showAlert("error", "Error", "Failed to fetch roles and their permissions.");
        }
    };

    // Add new permission
    addPermissionForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const permissionName = permissionNameInput.value.trim();

        if (!permissionName) {
            showAlert("warning", "Warning", "Permission name cannot be empty.");
            return;
        }

        try {
            const response = await fetch("/permissions/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name: permissionName }),
            });

            if (response.ok) {
                fetchPermissions();
                permissionNameInput.value = "";
                showAlert("success", "Success", "Permission added successfully!");
            } else {
                const errorData = await response.json();
                console.error(errorData);
                showAlert("error", "Error", errorData.error || "Failed to add permission.");
            }
        } catch (error) {
            console.error(error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    });

    // Assign permission to a role
    assignPermissionForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const roleId = rolesDropdown.value;
        const permissionId = permissionsDropdown.value;

        try {
            const response = await fetch(`/roles/${roleId}/assign-permission/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ permission_id: permissionId }),
            });

            if (response.ok) {
                fetchRolesWithPermissions();
                showAlert("success", "Success", "Permission assigned to role successfully!");
            } else {
                const errorData = await response.json();
                console.error(errorData);
                showAlert("error", "Error", errorData.error || "Failed to assign permission.");
            }
        } catch (error) {
            console.error(error);
            showAlert("error", "Error", "An unexpected error occurred.");
        }
    });

    // Attach delete handlers
    const attachDeleteHandlers = () => {
        document.querySelectorAll(".delete-permission").forEach((button) => {
            button.addEventListener("click", async (e) => {
                const permissionId = e.target.getAttribute("data-id");

                Swal.fire({
                    title: "Are you sure?",
                    text: "This action cannot be undone!",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#dc3545",
                    cancelButtonColor: "#6c757d",
                    confirmButtonText: "Yes, delete it!",
                }).then(async (result) => {
                    if (result.isConfirmed) {
                        try {
                            const response = await fetch(`/permissions/${permissionId}/`, {
                                method: "DELETE",
                            });

                            if (response.ok) {
                                fetchPermissions();
                                showAlert("success", "Deleted!", "Permission deleted successfully!");
                            } else {
                                const errorData = await response.json();
                                console.error(errorData);
                                showAlert("error", "Error", errorData.error || "Failed to delete permission.");
                            }
                        } catch (error) {
                            console.error(error);
                            showAlert("error", "Error", "An unexpected error occurred.");
                        }
                    }
                });
            });
        });
    };

    // Initialize
    fetchPermissions();
    fetchRoles();
});
