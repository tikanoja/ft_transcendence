document.addEventListener("DOMContentLoaded", function () {
	// Get the current URL path
	var currentPath = window.location.pathname;

	// Find the link corresponding to the current URL path
	var activeLink = document.querySelector('.nav-link[href="' + currentPath + '"]');

	// If a matching link is found, add 'active' class to it
	if (activeLink) {
		activeLink.classList.add('active');
	}
});

function setActive(link) {
	var links = document.querySelectorAll('.nav-link');
	links.forEach(function (el) {
		el.classList.remove('active');
	});
	link.classList.add('active');
}


// List all the necessary event listeners 
const updateEventListeners = () => {
	const fetchButton = document.getElementById("fetchButton");
    if (fetchButton) {
		fetchButton.removeEventListener("click", fetchData);
        fetchButton.addEventListener("click", fetchData);
    }
}

// Define the functions for the events listed above!
const fetchData = () => {
	var greetings = "hello from index.js";
	greetings = //fetch something from django
	console.log(greetings);
}
