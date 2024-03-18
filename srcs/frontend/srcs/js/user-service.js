
// function loginButtonClickHandler(event) {
//     event.preventDefault();
//     console.log("sending loqin request!");

//     var loginData = {};
//     loginData["username"] = document.getElementById('usernameLogin').value;
//     loginData["password"] = document.getElementById('passwordLogin').value;

//     var endpoint = '/user/login_user/';
//     sendRequest(endpoint, loginData, (response) => {
//         console.log('Received response:', response);
//     });
// }

// function usernameButtonClickHandler(event) {
//     event.preventDefault();
//     console.log("requesting username!");

//     var endpoint = 'http://localhost:8001/user/get_current_username/'
//     sendRequest(endpoint, null, (response) => {
//         console.log('Received response:', response);
//     });
// }

// function logoutButtonClickHandler(event) {
//     event.preventDefault();
//     console.log("requesting logout!");

//     var endpoint = '/user/logout/';
//     sendRequest(endpoint, null, (response) => {
//         console.log('Received response:', response);
//     });
// }

// const submitRegistrationHandler = async (event) => {
//     event.preventDefault();
//     const formData = new FormData(event.target);

//     const html = await fetch('/user/register/', {
//         method: 'POST',
//         body: formData
//     }).then((response) => response.text());

//     document.getElementById("content").innerHTML = html;
// 	document.title = "Registration | Pong";
// 	document.querySelector('meta[name="description"]').setAttribute("content", "Registration");
//     updateEventListeners();
// }

// function loginFormHandler (event) {
//     event.preventDefault();
//     console.log("in loginFormHandler")
//     const formData = new FormData(event.target);

// 	response = sendPostRequest('/user/login', formData);
// 	html = response.text();
// 	if (response.ok) {
// 		// stay on this page, display the content again
// 		document.getElementById("content").innerHTML = html;
// 		document.title = "Login | Pong";
// 		document.querySelector('meta[name="description"]').setAttribute("content", "Login");
// 		updateEventListeners();
// 	}
// 	else if (response.status >= 300 && response.status < 400) {
// 		// do we display content and handle routing from here?
// 		// or change routing to trigger the next request
// 		// redirect_location = response.headers.get('location')
// 		// routeRedirect(redirect_location)
// 		routeRedirect('/play')
// 	}
// 	else {
// 		console.log("Response status: ", response.status)
// 		// some 400 or 500 code probably, show the error that was sent?
// 	}
// }