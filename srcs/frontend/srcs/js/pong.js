// // Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

// //TODO:the size of paddles, ball and their positioning MUST BE DYNAMIC!
// //TODO: A better looking start screen the also shows user name, and opponent name
// //TODO: Make lighting better
// //TODO: boundrys working, potentially a canvas boarder

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

let socket;

function connectWebSocket() {
    socket = io.connect('https://' + window.location.hostname);
	console.log(window.location.hostname)
    socket.on('connect', () => {
    });
    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
}

export const startScreen = async () => {
    try {
			await loadScript();
			connectWebSocket();
            
			const startScreen = document.getElementById('startScreen');
			const playButton = document.getElementById('playButton');
			const canvasContainer = document.getElementById('canvasContainer');
			const styleCheckbox = document.getElementById('styleCheckbox');
			let is3DGraphics = false;

			playButton.addEventListener('click', () => {
				startScreen.style.display = 'none';
				canvasContainer.style.display = 'block';
				
				is3DGraphics = styleCheckbox.checked;
				socket.emit('message', 'games_running');
                socket.on('games_running_response', (data) => {
                    const gameStates = data.split(',').slice(1);
                    const areAllZero = gameStates.every(state => state.trim() === '0');
                    if (areAllZero == true)
                        socket.emit('message', 'start_background_loop');
                });
				socket.emit('message', 'start_game,0'); //TODO: need to check how this will decide what number??
				
				let gameNumber = 0
				renderPongGame(is3DGraphics, gameNumber);
        });
    } catch (error) {
        console.error('Error loading script:', error);
    }
};

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



window.addEventListener('resize', function() {
    var canvasContainer = document.getElementById('canvasContainer');
    var scoreboard = document.getElementById('scoreboard');
    
    var canvasWidth = canvasContainer.offsetWidth;
    var scoreboardWidth = scoreboard.offsetWidth;
    
    if (canvasWidth < scoreboardWidth) {
        scoreboard.style.flexDirection = 'column'; // Stack elements vertically
        scoreboard.style.alignItems = 'center'; // Center elements vertically
    } else {
        scoreboard.style.flexDirection = 'row'; // Reset to default row layout
        scoreboard.style.alignItems = 'initial'; // Reset alignment
    }
});

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

    // Calculate ball radius based on screen width
    const sizeFactor = 0.5; // Adjust this value to make the ball slightly smaller while keeping the ratio
    const ballRadiusScreen = 25 * (Math.min(window.innerWidth / 1920, window.innerHeight / 1080)) * sizeFactor;
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
    let widthRatio = 20 / 1920
    let heightRatio = 90 / 1080
	let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;
	

    const ballRadiusScreen = 25 * (Math.min( window.innerWidth / 1920, screenHeight / 1080));

    
    let paddleWidth = screenWidth * widthRatio;
    let paddleHeight = screenHeight * heightRatio;

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
    const scene = new THREE.Scene();
    let camera;

    const renderer = new THREE.WebGLRenderer();
    const pixelRatio = window.devicePixelRatio;
    renderer.setPixelRatio(pixelRatio);
	renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4));
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    let p1_paddle, p2_paddle, ball; //TODO: take into account the paddle width and height?
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
        // let game_state_number = valuesArray[0];
        console.log(valuesArray)
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

    socket.on('state', (data) => {
        updateGameState(data)

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
			socket.emit('message', 'right_paddle_down,' + gameNumber);
        if (event.key  == 'ArrowDown')
			socket.emit('message', 'right_paddle_up,' + gameNumber);
        if (event.key  == 'w')
			socket.emit('message', 'left_paddle_down,' + gameNumber);
        if (event.key  == 's')
			socket.emit('message', 'left_paddle_up,' + gameNumber);
		if (event.key == 'c')
			render = false;
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
        socket.emit('message', 'games_running');
        socket.on('games_running_response', (data) => {
            const gameStates = data.split(',').slice(1);
            const areAllZero = gameStates.every(state => state.trim() === '0');
            console.log('Games still running?', data);
            
            if (areAllZero == true)
            console.log('stopping loop');
                socket.emit('message', 'stop_background_loop');
            
                socket.on('disconnect', () => {
                console.log('Disconnected from server');
            });
        });

        cancelAnimationFrame(animationId);
        render = true
    }
    if (render)
    {
        startAnimation();
    }
};
