
/*
*** URL-based router for displaying the main content based on the navbar
*/

const pageTitle = "Pong";

import { handleResponseForContentUpdate, updateContent } from './index.js'


document.addEventListener("click", (e) => {
	// Save the clicked element as target
	const target = e.target;
	// Check if the clicked element is a part of the nav anchors
	if (!target.matches("nav a")) {
		return ;
	}
	// Prevent the navigation to a new page
	e.preventDefault();
	route();
})

// An object of the possible routes (eg. views, pages... etc)
// * * * * REMEMBER TRAILING `/` FOR BACKEND CALLS TO AVOID HOURS OF PAIN!!!!! * * * *
const routes = {
	404 : {
		view: "/app/notfound/",
		title: "404 | " + pageTitle,
		description: "Page not found"
	},
	"/" : {
		view: "/app/play/",
		title: "Play | " + pageTitle,
		description: "Play games"
	},
	"/play" : {
		view: "/app/play/",
		title: "Play | " + pageTitle,
		description: "Play games"
	},
	"/login" : {
		view: "/app/login/",
		title: "Login | " + pageTitle,
		description: "Login"
	}, 
	"/register" : {
		view: "/app/register/",
		title: "Register | " + pageTitle,
		description: "Register to play!"
	},
	"/profile" : {
		view: "app/profile/",
		title: "test_profile | " +  pageTitle,
		description: "Test profile"
	},
	"/play/pong" : {
		view: "/pong/post_pong_canvas/",
		title: "Play | " + pageTitle,
		description: "Play games"
	},
	"/play/color" : {
		view: "/pong/post_cw_canvas/",
		title: "Play | " + pageTitle,
		description: "Play games"
	}
}


// Checks the URL
const route = (event) => {
	console.log('In route()');
	// The event is either the one passed to it, or use the window event if not (prev / forward buttons)
	event = event || window.event;
	event.preventDefault();
	// Update browser history without triggering page reload
	console.log("route event target : " + event.target.href)
	console.log("route window location : " + window.location.href)
	// don't push to history or navigate if we are already there
	if (event.target.href == window.location.href)
		return ;
	console.log('route(): pushing this to history: ' + event.target.href);
	window.history.pushState("", "", event.target.href);
	locationHandler();
}


//used when redirect (3XX) codes in responses
const routeRedirect = (target) => {
	console.log('In routeRedirect()... pushing to history: ' + target);
	window.history.pushState("", "", target);
	locationHandler();
}


function removeExtraLeadingAndTrailingPartsOfLocation(location) {

	if (location.endsWith('/'))
		location = location.slice(0, -1);
	if (location.length == 0)
		location = "/";
	if (location.startsWith('/app/'))
		location = location.substring(4);
	return location;
}


function checkForCorrectProfilePathRoute(location, route) {

	const profileRe = new RegExp("^/profile/[a-zA-Z0-9]+(/)?$")
	if (profileRe.test(location)) {
		route = {
			view: "/app" + location,
			title: "Profile | " + pageTitle,
			description: "PogChamp Profile"}
	}
	return route
}


// match window location to route, fetch the content
const locationHandler = async () => {
	console.log('In locationHandler()');
	
	let location = window.location.pathname;
	location = removeExtraLeadingAndTrailingPartsOfLocation(location);

	console.log('locationHandler(): matching this to routes: ' + location);
	// Check the routes (the views above) for a match, if no match: 404
	let route = routes[location] || routes[404];
	console.log("route before profile correction: " + route.view);
	if (route == routes[404])
		route = checkForCorrectProfilePathRoute(location, route);

	//send request with querystring
	const querystring = window.location.search;
	console.log('locationHandler(): fetching this: ' + route.view + querystring);
	const response = await fetch(route.view + querystring);
	handleResponseForContentUpdate(response, route.title, route.description)
}

// Add an event listener to the window that looks for URL changes
window.onpopstate = locationHandler;

// Modify the URL to match the route
window.route = route;

// Run route as soon as the page loads
locationHandler();

export { routeRedirect, locationHandler }