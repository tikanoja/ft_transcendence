                                                                                                                                                                            // // Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

// //TODO:the size of paddles, ball and their positioning MUST BE DYNAMIC!
// //TODO: A better looking start screen the also shows user name, and opponent name
// //TODO: Make lighting better
let socket;
let gameNumber = -1;

export const loadScript = () => {
    return new Promise((resolve, reject) => {
        var script = document.createElement('script');
        script.src = "https://cdn.socket.io/4.7.5/socket.io.min.js"
        script.integrity = "sha384-2huaZvOR9iDzHqslqwpR87isEmrfxqyWOF7hr7BY6KG0+hVKLoEXMPUJw3ynWuhO"
        script.crossOrigin = "anonymous"
        document.head.appendChild(script);
        script.onload = function() {
            console.log(script.src + ' loaded');
            resolve();
        };
        script.onerror = function(error) {
            reject(error);
        };
    });
}


function connectWebSocket() {
    socket = io.connect('https://' + window.location.hostname);
	console.log(window.location.hostname)
    socket.on('connect', () => {
    });
    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
}

export const verifyUsername = () => {
    return new Promise((resolve, reject) => {
        const player1username = document.getElementById('player1username').value;
        const player2username = document.getElementById('player2username').value;
        const current_game_id = document.getElementById('current_game_id').value;
        const usernameString = player1username + "," + player2username + "," + current_game_id;
        
        console.log('usernameString id: ', usernameString);
        socket.emit("username", usernameString);

        socket.on('setup_game', (data) => {
            console.log("in setup game");
            const valuesArray = data.split(',');
            gameNumber = valuesArray[1];
            console.log("after setup game: ", gameNumber);
            resolve(gameNumber);
        });

        socket.on('error', (error) => {
            reject('Error verifying username:', error);
        });
    });
};

export const startScreen = async () => {
    try {
			await loadScript();
			connectWebSocket();
            
			const startScreen = document.getElementById('startScreen');
			const playButton = document.getElementById('playButton');
			const canvasContainer = document.getElementById('canvasContainer');
			const styleCheckbox = document.getElementById('styleCheckbox');
			let is3DGraphics = false;
            

            await verifyUsername()
            console.log("after verify: ", gameNumber);
            
            playButton.addEventListener('click', () => {
                console.log("in the click listener")
                startScreen.style.display = 'none';
                canvasContainer.style.display = 'block';
                is3DGraphics = styleCheckbox.checked;

                // # DONT FORGET to maybe insert to here to get permission from django to start the game
                socket.emit('message', 'start_game,' + gameNumber);

                socket.on('start_game', (data) => {
                    console.log("start game was called")
                    startScreen.style.display = 'none';
                    canvasContainer.style.display = 'block';
                    console.log(data)
                    const valuesArray = data.split(',')
                    gameNumber = valuesArray[1]
                    renderPongGame(is3DGraphics, gameNumber);
                });
            });
    } catch (error) {
        console.error('Error loading script:', error);
    }
};

// Define the gameOverScreen function within the same scope
function loadGameOverScreen(data) {
    const winnerInfo = document.getElementById('winnerInfo');
    const gameOverScreen = document.getElementById('gameOverScreen');
    
    const valuesArray = data.split(',');
    const p1Score = parseInt(valuesArray[8]);
    const p2Score = parseInt(valuesArray[7]);

    let winnerText;
    if (p1Score > p2Score) {
        winnerText = "Player 1 wins!";
    } else if (p1Score < p2Score) {
        winnerText = "Player 2 wins!";
    } else {
        winnerText = "It's a tie!";
    }

    winnerInfo.textContent = winnerText;
    gameOverScreen.style.display = 'block';
    canvasContainer.style.display = 'none';
}

let previousP1Score = null;
let previousP2Score = null;

