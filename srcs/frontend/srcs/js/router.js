
/*
*** URL-based router for displaying the main content based on the navbar
 */

const pageTitle = "Pong";

import { updateEventListeners, checkLogin } from './index.js'

// Listens to clicks on the entire document
document.addEventListener("click", (e) => {
	// Save the clicked element as target
	const target = e.target;
	// Check if the clicked element is a part of the nav anchors
	if (!target.matches("nav a")) {
		return ;
	}
	// Prevent the navigation to a new page
	// checkLogin();
	e.preventDefault();
	route();
})

// An array of the possible routes (eg. views, pages... etc)
// * * * * REMEMBER TRAILING / FOR BACKEND CALLS TO AVOID HOURS OF PAIN!!!!! * * * *
const routes = {
	404 : {
		view: "/app/notfound/",
		title: "404 | " + pageTitle,
		description: "Page not found"
	},
	"/" : {
		view: "/app/home/",
		title: "Home | " + pageTitle,
		description: "Home page"
	},
	"/play" : {
		view: "/app/play/",
		title: "Play | " + pageTitle,
		description: "Play games"
	},
	"/friends" : {
		view: "/app/friends/",
		title: "Friends | " + pageTitle,
		description: "Chat and manage friends"
	},
	"/settings" : {
		view: "/app/settings/",
		title: "Settings | " + pageTitle,
		description: "Manage your settings"
	},
	"/login" : {
		view: "/app/login/",
		title: "Login | " + pageTitle,
		description: "Login"
	}, 
	"/register" : {
		view: "/app/register/",
		title: "Login | " + pageTitle,
		description: "Login"
	},
	"/check-login" : {
		view: "../views/login.html",
		title: "Login | " + pageTitle,
		description: "Login"
	}
}
// route above should not be the same as the calls to the backend...seems fragile

// Checks the URL
const route = (event) => {
	console.log('In route()');	
	// The event is either the one passed to it, or grab the window event if not (prev / forward buttons)
	event = event || window.event;
	event.preventDefault();
	// Update browser history without triggering page reload
	if (event.target.href == window.location.href)
		return ;
	console.log('route(): pushing this to history: ' + event.target.href);
	window.history.pushState("", "", event.target.href);
	locationHandler();
}

const routeRedirect = (target) => {
	console.log('In routeRedirect()');	
	if (target == window.location.href)
		return ;	
	console.log('routeRedirect(): pushing this to history: ' + target);
	window.history.pushState("", "", target);
	locationHandler();
}

// By using 'async' we can use 'await'. This way we can use asynchronous operations without blocking the execution of other code
const locationHandler = async () => {
	console.log('In locationHandler()');
	// Get the path part of URL (eg. https://example.com/friends/profile returns /friends/profile)
	let location = window.location.pathname;
	// Redirect https://example.com to https://example.com/ in order to land on home page
	if (location.endsWith('/'))
		location = location.slice(0, -1);
	if (location.length == 0)
		location = "/";
	if (location.startsWith('/app/'))
		location = location.substring(4);

	console.log('locationHandler(): matching this to routes: ' + location)
	// Check the routes (the views above) for a match, if no match: 404
	const route = routes[location] || routes[404];
	const querystring = window.location.search;
	console.log('locationHandler(): fetching this: ' + route.view + querystring);
	const response = await fetch(route.view + querystring)//, {redirect: 'manual'});
	if (!response.ok)
		console.log("locationHandler(): Fetch status != OK");
	if (response.redirected){
		console.log('locationHandler(): Response redirected');
		console.log(response);
		const newUrl = response.url;
		if (newUrl) {
			console.log('locationHandler(): replacing history: ' + newUrl);	
			window.history.replaceState("", "", newUrl);
			// locationHandler();
			const html = await response.text();
			document.getElementById("content").innerHTML = html;
			document.title = 'oh my god it worked!!!!';
			document.querySelector('meta[name="description"]').setAttribute("content", route.description);
			updateEventListeners();
		}
	} else {
		console.log('locationHandler(): Fetch OK, no redirs, updating site content');
		const html = await response.text();
		document.getElementById("content").innerHTML = html;
		document.title = route.title;
		document.querySelector('meta[name="description"]').setAttribute("content", route.description);
		updateEventListeners();
	}
}

// Add an event listener to the window that looks for URL changes
window.onpopstate = locationHandler;
// Modify the URL to match the route
window.route = route;

// Run route as soon as the page loads
locationHandler();

export { routeRedirect, locationHandler }