import { routeRedirect } from './router.js'

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

window.setActive = setActive;

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

function checkLogin() {
    fetch('app/check_login/', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
    .then(response => {
        if (!response.ok) {
            return false;
        }
        return response.json()
    })
    .then(data => {
        if (data.status === 'authenticated') {
            return true;
        } else {
            return false;
        }
    })
    .catch(error => {
        console.error('Problem with fetch call:', error);
        return false;
    });
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

const sendPostRequest = async (endpoint, data) => {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: data
    })
    console.log("Response status in sendrequest: ", response.status)
    return response
}

const sendGetRequest = async (endpoint, data, callback) => {
    const response = await fetch(endpoint, {
        method: 'GET'
    })
    return response
}


// function updateEventListeners(buttonId, event, nameOfF)
// {
//     var button = document.getElementById(buttonId);
//     var func = ; // hey javascript get me this function with the name of nameofF
//     button.removeEventListener(event, func);
// }

function updateEventListeners() {
    // Check if the buttons exist on the current view
    // var connectButton = document.getElementById('connectButton');
    // var userConnectButton = document.getElementById('user-connectButton');
    // var userRetrieveButton = document.getElementById('user-retrieveButton');
    var loginForm = document.getElementById('loginForm');
    var registerForm = document.getElementById('registerForm');
    var loginButton = document.getElementById('loginButton');
    var usernameButton = document.getElementById('getUsernameButton');
    var logoutButton = document.getElementById('logoutButton');

    // Remove existing event listeners if any
    // if (connectButton) {
    //     connectButton.removeEventListener('click', connectButtonClickHandler);
    // }
    // if (userConnectButton) {
    //     userConnectButton.removeEventListener('click', userConnectButtonClickHandler);
    // }
    // if (userRetrieveButton) {
    //     userRetrieveButton.removeEventListener('click', userRetrieveButtonClickHandler);
    // }
    if (loginForm) {
        loginForm.removeEventListener('submit', loginFormHandler);
    }
    if (registerForm) {
        registerForm.removeEventListener('submit', submitRegistrationHandler);
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

    // Attach event listeners only if the buttons exists
    // if (connectButton) {
    //     connectButton.addEventListener('click', connectButtonClickHandler);
    // }
    // if (userRetrieveButton) {
    //     userRetrieveButton.addEventListener('click', userRetrieveButtonClickHandler);
    // }
    // if (userConnectButton) {
    //     userConnectButton.addEventListener('click', userConnectButtonClickHandler);
    // }
    if (loginForm) {
        loginForm.addEventListener('submit', loginFormHandler);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', submitRegistrationHandler);
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

// function connectButtonClickHandler() {
//     const socket = new WebSocket('wss://localhost/ws/pong/');
//     // const socket = new WebSocket('wss://backend:8000/ws/pong/');
//     socket.onerror = function(error) {
//         console.log('WebSocket Error: ', error);
//     };
//     socket.addEventListener('open', function (event) {
//         console.log('WebSocket connection opened:', event);
//         socket.send(JSON.stringify({ message: 'hello world' }));
//     });
//     socket.addEventListener('message', function (event) {
// 		console.log('WebSocket message received:', event.data);
// 	});
//     socket.addEventListener('close', function (event) {
//         console.log('WebSocket connection closed:', event);
//     });
// }

// function userConnectButtonClickHandler() {
//     const socket = new WebSocket('wss://localhost/ws/user/');
//     socket.onerror = function(error) {
//         console.log('WebSocket Error: ', error);
//     };
//     socket.addEventListener('open', function (event) {
//         console.log('WebSocket connection opened:', event);
//         socket.send(JSON.stringify({ message: 'hello world' }));
//     });
//     socket.addEventListener('message', function (event) {
// 		console.log('WebSocket message received:', event.data);
// 	});
//     socket.addEventListener('close', function (event) {
//         console.log('WebSocket connection closed:', event);
//     });
// }

// ***** USER SERVICE HANDLERS ***** //


function loginButtonClickHandler(event) {
    event.preventDefault();
    console.log("sending loqin request!");

    var loginData = {};
    loginData["username"] = document.getElementById('usernameLogin').value;
    loginData["password"] = document.getElementById('passwordLogin').value;

    var endpoint = '/app/login_user/';
    sendRequest(endpoint, loginData, (response) => {
        console.log('Received response:', response);
    });
}

function usernameButtonClickHandler(event) {
    event.preventDefault();
    console.log("requesting username!");

    var endpoint = 'http://localhost:8001/app/get_current_username/'
    sendRequest(endpoint, null, (response) => {
        console.log('Received response:', response);
    });
}

async function logoutButtonClickHandler(event) {
    event.preventDefault();
    console.log("requesting logout!");

    const querystring = window.location.search;
    var endpoint = '/app/logout/' + querystring;
    let response = await sendPostRequest(endpoint, null);
    if (response.redirected) {
        console.log('redirect status found');
        console.log(response)
        // do we display content and handle routing from here?
        // or change routing to trigger the next request
        let redirect_location = response.url;
        console.log('in logoutButtonClickHandler. redir location: ' + redirect_location)
        routeRedirect(redirect_location)
        // routeRedirect('/play');
    }
}

const submitRegistrationHandler = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);

    const html = await fetch('/app/register/', {
        method: 'POST',
        body: formData
    }).then((response) => response.text());

    document.getElementById("content").innerHTML = html;
	document.title = "Registration | Pong";
	document.querySelector('meta[name="description"]').setAttribute("content", "Registration");
    updateEventListeners();
}


const loginFormHandler = async (event) => {
    event.preventDefault();
    console.log("in loginFormHandler")
    const formData = new FormData(event.target);
    const querystring = window.location.search;
	let response = await sendPostRequest('/app/login/' + querystring, formData);
	// html = response.body();
    // console.log(html);
    console.log("Response status: ", response.status, "Redirect: ", response.redirected)
    if (response.redirected) {
        console.log('redirect status found');
        console.log(response)
        // do we display content and handle routing from here?
        // or change routing to trigger the next request
        let redirect_location = response.url;
        console.log('in loginFormHandler. redir location: ' + redirect_location)
        routeRedirect(redirect_location)
        // routeRedirect('/play');
    }
	else if (response.ok) {
        console.log('response,ok triggered');
		// stay on this page, display the content again
        response.text().then(function (text) {
            document.getElementById("content").innerHTML = text;
            document.title = "Login | Pong";
            document.querySelector('meta[name="description"]').setAttribute("content", "Login");
            updateEventListeners();
        })
	}
	else {
		console.log("Response status: ", response.status)
		// some 400 or 500 code probably, show the error that was sent?
	}
}

export { updateEventListeners, setActive, checkLogin }