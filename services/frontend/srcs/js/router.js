/*
*** URL-based router for displaying the main content based on the navbar
 */

const pageTitle = "Pong";

// Listens to clicks on the entire document
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

// An array of the possible routes (eg. views, pages... etc)
const routes = {
	404 : {
		view: "../views/404.html",
		title: "404 | " + pageTitle,
		description: "Page not found"
	},
	"/" : {
		view: "../views/home.html",
		title: "Home | " + pageTitle,
		description: "Home page"
	},
	"/play" : {
		view: "../views/play.html",
		title: "Play | " + pageTitle,
		description: "Play games"
	},
	"/friends" : {
		view: "../views/friends.html",
		title: "Friends | " + pageTitle,
		description: "Chat and manage friends"
	},
	"/settings" : {
		view: "../views/settings.html",
		title: "Settings | " + pageTitle,
		description: "Manage your settings"
	},
	"/login" : {
		view: "../views/login.html",
		title: "Login | " + pageTitle,
		description: "Login"
	}
}

// Checks the URL
const route = (event) => {
	// The event is either the one passed to it, or grab the window event if not (prev / forward buttons)
	event = event || window.event;
	event.preventDefault();
	// Update browser history without triggering page reload
	if (event.target.href == window.location.href)
		return ;
	window.history.pushState("", "", event.target.href);
	locationHandler();
}

// By using 'async' we can use 'await'. This way we can use asynchronous operations without blocking the execution of other code
const locationHandler = async () => {
	// Get the path part of URL (eg. https://example.com/friends/profile returns /friends/profile)
	const location = window.location.pathname;
	// Redirect https://example.com to https://example.com/ in order to land on home page
	if (location.length == 0)
		location = "/";
	// Check the routes (the views above) for a match, if no match: 404
	const route = routes[location] || routes[404];
	// Make a network request to the URL specified route.view
		// .then() is used to handle the Promise returned by fetch. It waits for the fetch to to complete and processes the response
		// (response) => response.text() takes the response object returned by fetch and converts its body to text
		// await waits for the entire .then() chain to resolve
	const html = await fetch(route.view).then((response) => response.text());
	// Update the main content element with the content of the retrieved html
	document.getElementById("content").innerHTML = html;
	document.title = route.title;
	document.querySelector('meta[name="description"]').setAttribute("content", route.description);

	updateEventListeners();
}

// Add an event listener to the window that looks for URL changes
window.onpopstate = locationHandler;
// Modify the URL to match the route
window.route = route;

// Run route as soon as the page loads
locationHandler();
