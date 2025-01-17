document.addEventListener("DOMContentLoaded", () => {
    const modulesTableBody = document.getElementById("modules-table-body");
    const moduleForm = document.getElementById("add-edit-module-form");
    const moduleNameInput = document.getElementById("module-name");
    const moduleIdInput = document.getElementById("module-id");

    // Fetch and render modules
    const fetchModules = async () => {
        try {
            const response = await fetch("/modules/");
            if (!response.ok) throw new Error("Failed to fetch modules.");
            const modules = await response.json();

            modulesTableBody.innerHTML = "";
            modules.forEach((module, index) => {
                const row = `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${module.module_name}</td>
                        <td>
                            <button class="btn btn-warning btn-sm" onclick="editModule(${module.id}, '${module.module_name}')">Edit</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteModule(${module.id})">Delete</button>
                        </td>
                    </tr>
                `;
                modulesTableBody.innerHTML += row;
            });
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Unable to fetch modules. Please try again later.",
            });
        }
    };

    // Add or update module
    moduleForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const moduleId = moduleIdInput.value;
        const moduleName = moduleNameInput.value;

        if (!moduleName.trim()) {
            Swal.fire({
                icon: "warning",
                title: "Warning",
                text: "Module name cannot be empty.",
            });
            return;
        }

        const url = moduleId ? `/modules/${moduleId}/` : "/modules/";
        const method = moduleId ? "PUT" : "POST";

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ module_name: moduleName }),
            });

            if (response.ok) {
                Swal.fire({
                    icon: "success",
                    title: "Success",
                    text: moduleId ? "Module updated successfully." : "Module added successfully.",
                });
                fetchModules();
                moduleForm.reset();
            } else {
                const errorData = await response.json();
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: errorData.message || "An error occurred while saving the module.",
                });
            }
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "An error occurred while saving the module. Please try again.",
            });
        }
    });

    // Edit module
    window.editModule = (id, name) => {
        moduleIdInput.value = id;
        moduleNameInput.value = name;
        Swal.fire({
            icon: "info",
            title: "Edit Mode",
            text: `You are editing the module: ${name}`,
        });
    };

    // Delete module
    window.deleteModule = async (id) => {
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
                const response = await fetch(`/modules/${id}/`, {
                    method: "DELETE",
                });

                if (response.ok) {
                    Swal.fire({
                        icon: "success",
                        title: "Deleted",
                        text: "Module has been deleted successfully.",
                    });
                    fetchModules();
                } else {
                    throw new Error("Failed to delete module.");
                }
            } catch (error) {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "An error occurred while deleting the module. Please try again.",
                });
            }
        }
    };

    // Initial fetch
    fetchModules();
});
