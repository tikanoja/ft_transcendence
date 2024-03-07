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

// Once we are using templates, we should include a csrftoken in django. Then django will be very happy and there is no need for decorator.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// callback?
function sendRequest(endpoint, data, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', endpoint, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.withCredentials = true;

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response);
            if (callback) {
                callback(response);
            }
        }
    };
    if (data)
        xhr.send(JSON.stringify(data));
    else
        xhr.send();
}

function updateEventListeners() {
    // Check if the buttons exist on the current view
    var increaseButton = document.getElementById('increaseButton');
    var decreaseButton = document.getElementById('decreaseButton');
    var retrieveButton = document.getElementById('retrieveButton');
    var connectButton = document.getElementById('connectButton');
    var userConnectButton = document.getElementById('user-connectButton');
    var userRetrieveButton = document.getElementById('user-retrieveButton');
    var registerButton = document.getElementById('registerButton');
    var loginButton = document.getElementById('loginButton');
    var usernameButton = document.getElementById('getUsernameButton');
    var logoutButton = document.getElementById('logoutButton');

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
    if (userConnectButton) {
        userConnectButton.removeEventListener('click', userConnectButtonClickHandler);
    }
    if (userRetrieveButton) {
        userRetrieveButton.removeEventListener('click', userRetrieveButtonClickHandler);
    }
    if (registerButton) {
        registerButton.removeEventListener('click', registerButtonClickHandler);
    }
    if (loginButton) {
        loginButton.removeEventListener('click', loginButtonClickHandler);
    }
    if (usernameButton) {
        usernameButton.removeEventListener('click', usernameButtonClickHandler);
    }
    if (logoutButton) {
        logoutButton.removeEventListener('click', logoutButtonClickHandler);
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
    if (userRetrieveButton) {
        userRetrieveButton.addEventListener('click', userRetrieveButtonClickHandler);
    }
    if (userConnectButton) {
        userConnectButton.addEventListener('click', userConnectButtonClickHandler);
    }
    if (registerButton) {
        registerButton.addEventListener('click', registerButtonClickHandler);
    }
    if (loginButton) {
        loginButton.addEventListener('click', loginButtonClickHandler);
    }
    if (usernameButton) {
        usernameButton.addEventListener('click', usernameButtonClickHandler);
    }
    if (logoutButton) {
        logoutButton.addEventListener('click', logoutButtonClickHandler);
    }

}

// Define separate click handlers for each button
function increaseButtonClickHandler() {
    sendRequest('http://localhost:8000/pong/increase_number/', (response) => {
        console.log('Increased number:', response.number);
    });
}

function decreaseButtonClickHandler() {
    sendRequest('http://localhost:8000/pong/decrease_number/', (response) => {
        console.log('Decreased number:', response.number);
    });
}

function retrieveButtonClickHandler() {
    sendRequest('http://localhost:8000/pong/get_number/', (response) => {
        console.log('Current number:', response.number);
    });
}

function userRetrieveButtonClickHandler() {
    sendRequest('http://localhost:8001/user/get_number/', (response) => {
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

function userConnectButtonClickHandler() {
    const socket = new WebSocket('wss://localhost/ws/user/');
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

function registerButtonClickHandler(event) {
    event.preventDefault();
    console.log("sending registration!");

    var registrationData = {};
    registrationData["username"] = document.getElementById('username').value;
    registrationData["email"] = document.getElementById('email').value;
    registrationData["firstname"] = document.getElementById('firstname').value;
    registrationData["lastname"] = document.getElementById('lastname').value;
    registrationData["password"] = document.getElementById('password').value;
    registrationData["confirm_password"] = document.getElementById('confirm_password').value;
    
    var endpoint = 'http://localhost:8001/user/register_user/';
    sendRequest(endpoint, registrationData, (response) => {
        console.log('Received response:', response);
    });
}

function loginButtonClickHandler(event) {
    event.preventDefault();
    console.log("sending loqin request!");

    var loginData = {};
    loginData["username"] = document.getElementById('usernameLogin').value;
    loginData["password"] = document.getElementById('passwordLogin').value;

    var endpoint = 'http://localhost:8001/user/login_user/';
    sendRequest(endpoint, loginData, (response) => {
        console.log('Received response:', response);
    });
}

function usernameButtonClickHandler(event) {
    event.preventDefault();
    console.log("requesting username!");

    var endpoint = 'http://localhost:8001/user/get_current_username/'
    sendRequest(endpoint, null, (response) => {
        console.log('Received response:', response);
    });
}

function logoutButtonClickHandler(event) {
    event.preventDefault();
    console.log("requesting logout!");

    var endpoint = 'http://localhost:8001/user/logout_user/';
    sendRequest(endpoint, null, (response) => {
        console.log('Received response:', response);
    });
}
