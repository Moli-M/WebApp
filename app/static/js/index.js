// script.js

function toggleMenu() {
    var menu = document.getElementById("profile-menu");
    console.log("A")
    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}

// Close the menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.profile-button')) {
        var dropdowns = document.getElementsByClassName("profile-menu");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.style.display === "block") {
                openDropdown.style.display = "none";
            }
        }
    }
}
