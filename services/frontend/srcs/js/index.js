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
    xhr.open('GET', 'http://localhost:8000/' + endpoint, true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = xhr.responseText;
                if (callback) {
                    callback(response);
                }
            } else {
                console.error('Error:', xhr.statusText);
            }
        }
    };
    xhr.send();
}
// index.js:38     GET http://localhost:8000/pong/get_game_state/ net::ERR_INSUFFICIENT_RESOURCES


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
		case "ArrowUp": 
		case "ArrowDown":  
			event.preventDefault();
			 break;
		default:
			break;
				
		};
    }
);

function testButtonClickHandler(){
    sendRequest('pong/increase_number/', function (response) {
        console.log("The thing works");
    });
}

function increaseButtonClickHandler() {
    sendRequest('pong/increase_number/', function (response) {
        console.log(response);
    });
}


function decreaseButtonClickHandler() {
    sendRequest('pong/decrease_number/', function (response) {
        console.log(response);
    });
};

const get_game_state = () => {
    return new Promise((resolve, reject) => {
        sendRequest('pong/get_game_state/', function(response) {
            try {
                const responseData = JSON.parse(response);
                console.log("from index, game_state: ", responseData)
                const p1_pos = responseData.p1_pos;
                const p2_pos = responseData.p2_pos;
                const p1_pos_y = responseData.p1_pos_y;
                const p2_pos_y = responseData.p2_pos_y;
                const p1_score = responseData.p1_score;
                const p2_score = responseData.p2_score;
                const game_progress = responseData.game_;
                resolve({ game_progress, p1_pos, p2_pos, p1_score, p2_score, p1_pos_y, p2_pos_y});
            } catch (error) {
                console.error('Error parsing JSON:', error);
                reject(error);
            }
        });
    });
};


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