import { sendPostRequest, sendGetRequest, updateContent, updateElementContent, handleResponseForContentUpdate, handleResponseForElementUpdate } from './index.js'
import { routeRedirect } from './router.js'
import { startScreen} from './pong.js'
import { startScreenColorwar} from './colorwar.js'


const loginEvent  = new Event("login");
const logoutEvent = new Event("logout");

/*
single_listeners = [
    {
        element: document element,
        event: e.g submit,
        handler: function
    },
    ...
]
*/

// set all lone elements here
function getSingleHandlerDetails() {

    const elementsList = [
        {
            element: document.getElementById('loginForm'),
            event_name: "submit",
            handler: loginFormHandler
        },
        {
            element: document.getElementById('registerForm'),
            event_name: "submit",
            handler: submitRegistrationHandler
        },
        {
            element: document.getElementById('logoutButton'),
            event_name: "click",
            handler: logoutButtonClickHandler
        },
        {
            element: document.getElementById('playButton'),
            event_name: "click",
            handler: playButtonClickHandler
        },
        {
            element:  document.getElementById('ColorwarPlayButton'),
            event_name: "click",
            handler: playButtoncolorwarClickHandler
        },
        {
            element: document.getElementById('addFriendButton'),
            event_name: "click",
            handler: addFriendHandler
        },
        {
            element: document.getElementById('blockUserButton'),
            event_name: "click",
            handler: blockUserHandler
        },
        {
            element:  document.getElementById('gameInviteForm'),
            event_name: "submit",
            handler: gameRequestHandler
        },
        {
            element: document.getElementById('playButton'),
            event_name: "click",
            handler: playButtonClickHandler
        },
        {
            element: document.getElementById('delete-account-form'),
            event_name: "submit",
            handler: manageAccountHandler
        },
        {
            element: document.getElementById('name-change-form'),
            event_name: "submit",
            handler: manageAccountHandler
        },
        {
            element:  document.getElementById('email-change-form'),
            event_name: "submit",
            handler: manageAccountHandler
        },
        {
            element: document.getElementById('password-change-form'),
            event_name: "submit",
            handler: manageAccountHandler
        },
        {
            element: document.getElementById('profile_picture_upload'),
            event_name: "submit",
            handler: manageAccountHandler
        },
        {
            element: document.getElementById('gameRenderButton'),
            event_name: "click",
            handler: gameRenderButtonHandler
        },
        {
            element: document.getElementById('startTournamentForm'),
            event_name: "submit",
            handler: tournamentFormHandler
        },
        {
            element: document.getElementById('tournamentInviteForm'),
            event_name: "submit",
            handler: tournamentFormHandler
        },
        {
            element: document.getElementById('tournamentJoinForm'),
            event_name: "submit",
            handler: tournamentFormHandler
        },
        {
            element: document.getElementById('autoRegister'),
            event_name: "click",
            handler: automate_register
        }
    ];
    return elementsList
}


// set all elements that have multiples here
function getMultipleElementDetails() {

    const elementsList = [
        {
            element: document.querySelectorAll('[id^="friendRequestButton"]'),
            event_name: "click",
            handler: friendRequestHandler
        },
        {
            element: document.querySelectorAll('[id^="gameRequestButton"]'),
            event_name: "click",
            handler: gameResponseHandler
        },
        {
            element: document.querySelectorAll('[id^="playerAuthForm"]'),
            event_name: "submit",
            handler: playerAuthHandler
        },
        {
            element: document.querySelectorAll('[id^="tournamentButton"]'),
            event_name: "click",
            handler: tournamentButtonHandler
        }
    ];
    return elementsList
}

// ***** USER SERVICE HANDLERS ***** //

async function logoutButtonClickHandler(event) {
	
    event.preventDefault();

    const querystring = window.location.search;
    var endpoint = '/app/logout/' + querystring;
    const response = await sendPostRequest(endpoint, null);
    document.dispatchEvent(logoutEvent);
    if (response.redirected) {
        let redirect_location = response.url;
        routeRedirect(redirect_location);
    } else {
        console.log("Logout failed to redirect");
    }
}