export const updateScoreboard = (p1Score, p2Score) => {
    const scoreLeftElement = document.querySelector('.score-left');
    const scoreRightElement = document.querySelector('.score-right');
    
    if (isNaN(p1Score) || isNaN(p2Score)) {
        return;
    }
    if (scoreLeftElement && scoreRightElement) {
        if (p1Score !== previousP1Score || p2Score !== previousP2Score) {
            scoreLeftElement.textContent = `P1 SCORE: ${p1Score}`;
            scoreRightElement.textContent = `P2 SCORE: ${p2Score}`;
            previousP1Score = p1Score;
            previousP2Score = p2Score;
        }
    } else {
        console.error('Scoreboard elements not found.');
    }
};

function addLighting(scene) {
    let color = 0xFFFFFF;
    let intensity = 8;
    let light = new THREE.DirectionalLight(color, intensity);
    light.position.set(15, 35, 20);
    light.target.position.set(15, 29, 15);
    const amb_light = new THREE.AmbientLight(0xFFFFFF);
    scene.add(light);
    scene.add(light.target);
    scene.add(amb_light);
}

function setup2DScene(scene) {
    const camera = new THREE.OrthographicCamera(window.innerWidth / -2, window.innerWidth / 2, window.innerHeight / 2, window.innerHeight / -2, 1, 1000);
    // scene.add(camera);
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(0, 0, 1);
    scene.add(directionalLight);

    const p1_paddle = create2DPaddle(0x808080); // Old-school TV Pong grey
    const p2_paddle = create2DPaddle(0x808080);


    const sizeFactor = 0.2;
    const ballRadiusScreen = (25 * 2) * (Math.min(window.innerWidth / 1920, window.innerHeight / 1080)) * sizeFactor;
    const ball = new THREE.Mesh(new THREE.PlaneGeometry(ballRadiusScreen * 2, ballRadiusScreen * 2), new THREE.MeshStandardMaterial({ color: 0x808080 }));
    
    scene.add(p1_paddle);
    scene.add(p2_paddle);
    scene.add(ball);

    return { camera, p1_paddle, p2_paddle, ball };
}

function setup3DScene(scene) {
    let p1_paddle, p2_paddle, ball;
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    addLighting(scene);
    p1_paddle = create3DPaddle(0xEF85A8);
    p2_paddle = create3DPaddle(0xC2C9C9);
    ball = new THREE.Mesh(new THREE.SphereGeometry(5, 10, 6), new THREE.MeshPhongMaterial({color: 0xff00ff}))
    scene.add(p1_paddle);
    scene.add(p2_paddle);
    scene.add(ball);
    p1_paddle.position.set(-100,  0, 0);
    p2_paddle.position.set(100, 0, 0);

    return camera;
}


function create2DPaddle(color) {
    // Adjust the dimensions of the paddle geometry based on the ratios
    let widthRatio = (20 * 2) / 1920
    let heightRatio = (90 * 2) / 1080
	let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;
	const sizeFactor = 0.7;


    let paddleWidth = (screenWidth * widthRatio) * sizeFactor;
    let paddleHeight = (screenHeight * heightRatio) * sizeFactor;

    const geometry = new THREE.BoxGeometry(paddleWidth, paddleHeight, 0);
    const material = new THREE.MeshStandardMaterial({ color });
    return new THREE.Mesh(geometry, material);
}

// Function to create a 3D paddle
function create3DPaddle(color) {
    const geometry = new THREE.BoxGeometry(5, 20, 5);
    const material = new THREE.MeshPhongMaterial({ color });
    return new THREE.Mesh(geometry, material);
}

