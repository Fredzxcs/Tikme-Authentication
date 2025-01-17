document.addEventListener("DOMContentLoaded", () => {
    const rolesTableBody = document.getElementById("roles-table-body");
    const roleForm = document.getElementById("add-edit-role-form");
    const roleNameInput = document.getElementById("role-name");
    const roleIdInput = document.getElementById("role-id");

    // Fetch and render roles
    const fetchRoles = async () => {
        try {
            const response = await fetch("/roles/");
            if (!response.ok) throw new Error("Failed to fetch roles.");
            const roles = await response.json();

            rolesTableBody.innerHTML = "";
            roles.forEach((role, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${role.role_name}</td>
                        <td>
                            <button class="btn btn-warning btn-sm" onclick="editRole(${role.id}, '${role.role_name}')">Edit</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteRole(${role.id})">Delete</button>
                        </td>
                    </tr>
                `;
                rolesTableBody.innerHTML += row;
            });
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Unable to fetch roles. Please try again later.",
            });
        }
    };

    // Add or update role
    roleForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const roleId = roleIdInput.value;
        const roleName = roleNameInput.value;

        if (!roleName.trim()) {
            Swal.fire({
                icon: "warning",
                title: "Warning",
                text: "Role name cannot be empty.",
            });
            return;
        }

        const url = roleId ? `/roles/${roleId}/` : "/roles/";
        const method = roleId ? "PUT" : "POST";

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ role_name: roleName }),
            });

            if (response.ok) {
                Swal.fire({
                    icon: "success",
                    title: "Success",
                    text: roleId ? "Role updated successfully." : "Role added successfully.",
                });
                fetchRoles();
                roleForm.reset();
            } else {
                throw new Error("Failed to save role.");
            }
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "An error occurred while saving the role. Please try again.",
            });
        }
    });

    // Edit role
    window.editRole = (id, name) => {
        roleIdInput.value = id;
        roleNameInput.value = name;
        Swal.fire({
            icon: "info",
            title: "Edit Mode",
            text: `You are editing the role: ${name}`,
        });
    };

    // Delete role
    window.deleteRole = async (id) => {
        const confirmDelete = await Swal.fire({
            title: "Are you sure?",
            text: "This action cannot be undone.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#e53e3e",
            cancelButtonColor: "#4a5568",
            confirmButtonText: "Yes, delete it!",
        });

        if (confirmDelete.isConfirmed) {
            try {
                const response = await fetch(`/roles/${id}/`, {
                    method: "DELETE",
                });

                if (response.ok) {
                    Swal.fire({
                        icon: "success",
                        title: "Deleted",
                        text: "Role has been deleted successfully.",
                    });
                    fetchRoles();
                } else {
                    throw new Error("Failed to delete role.");
                }
            } catch (error) {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "An error occurred while deleting the role. Please try again.",
                });
            }
        }
    };

    // Initial fetch
    fetchRoles();
});
