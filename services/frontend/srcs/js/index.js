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
    var connectButton = document.getElementById('connectButton');
	var testButton = document.getElementById('testButton');


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
	if (testButton) {
        testButton.removeEventListener('click', testButtonClickHandler);
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
	if (testButton) {
        testButton.addEventListener('click', testButtonClickHandler);
    }
}
document.addEventListener('keydown', function (event) {
    //playing with key bindings, currently registers the keys.
    switch (event.key) {
        case 'c':
            connectButtonClickHandler();
            break;
        case 't':
            testButtonClickHandler();
            break;
        case 'ArrowUp':
        case 'w':
            console.log("Arrow Up or 'w' key pressed");
            break;
        case 'ArrowDown':
        case 's':
            console.log("Arrow Down or 's' key pressed");
            break;
        case 'ArrowLeft':
        case 'a':
            console.log("Arrow Left or 'a' key pressed");
            break;
        case 'ArrowRight':
        case 'd':
            console.log("Arrow Right or 'd' key pressed");
            break;
        default:
            console.log('Key code for ' + event.key + ': ' + event.keyCode);
            break;
    }
});



function testButtonClickHandler(){
    sendRequest('pong/increase_number/', function (response) {
        console.log("The thing works");
    });
}

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