export const renderPongGame = (is3DGraphics, gameNumber) => {
	console.log("GAME IS RENDERING")
    const scene = new THREE.Scene();
    let camera;
    // Remove any existing canvas
    const existingCanvas = document.getElementById('pongCanvas');
    if (existingCanvas) {
        existingCanvas.remove();
    }

    const renderer = new THREE.WebGLRenderer();
    const pixelRatio = window.devicePixelRatio;
    renderer.setPixelRatio(pixelRatio);
	renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4));
    renderer.domElement.id = 'pongCanvas'; // Set an id for the new canvas
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    let p1_paddle, p2_paddle, ball;
    if (is3DGraphics) {
        camera = setup3DScene(scene);
    } else {
        ({ camera, p1_paddle, p2_paddle, ball } = setup2DScene(scene));

    }
    let render = true
	let min_visible_x, max_visible_x, min_visible_y, max_visible_y;
	calculateVisibleArea();

    function calculateVisibleArea() {  //TODO: potentially needs to be calculated differently for perspective, currently functions with 
        const half_width = window.innerWidth / 2;
        const half_height = window.innerHeight / 2;
        min_visible_x = camera.position.x - half_width;
        max_visible_x = camera.position.x + half_width;
        min_visible_y = camera.position.y - half_height;
        max_visible_y = camera.position.y + half_height;
    }


    camera.position.set(0, 0, 100);
    let p1_paddle_y, p1_paddle_x, p2_paddle_y, p2_paddle_x, ball_x, ball_y, p1_score, p2_score;

    function updateGameState(data) {
        const valuesArray = data.split(',');

		if (valuesArray[0] == gameNumber){
				ball_x = parseFloat(valuesArray[1]);
				ball_y = parseFloat(valuesArray[2]);
				p2_paddle_x = parseFloat(valuesArray[3]);
				p2_paddle_y = parseFloat(valuesArray[4]);
				p1_paddle_x = parseFloat(valuesArray[5]);
				p1_paddle_y = parseFloat(valuesArray[6]);
				p2_score = parseInt(valuesArray[7]);
				p1_score = parseInt(valuesArray[8]);

				ball_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[1]);
				ball_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[2]);
				p2_paddle_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[3]);
				p2_paddle_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[4]);
				p1_paddle_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[5]);
				p1_paddle_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[6]);
				p1_paddle.position.set(p1_paddle_x, p1_paddle_y, 0); 
				p2_paddle.position.set(p2_paddle_x, p2_paddle_y, 0); 
				ball.position.set(ball_x,  ball_y, 0);
				updateScoreboard(p1_score, p2_score);
			}
		}

    socket.on('state', (data) => {
        updateGameState(data)
    });

	function exit_game(data)
	{
        updateGameState(data)
        loadGameOverScreen(data)
		stopAnimation()

	}

	socket.on('endstate', (data) => {
        exit_game(data)
    });

    function animate() {
        if (render) {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        } else {
            stopAnimation();
        }
    }
	

    //THESE ARE INVERTED DUE TO COORD DIFFERENCE
	document.addEventListener('keydown', (event) => {
		event.preventDefault();
		if (event.key == 'ArrowUp')
		{
			socket.emit('message', 'right_paddle_down,' + gameNumber);
		}
        if (event.key  == 'ArrowDown')
		{
			socket.emit('message', 'right_paddle_up,' + gameNumber);
		}
        if (event.key  == 'w')
		{
			socket.emit('message', 'left_paddle_down,' + gameNumber);
		}
        if (event.key  == 's')
		{
			socket.emit('message', 'left_paddle_up,' + gameNumber);
		}
			if (event.key == 'c')
		{
			socket.emit('message', 'stop_game,' + gameNumber);
			render = false;
		}
    });

    document.addEventListener('keyup', (event) => {
		event.preventDefault();
		if (event.key == 'ArrowUp')
			socket.emit('message', 'right_paddle_down_release,' + gameNumber);
        if (event.key  == 'ArrowDown')
			socket.emit('message', 'right_paddle_up_release,' + gameNumber);
        if (event.key  == 'w')
			socket.emit('message', 'left_paddle_down_release,' + gameNumber);
        if (event.key  == 's')
			socket.emit('message', 'left_paddle_up_release,' + gameNumber);
    });


    let animationId;

    function startAnimation() {

        animationId = requestAnimationFrame(animate);
        animate();}

		function stopAnimation() {
		socket.emit('message', 'stop_game,' + gameNumber);
		socket.on('disconnect', () => {
			console.log('Disconnected from server');
		});
        cancelAnimationFrame(animationId);
        render = true
    }
    if (render)
    {
        startAnimation();
    }
};
