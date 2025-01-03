document.addEventListener("DOMContentLoaded", function () {
    const addEmployeeBtn = document.getElementById("add-employee-btn");
    const addEmployeeModal = document.getElementById("add-employee-modal");
    const closeModal = document.querySelector(".close-modal");
    const employeeForm = document.getElementById("add-employee-form");
    const employeeTableBody = document.getElementById("employee-tbody");
    const moduleButtons = document.querySelectorAll(".module-btn");
    const moduleInput = document.getElementById("module");

    // Open Add Employee Modal
    addEmployeeBtn.addEventListener("click", function () {
        addEmployeeModal.classList.remove("hidden");
    });

    // Close Modal
    closeModal.addEventListener("click", function () {
        addEmployeeModal.classList.add("hidden");
        employeeForm.reset();
    });

    // Select Module for Employee
    moduleButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            moduleInput.value = btn.getAttribute("data-module");
            moduleButtons.forEach((button) => button.classList.remove("selected"));
            btn.classList.add("selected");
        });
    });

    // Fetch and Populate Employee Table
    function fetchEmployees() {
        fetch("/manage-users/")
            .then(response => response.json())
            .then(data => {
                employeeTableBody.innerHTML = "";
                data.forEach(employee => {
                    const row = `
                        <tr>
                            <td>${employee.employee_number}</td>
                            <td>${employee.name}</td>
                            <td>${employee.first_name || ''}</td>
                            <td>${employee.last_name || ''}</td>
                            <td>${employee.email}</td>
                            <td>${employee.module}</td>
                            <td>${employee.role}</td>
                            <td>${employee.status}</td>
                            <td>
                                <!-- Actions Dropdown -->
                                <div class="dropdown">
                                    <button class="btn btn-secondary dropdown-toggle" type="button" data-toggle="dropdown">
                                        <i class="fas fa-cogs"></i>
                                    </button>
                                    <div class="dropdown-menu">
                                        <a class="dropdown-item" href="/change-status/${employee.id}/active">
                                            <i class="fas fa-check-circle"></i> Activate
                                        </a>
                                        <a class="dropdown-item" href="/change-status/${employee.id}/inactive">
                                            <i class="fas fa-times-circle"></i> Deactivate
                                        </a>
                                        <a class="dropdown-item" href="/change-status/${employee.id}/suspended">
                                            <i class="fas fa-ban"></i> Suspend
                                        </a>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <!-- Email Actions Dropdown -->
                                <div class="dropdown">
                                    <button class="btn btn-secondary dropdown-toggle" type="button" data-toggle="dropdown">
                                        <i class="fas fa-envelope"></i>
                                    </button>
                                    <div class="dropdown-menu">
                                        ${emailActionsTemplate(employee)}
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `;
                    employeeTableBody.insertAdjacentHTML("beforeend", row);
                });

                attachEventListeners();
            })
            .catch(error => console.error("Error fetching employees:", error));
    }

    // Email Actions Template
    function emailActionsTemplate(employee) {
        if (employee.status === "pending") {
            return `
                <a class="dropdown-item" href="#" data-email="${employee.email}" data-action="Onboarding" data-id="${employee.id}">
                    <i class="fas fa-user-plus"></i> Onboarding
                </a>
                <a class="dropdown-item disabled text-muted" href="#" style="pointer-events: none;">
                    <i class="fas fa-unlock-alt"></i> Unlock
                </a>
            `;
        } else if (employee.status === "active") {
            return `
                <a class="dropdown-item" href="#" data-email="${employee.email}" data-action="Unlock" data-id="${employee.id}">
                    <i class="fas fa-unlock-alt"></i> Unlock
                </a>
            `;
        }
        return `
            <a class="dropdown-item disabled text-muted" href="#" style="pointer-events: none;">
                <i class="fas fa-unlock-alt"></i> Unlock
            </a>
        `;
    }

    // Handle Form Submission
    employeeForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(employeeForm);
        const employeeData = Object.fromEntries(formData.entries());

        fetch("/manage-users/add/", {
            method: "POST",
            body: JSON.stringify(employeeData),
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
        })
            .then(response => {
                if (response.ok) return response.json();
                throw new Error("Failed to add employee");
            })
            .then(() => {
                Swal.fire("Success", "Employee added successfully!", "success").then(() => {
                    fetchEmployees();
                    addEmployeeModal.classList.add("hidden");
                    employeeForm.reset();
                });
            })
            .catch(error => {
                Swal.fire("Error", error.message, "error");
            });
    });

    // Attach Event Listeners for Edit and Delete
    function attachEventListeners() {
        document.querySelectorAll(".edit-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const employeeId = btn.getAttribute("data-id");
                window.location.href = `/manage-users/${employeeId}/edit/`;
            });
        });

        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const employeeId = btn.getAttribute("data-id");
                Swal.fire({
                    title: "Are you sure?",
                    text: "This action cannot be undone!",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#d33",
                    cancelButtonColor: "#3085d6",
                    confirmButtonText: "Yes, delete it!",
                }).then(result => {
                    if (result.isConfirmed) {
                        fetch(`/manage-users/${employeeId}/delete/`, {
                            method: "DELETE",
                            headers: {
                                "X-CSRFToken": getCSRFToken(),
                            },
                        })
                            .then(response => {
                                if (response.ok) {
                                    Swal.fire("Deleted!", "Employee has been deleted.", "success").then(() => {
                                        fetchEmployees();
                                    });
                                } else {
                                    throw new Error("Failed to delete employee");
                                }
                            })
                            .catch(error => {
                                Swal.fire("Error", error.message, "error");
                            });
                    }
                });
            });
        });
    }

    // Get CSRF Token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }

    // Initial Fetch for Employee Table
    fetchEmployees();
});
