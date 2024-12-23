const body = document.querySelector("body"),
      modeToggle = body.querySelector(".mode-toggle");
      sidebar = body.querySelector("nav");
      sidebarToggle = body.querySelector(".sidebar-toggle");

let getMode = localStorage.getItem("mode");
if(getMode && getMode ==="dark"){
    body.classList.toggle("dark");
}

let getStatus = localStorage.getItem("status");
if(getStatus && getStatus ==="close"){
    sidebar.classList.toggle("close");
}

modeToggle.addEventListener("click", () =>{
    body.classList.toggle("dark");
    if(body.classList.contains("dark")){
        localStorage.setItem("mode", "dark");
    }else{
        localStorage.setItem("mode", "light");
    }
});

sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
    if(sidebar.classList.contains("close")){
        localStorage.setItem("status", "close");
    }else{
        localStorage.setItem("status", "open");
    }
})


// Dropdown Toggle Functionality
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent default link behavior
            
            const parent = toggle.parentElement;
            const submenu = parent.querySelector('.submenu');
            const arrow = toggle.querySelector('.dropdown-arrow');

            // Close other dropdowns
            document.querySelectorAll('.dropdown').forEach(item => {
                if (item !== parent) {
                    item.classList.remove('active');
                    const otherSubmenu = item.querySelector('.submenu');
                    const otherArrow = item.querySelector('.dropdown-arrow');
                    if (otherSubmenu) otherSubmenu.style.display = 'none';
                    if (otherArrow) otherArrow.style.transform = 'rotate(0deg)';
                }
            });

            // Toggle current dropdown
            parent.classList.toggle('active');
            submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
            arrow.style.transform = parent.classList.contains('active') 
                ? 'rotate(180deg)' 
                : 'rotate(0deg)';
        });
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const sidebarLinks = document.querySelectorAll(".sidebar-link");
    const breadcrumbList = document.getElementById("breadcrumb-list");
    const pageContent = document.getElementById("page-content");

    // Helper function to update breadcrumbs
    function updateBreadcrumbs(pageName) {
        // Clear existing breadcrumbs (except Home)
        breadcrumbList.innerHTML = `
            <li><a href="#" data-page="Home" class="breadcrumb-link">Home</a></li>
        `;
        
        // Add the new breadcrumb
        breadcrumbList.innerHTML += `
            <li> &gt; </li>
            <li>${pageName}</li>
        `;
    }

    // Event listener for sidebar links
    sidebarLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const pageName = link.getAttribute("data-page");

            // Update breadcrumbs
            updateBreadcrumbs(pageName);

            // Update page content dynamically (optional)
            pageContent.innerHTML = `
                <h2>${pageName}</h2>
                <p>Welcome to the ${pageName} page.</p>
            `;
        });
    });

    document.addEventListener("DOMContentLoaded", () => {
        const profileSection = document.querySelector('.profile-section');
        const profileDropdown = document.querySelector('.profile-dropdown');
    
        if (profileSection && profileDropdown) {
            // Toggle dropdown visibility on click
            profileSection.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent the click from propagating to the document
                profileDropdown.classList.toggle('show');
            });
    
            // Hide dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!profileSection.contains(e.target)) {
                    profileDropdown.classList.remove('show');
                }
            });
        }

        // Tab switching functionality for main content (Optional)
        const tabs = document.querySelectorAll('.top .breadcrumbs a');
        const sections = document.querySelectorAll('.main-content > div');

        tabs.forEach((tab, index) => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                // Hide all sections
                sections.forEach(section => section.style.display = 'none');
                // Show selected section
                if (sections[index]) {
                    sections[index].style.display = 'block';
                }
            });
        });

        // Ensure only the first section is visible on page load (Optional)
        sections.forEach((section, index) => {
            section.style.display = index === 0 ? 'block' : 'none';
        });
    });

});



