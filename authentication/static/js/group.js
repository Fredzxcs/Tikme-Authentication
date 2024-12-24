document.addEventListener("DOMContentLoaded", () => {
    const groupsTableBody = document.getElementById("groups-table-body");
    const addGroupForm = document.getElementById("add-group-form");
    const groupNameInput = document.getElementById("group-name");

    // Fetch and render groups
    const fetchGroups = async () => {
        const response = await fetch("/groups/");
        const groups = await response.json();

        groupsTableBody.innerHTML = "";
        groups.forEach((group, index) => {
            const row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${group.name}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="deleteGroup(${group.id})">Delete</button>
                    </td>
                </tr>
            `;
            groupsTableBody.innerHTML += row;
        });
    };

    // Add new group
    addGroupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const groupName = groupNameInput.value;

        const response = await fetch("/groups/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name: groupName }),
        });

        if (response.ok) {
            fetchGroups();
            groupNameInput.value = "";
        } else {
            alert("Error adding group.");
        }
    });

    // Delete group
    window.deleteGroup = async (groupId) => {
        const response = await fetch(`/groups/${groupId}/`, {
            method: "DELETE",
        });

        if (response.ok) {
            fetchGroups();
        } else {
            alert("Error deleting group.");
        }
    };

    // Initial fetch
    fetchGroups();
});
