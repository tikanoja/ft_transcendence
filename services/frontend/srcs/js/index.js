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

// STYLING UP THERE
// 'Play' JS DOWN HERE

const socket = new WebSocket('ws://localhost:8000/ws/pong/');
// const socket = new WebSocket('wss://backend:8000/ws/pong/');
socket.onerror = function(error) {
    console.log('WebSocket Error: ', error);
};

socket.addEventListener('open', function (event) {
    console.log('WebSocket connection opened:', event);
});
socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed:', event);
});

function sendRequest(endpoint, callback) {
    // send json to backend to the specified endpoint
    socket.send(JSON.stringify({ endpoint: endpoint }));

    // handle response from backend
    socket.onmessage = function (event) {
        var response = JSON.parse(event.data);
        console.log(response);
        if (callback) {
            callback(response);
        }
    };
}

function updateEventListeners() {
    // Check if the buttons exist on the current view
    var increaseButton = document.getElementById('increaseButton');
    var decreaseButton = document.getElementById('decreaseButton');
    var retrieveButton = document.getElementById('retrieveButton');
    var connectButton = document.getElementById('connectButton');


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
    if (connectButton) {
        connectButton.removeEventListener('click', connectButtonClickHandler);
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
    if (connectButton) {
        connectButton.addEventListener('click', connectButtonClickHandler);
    }
}

// Define separate click handlers for each button
function increaseButtonClickHandler() {
    sendRequest('increase_number/', function (response) {
        console.log('Increased number:', response.number);
    });
}

function decreaseButtonClickHandler() {
    sendRequest('decrease_number/', function (response) {
        console.log('Decreased number:', response.number);
    });
}

function retrieveButtonClickHandler() {
    sendRequest('get_number/', function (response) {
        console.log('Current number:', response.number);
    });
}

function connectButtonClickHandler() {
    const socket = new WebSocket('wss://localhost/ws/pong/');
    // const socket = new WebSocket('wss://backend:8000/ws/pong/');
    socket.onerror = function(error) {
        console.log('WebSocket Error: ', error);
    };
    socket.addEventListener('open', function (event) {
        console.log('WebSocket connection opened:', event);
        socket.send(JSON.stringify({ message: 'hello world' }));
    });
    socket.addEventListener('message', function (event) {
		console.log('WebSocket message received:', event.data);
	});
    socket.addEventListener('close', function (event) {
        console.log('WebSocket connection closed:', event);
    });
}