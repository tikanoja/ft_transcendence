
// In your main JavaScript file or script that handles dynamic content loading
// document.addEventListener('input', (event) => {
//     if (event.target && event.target.id === 'confirm_password') {
//         check_same_input_registration_passwords();
//     }
// });


function check_same_input_registration_passwords() {
	var password = document.getElementById("password");
	var confirm = document.getElementById("confirm_password");
	if (password.value != confirm.value) {
		console.log("passwords don't match")
		password.setCustomValidity("Passwords must be matching");
		return false;
	} else {
		password.setCustomValidity("")
		return true;
	}
}