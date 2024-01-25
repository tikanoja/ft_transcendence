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

function sendRequest(endpoint, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:8000/' + endpoint, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response);
            if (callback) {
                callback(response);
            }
        }
    };

    xhr.send();
}

function updateEventListeners() {
    // Check if the buttons exist on the current view
    var increaseButton = document.getElementById('increaseButton');
    var decreaseButton = document.getElementById('decreaseButton');
    var retrieveButton = document.getElementById('retrieveButton');

    // Remove existing event listeners if any
    if (increaseButton) {
        increaseButton.removeEventListener('click', increaseButtonClickHandler);
    }
    if (decreaseButton) {
        decreaseButton.removeEventListener('click', decreaseButtonClickHandler);
    }
    if (retrieveButton) {
        retrieveButton.removeEventListener('click', retrieveButtonClickHandler);
    }

    // Attach event listeners only if the buttons exist
    if (increaseButton) {
        increaseButton.addEventListener('click', increaseButtonClickHandler);
    }
    if (decreaseButton) {
        decreaseButton.addEventListener('click', decreaseButtonClickHandler);
    }
    if (retrieveButton) {
        retrieveButton.addEventListener('click', retrieveButtonClickHandler);
    }
}

// Define separate click handlers for each button
function increaseButtonClickHandler() {
    sendRequest('pong/increase_number/', function (response) {
        console.log('Increased number:', response.number);
    });
}

function decreaseButtonClickHandler() {
    sendRequest('pong/decrease_number/', function (response) {
        console.log('Decreased number:', response.number);
    });
}

function retrieveButtonClickHandler() {
    sendRequest('pong/get_number/', function (response) {
        console.log('Current number:', response.number);
    });
}