const submitRegistrationHandler = async (event) => {
    
    event.preventDefault();
    const formData = new FormData(event.target);

    const querystring = window.location.search;
    var endpoint = '/app/register/' + querystring;
    const response = await sendPostRequest(endpoint, formData);
    await handleResponseForContentUpdate(response, "Registration | Pong", "Register to Play Pong!");
}


const loginFormHandler = async (event) => {
	
	event.preventDefault();
	const formData = new FormData(event.target);
	const querystring = window.location.search;
	var endpoint = '/app/login/' + querystring;
	const response = await sendPostRequest(endpoint, formData);
	document.dispatchEvent(loginEvent);
    await handleResponseForContentUpdate(response, "Login | Pong", "Login form");
}


const blockUserHandler = async (event) => {
	
	event.preventDefault();
	let form = document.getElementById("addFriendForm");
	const formData = new FormData(form);
	const querystring = window.location.search;
	var endpoint = '/app/block_user/' + querystring;
	const response = await sendPostRequest(endpoint, formData);
    await handleResponseForElementUpdate(response, "friends");
}


const addFriendHandler = async (event) => {
	
	event.preventDefault();
	let form = document.getElementById("addFriendForm");
	const formData = new FormData(form);
	const querystring = window.location.search;
	var endpoint = '/app/friends/' + querystring;
	const response = await sendPostRequest(endpoint, formData);
    await handleResponseForElementUpdate(response, "friends");
}


const friendRequestHandler = async (event) => {

	event.preventDefault();

	var fromUser = event.target.getAttribute('data-from-user');
	var action = event.target.getAttribute('data-action');

	var data = {
		'from_user': fromUser,
		'action': action,
		'request_type': 'friendResponse'
	};

	const querystring = window.location.search;
	var endpoint = '/app/friends/' + querystring;
	const response = await sendPostRequest(endpoint, data, true);
    await handleResponseForElementUpdate(response, "friends");
}


const manageAccountHandler = async (event) => {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    formData.append("form_id", event.target.id);

	let response = await sendPostRequest('/app/manage_account/', formData);
    if (response.redirected) {
        let redirect_location = response.url;
        routeRedirect(redirect_location);
    }
	else if (response.ok) {
        const html = await response.text();
        if (event.target.id === "delete-account-form") {
            window.history.pushState("", "", "/account/deleted");
            updateContent(html, "Account Deleted", "You're account is gone forever!");
        }
        else
            updateElementContent(html, "manage-account");
        if (event.target.id === "profile_picture_upload") {
            updateProfilePicture();
        }
	}
	else {
		console.log("Response status: ", response.status, " for manage account form: ", event.target.id)
	}
}


const updateProfilePicture = async(event) => {
    
    let response = await sendGetRequest("/app/profile_picture/");
    await handleResponseForElementUpdate(response, "profile-picture");
}


const profileLinkHandler = async (event) => {

    event.preventDefault();

    let profileUrl = new URL(event.target.href);
    
    if (profileUrl == window.location.href)
		return ;
    let profilePath = profileUrl.pathname;
    let profileUsername = event.target.textContent;
    let response = await sendGetRequest('/app' + profilePath);
    await handleResponseForContentUpdate(response, "Profile | " + profileUsername, "Personal Profile");
    if (response.ok)
        window.history.pushState("", "", profilePath);
}


//  ***** PLAY HANDLERS ***** //

const playButtonClickHandler = async (event) => {	
    startScreen();
}


const playButtoncolorwarClickHandler = async (event) => {

    event.preventDefault();
    startScreenColorwar();
}


const gameResponseHandler = async (event) => {

    event.preventDefault();

    var fromUser = event.target.getAttribute('data-from-user');
    var action = event.target.getAttribute('data-action');

    var data = {
        'from_user': fromUser,
        'action': action,
        'request_type': 'gameResponse'
    };

    const querystring = window.location.search;
    var endpoint = '/app/play/' + querystring;
    const response = await sendPostRequest(endpoint, data, true);
    await handleResponseForContentUpdate(response, "Play | Pong", "Play");
}


