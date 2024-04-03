import { routeRedirect } from './router.js'
import { startScreen } from './pong.js'

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

const sendPostRequest = async (endpoint, data) => {
    console.log('In sendPostRequest()');
    const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
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

function updateEventListeners() {
    var loginForm = document.getElementById('loginForm');
    var registerForm = document.getElementById('registerForm');
    var logoutButton = document.getElementById('logoutButton');
    var deleteForm = document.getElementById('deleteAccountForm');
    var playButton = document.getElementById('playButton');
    if (deleteForm) {
        deleteForm.removeEventListener('submit', deleteFormHandler);
    }
	var playButton = document.getElementById('playButton');
    
    if (loginForm) {
        loginForm.removeEventListener('submit', loginFormHandler);
    }
    if (registerForm) {
        registerForm.removeEventListener('submit', submitRegistrationHandler);
    }
    if (logoutButton) {
        logoutButton.removeEventListener('click', logoutButtonClickHandler);
    }
	if (playButton) {
        playButton.removeEventListener('click', playButtonClickHandler);
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', loginFormHandler);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', submitRegistrationHandler);
    }
    if (logoutButton) {
        logoutButton.addEventListener('click', logoutButtonClickHandler);
    }
    if (deleteForm) {
        deleteForm.addEventListener('submit', deleteFormHandler);
    }
	if (playButton) {
        playButton.addEventListener('click', playButtonClickHandler);
    }
}

function updateContent(html, title, description) {
    document.getElementById("content").innerHTML = html;
	document.title = title;
	document.querySelector('meta[name="description"]').setAttribute("content", description);
    updateEventListeners();
}

// ***** USER SERVICE HANDLERS ***** //

async function logoutButtonClickHandler(event) {
    console.log('In logoutButtonClickHandler()');	
    event.preventDefault();

    const querystring = window.location.search;
    var endpoint = '/app/logout/' + querystring;
    const response = await sendPostRequest(endpoint, null);
    if (response.redirected) {
        let redirect_location = response.url;
        routeRedirect(redirect_location);
    } else {
        console.log("this shouldn't be? logout should always lead to redirection?");
    }
}

const submitRegistrationHandler = async (event) => {
    console.log('In submitRegistrationHandler');
    event.preventDefault();
    const formData = new FormData(event.target);

    const querystring = window.location.search;
    var endpoint = '/app/register/' + querystring;
    const response = await sendPostRequest(endpoint, formData);
    if (response.redirected) {
        let redirect_location = response.url;
        console.log("redir to: ", redirect_location);
        routeRedirect(redirect_location);
    } else if (response.ok) {
        // handling normal content update
        const html = await response.text();
        updateContent(html, "Registration | Pong", "Description");
    } else {
        // something is not quite right...
        console.log('submitRegistrationHandler(): response status: ' + response.status);
    }
}

const playButtonClickHandler = async (event) => {
    console.log('In playButtonClickHandler');
    startScreen();
}

const loginFormHandler = async (event) => {
    console.log('In loginFormHandler()');
    event.preventDefault();
    const formData = new FormData(event.target);
    const querystring = window.location.search;
    var endpoint = '/app/login/' + querystring;
	const response = await sendPostRequest(endpoint, formData);
    if (response.redirected) {
        let redirect_location = response.url;
        console.log("redir to: ", redirect_location);
        routeRedirect(redirect_location);
    } else if (response.ok) {
        const html = await response.text();
        updateContent(html, "Login | Pong", "Login form");
	} else {
		console.log("Response status in loginFormHandler(): ", response.status)
	}
}


const deleteFormHandler= async (event) => {
    event.preventDefault();
    console.log("in loginFormHandler")

    const formData = new FormData(event.target);

	let response = await sendPostRequest('/app/delete_account/', formData);
	
    console.log("Response status: ", response.status, "Redirect: ", response.redirected)
    if (response.redirected) {
        console.log('redirect status found');
      
        routeRedirect('/login');
    }
	else if (response.ok) {
        console.log('response,ok triggered');
		// stay on this page, display the content again
        response.text().then(function (text) {
            document.getElementById("content").innerHTML = text;
            document.title = "Delete Account | Pong";
            document.querySelector('meta[name="description"]').setAttribute("content", "Delete Account");
            updateEventListeners();
        })
	}
	else {
		console.log("Response status: ", response.status)
		// some 400 or 500 code probably, show the error that was sent?
	}
}
const start_game_loop = async () => {
    const responseData = await sendGetRequest('pong/start_background_loop').then((response) => response.text());
    console.log('start game loop:	', responseData);
    return (responseData);
}

const stop_game_loop = async () => {
    const responseData = await sendGetRequest('pong/stop_background_loop').then((response) => response.text());
    console.log('stop game loop:	', responseData);
    return (responseData);
};


const start_game = async () => {
    const responseData = await sendGetRequest('pong/game_start').then((response) => response.text());
    console.log('start game:	', responseData);
    return (responseData);
}

const stop_game = async () => {
    const responseData = await sendGetRequest('pong/game_stop').then((response) => response.text());
    console.log('stop game :	', responseData);
    return (responseData);
}


const left_paddle_up = async () => {
    const responseData = await sendGetRequest('pong/left_paddle_up').then((response) => response.text());
    console.log('left paddle up:	', responseData);
    return (responseData);
}

const left_paddle_up_release = async () => {
    const responseData = await sendGetRequest('pong/left_paddle_up_release/').then((response) => response.text());
    console.log('left_paddle_up_release:	', responseData);
    return (responseData);
}

const left_paddle_down = async () => {
    const responseData = await sendGetRequest('pong/left_paddle_down').then((response) => response.text());
    console.log('left paddle up:	', responseData);
    return (responseData);
}

const left_paddle_down_release = async () => {
    const responseData = await sendGetRequest('pong/left_paddle_down_release/').then((response) => response.text());
    console.log('left_paddle_up_release:	', responseData);
    return (responseData);
}

const right_paddle_up = async () => {
    const responseData = await sendGetRequest('pong/right_paddle_up').then((response) => response.text());
    console.log('right paddle up:	', responseData);
    return (responseData);
}

const right_paddle_up_release = async () => {
    const responseData = await sendGetRequest('pong/right_paddle_up_release/').then((response) => response.text());
    console.log('right_paddle_up_release:	', responseData);
    return (responseData);
}

const right_paddle_down = async () => {
    const responseData = await sendGetRequest('pong/right_paddle_down').then((response) => response.text());
    console.log('right paddle up:	', responseData);
    return (responseData);
}

const right_paddle_down_release = async () => {
    const responseData = await sendGetRequest('pong/right_paddle_down_release/').then((response) => response.text());
    console.log('right_paddle_up_release:	', responseData);
    return (responseData);
}

const get_game_state = async () => {
    const responseData = await sendGetRequest('pong/get_game_state/').then((response) => response.text());
    console.log('from timo pong game_state:	', responseData);
    return (responseData);
}

export { checkLogin, updateContent, start_game_loop, stop_game_loop, start_game, stop_game, get_game_state, left_paddle_up, left_paddle_up_release , left_paddle_down, left_paddle_down_release , right_paddle_up, right_paddle_up_release , right_paddle_down, right_paddle_down_release, updateEventListeners, setActive }

// export { updateEventListeners, setActive, checkLogin, updateContent }