const gameRequestHandler = async (event) => {

    event.preventDefault();
    
    const formData = new FormData(event.target);
    const querystring = window.location.search;

    var endpoint = '/app/play/' + querystring;
    const response = await sendPostRequest(endpoint, formData);
    await handleResponseForContentUpdate(response, "Play | Pong", "Play games");
}


const gameRenderButtonHandler = async (event) => {

    event.preventDefault();
    var gameType = event.target.dataset.game;
    var p1 = event.target.dataset.p1;
    var p2 = event.target.dataset.p2;
    var endpoint;

    var data = {
        'p1': p1,
        'p2': p2,
        'game': gameType
    }
    if (gameType === 'Pong') {
        endpoint = '/pong/post_pong_canvas/';
    } else {
        endpoint = '/pong/post_cw_canvas/';
    }
    let response = await sendPostRequest(endpoint, data, true);
    await handleResponseForContentUpdate(response, "Playing " + gameType + " | Pong", "Playing " + gameType);
    if (response.ok)
        window.history.pushState("", "", "https://localhost/play/" + gameType.toLowerCase());
}


const playerAuthHandler = async (event) => {

    event.preventDefault();
    const formData = new FormData(event.target);

    const querystring = window.location.search;
    var endpoint = '/pong/authenticate_player/' + querystring;
    const response = await sendPostRequest(endpoint, formData);
    await handleResponseForContentUpdate(response, "Playing | Pong", "Play games");
}

const tournamentFormHandler = async (event) => {
    
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const querystring = window.location.search;

    var endpoint = '/app/tournament_forms/' + querystring;
    const response = await sendPostRequest(endpoint, formData);
    await handleResponseForContentUpdate(response, "Play | Pong", "Play games");
}

const tournamentButtonHandler = async (event) => {

    event.preventDefault();

    var action = event.target.getAttribute('data-action');

    var data = {
        'action': action,
    };

    if (action == 'nuke')
        data['tournament-id'] = event.target.getAttribute('data-tournament-id');
    else if (action == 'rejectTournamentInvite')
        data['participant_id'] = event.target.getAttribute('data-participant-id');
    else if (action == 'leaveTournament')
        data['participant_id'] = event.target.getAttribute('data-participant-id');
    else if (action == 'startTournament')
        data['tournament_id'] = event.target.getAttribute('data-tournament-id');

    const querystring = window.location.search;
    var endpoint = '/app/tournament_buttons/' + querystring;
    const response = await sendPostRequest(endpoint, data, true);
    await handleResponseForContentUpdate(response, "Tournament | Pong", "Play Tournament");
}

// ***** DEV FEATURE ***** //

const automate_register = async (event) => {
    console.log('In automate_register');
    event.preventDefault();

    const users = [
        { username: 'qwe', first_name: 'qwe', last_name: 'qwe', email: 'qwe@qwe.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'asd', first_name: 'asd', last_name: 'asd', email: 'asd@asd.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'zxc', first_name: 'zxc', last_name: 'zxc', email: 'zxc@zxc.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'jen', first_name: 'jen', last_name: 'jen', email: 'jen@jen.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'ben', first_name: 'ben', last_name: 'ben', email: 'ben@ben.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'ken', first_name: 'ken', last_name: 'ken', email: 'ken@ken.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'hen', first_name: 'hen', last_name: 'hen', email: 'hen@hen.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'foo', first_name: 'foo', last_name: 'foo', email: 'foo@foo.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'bar', first_name: 'bar', last_name: 'bar', email: 'bar@bar.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
        { username: 'baz', first_name: 'baz', last_name: 'baz', email: 'baz@baz.com', password: 'qweQWE123!@#', confirm_password: 'qweQWE123!@#' },
    ];

    for (const user of users) {
        const formData = new FormData();
        Object.entries(user).forEach(([key, value]) => formData.append(key, value));

        const querystring = window.location.search;
        var endpoint = '/app/register/' + querystring;
        const response = await sendPostRequest(endpoint, formData);
        await handleResponseForContentUpdate(response, "Registration | Pong", "Register to Play");
    }
}


export { getSingleHandlerDetails, getMultipleElementDetails, profileLinkHandler }