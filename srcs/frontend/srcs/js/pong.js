
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

let socket;
let gameNumber = -1;
let camera;
let p1_paddle;
let p2_paddle;
let ball;
let ground;
let keydownHandler, keyupHandler;
let render = true
let canvasFocused = true;

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
    socket = io.connect('https://' + window.location.hostname, {path: "/pong/socket.io"});  
    socket.on('connect', () => {
        // empty on purpose nothing todo
    });
    socket.on('error', (error) => {
        // empty on purpose nothing todo
    });
}

export const verifyUsername = () => {
        return new Promise((resolve, reject) => {
        const player1username = document.getElementById('player1username').value;
        const player2username = document.getElementById('player2username').value;
        const current_game_id = document.getElementById('current_game_id').value;
        const usernameString = player1username + "," + player2username + "," + current_game_id;
        
        socket.emit("username", usernameString);

        socket.on('setup_game', (data) => {
            const valuesArray = data.split(',');
            gameNumber = valuesArray[1];
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
			const canvasContainer = document.getElementById('canvasContainer');

            await verifyUsername()    
            startScreen.style.display = 'none';

            socket.emit('message', 'start_game,' + gameNumber);

            socket.on('start_game', (data) => {
                startScreen.remove();
                canvasContainer.style.display = 'block';
                const P1score = document.getElementById('P1Card');
                P1score.style.display = 'block';
                const P2score = document.getElementById('P2Card');
                P2score.style.display = 'block';
                const valuesArray = data.split(',')
                gameNumber = valuesArray[1]
                renderPongGame();
            });
    } catch (error) {
        console.error('Error loading script:', error);
    }
};

function loadGameOverScreen(data) {
    const winnerInfo = document.getElementById('winnerInfo');
    const gameOverScreen = document.getElementById('gameOverScreen');
    const canvasContainer = document.getElementById('canvasContainer');
    const scoreboard = document.getElementById('scoreboard');
    const P1score = document.getElementById('P1Card');
    const P2score = document.getElementById('P2Card');
    const player1username = document.getElementById('player1username').value;
    const player2username = document.getElementById('player2username').value;


    P1score.style.display = 'none';
    P2score.style.display = 'none';
    scoreboard.style.display = 'none';

    const valuesArray = data.split(',');
    const p1Score = parseInt(valuesArray[7]);
    const p2Score = parseInt(valuesArray[8]);

    let winnerText;
    if (p1Score > p2Score) {
        winnerText = `${player1username} wins!`;
    } else {
        winnerText = `${player2username} wins!`;
    }

    winnerInfo.textContent = winnerText;
    gameOverScreen.style.display = 'block';
    canvasContainer.style.display = 'none';
}

let previousP1Score = null;
let previousP2Score = null;

export const updateScoreboard = (p1Score, p2Score) => {
    const scoreLeftElement = document.getElementById('player1Score');
    const scoreRightElement = document.getElementById('player2Score');
    
    if (isNaN(p1Score) || isNaN(p2Score)) {
        return;
    }
    if (scoreLeftElement && scoreRightElement) {
        if (p1Score !== previousP1Score || p2Score !== previousP2Score) {
            scoreLeftElement.textContent = `${p1Score}`;
            scoreRightElement.textContent = `${p2Score}`;
            previousP1Score = p1Score;
            previousP2Score = p2Score;
        }
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

function create3DBall(ballRadiusScreen) {
    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load('../textures/checkers.jpg');
    return new THREE.Mesh(new THREE.SphereGeometry(ballRadiusScreen * 2, 10, 10), new THREE.MeshBasicMaterial({ map: texture }));
}

function createGround() {
    const textureLoader = new THREE.TextureLoader();
    const groundTexture = textureLoader.load('../textures/football_field.jpg');
    groundTexture.wrapS = groundTexture.wrapT = THREE.RepeatWrapping; // x, y
    groundTexture.repeat.set(1, 1); // 1, 1 means only one texture
   
    const groundMaterial = new THREE.MeshBasicMaterial({ map: groundTexture });
    const groundGeometry = new THREE.PlaneGeometry(1950, 1200);
    return new THREE.Mesh(groundGeometry, groundMaterial);
}

function setup3DScene(scene) {
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);

    addLighting(scene);
    p1_paddle = create3DPaddle(0xEF85A8);
    p2_paddle = create3DPaddle(0xC2C9C9);
    const sizeFactor = 0.2;
    const ballRadiusScreen = (25 * 2) * (Math.min(window.innerWidth / 1920, window.innerHeight / 1080)) * sizeFactor;
    
    ball = create3DBall(ballRadiusScreen);

    ground = createGround();
    ground.rotation.x = -Math.PI / 2; // Rotate the ground to be horizontal
    ground.position.y = -14; // To show whole ball the ground needs to go down a little bit

    // Set background texture
    const textureLoader = new THREE.TextureLoader();    
    textureLoader.load('../textures/space.jpg' , function(texture) { scene.background = texture;});

    scene.add(ground);
    scene.add(p1_paddle);
    scene.add(p2_paddle);
    scene.add(ball);
    p1_paddle.position.set(-100,  0, 0);
    p2_paddle.position.set(100, 0, 0);
    return { camera, p1_paddle, p2_paddle, ball };
}

function create3DPaddle(color) {
    let widthRatio = (20 * 2) / 1920
    let heightRatio = (90 * 2) / 1080
	let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;
	const sizeFactor = 0.7;

    let paddleWidth = (screenWidth * widthRatio) * sizeFactor;
    let paddleHeight = (screenHeight * heightRatio) * sizeFactor;
    let paddleZed = (0.30 * paddleHeight) * sizeFactor;

    const textureLoader = new THREE.TextureLoader();
    const fireTexture = textureLoader.load('../textures/fire.jpg');

    const materials = [
        new THREE.MeshBasicMaterial({ map: fireTexture }), // Front
        new THREE.MeshBasicMaterial({ map: fireTexture }), // Back
        new THREE.MeshBasicMaterial({ map: fireTexture }), // Top
        new THREE.MeshBasicMaterial({ map: fireTexture }), // Bottom
        new THREE.MeshBasicMaterial({ map: fireTexture }), // Right
        new THREE.MeshBasicMaterial({ map: fireTexture })  // Left
    ];

    const geometry = new THREE.BoxGeometry(paddleWidth, paddleZed, paddleHeight);
    return new THREE.Mesh(geometry, materials);
}

function updateGameState(data, p1_paddle, p2_paddle, ball) {
    let p1_paddle_y, p1_paddle_x, p2_paddle_y, p2_paddle_x, ball_x, ball_y, p1_score, p2_score;
    const min_visible_x = -1010;
    const max_visible_x = 1010;
    const min_visible_y = -586;
    const max_visible_y = 586;
    const valuesArray = data.split(',');

	if (valuesArray[0] == gameNumber){
	    ball_x = parseFloat(valuesArray[1]);
		ball_y = parseFloat(valuesArray[2]);
		p2_paddle_x = parseFloat(valuesArray[3]);
		p2_paddle_y = parseFloat(valuesArray[4]);
		p1_paddle_x = parseFloat(valuesArray[5]);
		p1_paddle_y = parseFloat(valuesArray[6]);
		p1_score = parseInt(valuesArray[7]);
		p2_score = parseInt(valuesArray[8]);

		ball_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[1]);
		ball_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[2]);
		p2_paddle_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[3]);
		p2_paddle_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[4]);
		p1_paddle_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[5]);
		p1_paddle_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[6]);
    
        p1_paddle.position.set(p1_paddle_x, 0, p1_paddle_y); 
        p2_paddle.position.set(p2_paddle_x, 0, p2_paddle_y); 
        ball.position.set(ball_x, 0, ball_y);

		updateScoreboard(p1_score, p2_score);
	}
}

let rotate_ball_turn = 0;
let ball_rotation_slowdown_factor = 2;

function animateBallRotation(ball) {
    if (rotate_ball_turn == 0) // Is it time to update ball rotation
    {
        if (!render)
            return; // If rendering is not active dont update ball
        // Define rotations for the ball
        const randomRotationX = Math.random() * Math.PI * 2;
        const randomRotationY = Math.random() * Math.PI * 2;
        const randomRotationZ = Math.random() * Math.PI * 2;

        // Apply rotations for the ball
        ball.rotation.x += randomRotationX;
        ball.rotation.y += randomRotationY;
        ball.rotation.z += randomRotationZ;
    }
    // These are related to slowning down the ball rotation
    rotate_ball_turn += 1;
    if (rotate_ball_turn >= ball_rotation_slowdown_factor)
        rotate_ball_turn = 0;
}

const AnimationController = {
    animationId: null,
    
    animate: function(scene, camera, renderer) {
        this.animationId = requestAnimationFrame(() => this.animate(scene, camera, renderer));
            animateBallRotation(ball);
        renderer.render(scene, camera);
    },
    
    stopAnimation: function() {
        socket.emit('message', 'stop_game,' + gameNumber);
        socket.on('disconnect', () => {
            // empty on purpose nothing todo
        });
        cancelAnimationFrame(this.animationId);
    },
    
    startAnimation: function(scene, camera, renderer)
    {
        this.animate(scene, camera, renderer);
    }
};

function removeEventListeners() {
    document.removeEventListener('keydown', keydownHandler);
    document.removeEventListener('keyup', keyupHandler);
}

function cleanUpScene(scene) {
    scene.remove(p1_paddle);
    scene.remove(p2_paddle);
    scene.remove(ball);
    scene.remove(ground);
}

function exit_game(data, scene)
{
    loadGameOverScreen(data);
    removeEventListeners();
    cleanUpScene(scene);
    canvasFocused = false;
}

function onWindowResize(camera, renderer, canvas) {

    const width = window.innerWidth - (window.innerWidth / 4);
    const height = window.innerHeight - (window.innerHeight / 4);
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    const canvasBounds = canvas.getBoundingClientRect();
    const P1score = document.getElementById('P1Card');
    const P2score = document.getElementById('P2Card');
    
    P1score.style.top = canvasBounds.top + 10 + 'px';
    P1score.style.left = canvasBounds.left + 100 + 'px';
    
    P2score.style.top = canvasBounds.top + 10 + 'px';
    P2score.style.left = canvasBounds.right - P2score.offsetWidth - 100 + 'px';
}

function setupEventListeners() {

    keydownHandler = (event) => {
        if (canvasFocused)
        {
            event.preventDefault();
            const moveDistance = 10;
            const rotateAngle = Math.PI / 36;
            switch (event.key) {
                case 'ArrowDown':
                    socket.emit('message', 'right_paddle_down,' + gameNumber);
                    break;
                case 'ArrowUp':
                    socket.emit('message', 'right_paddle_up,' + gameNumber);
                    break;
                case 's':
                    socket.emit('message', 'left_paddle_down,' + gameNumber);
                    break;
                case 'w':
                    socket.emit('message', 'left_paddle_up,' + gameNumber);
                    break;
                case 'r':
                    camera.position.x += moveDistance;
                    if (camera.position.x > -1000)
                        camera.position.x = -1000;
                    break;
                case 'f':
                    camera.position.x -= moveDistance;
                    if (camera.position.x < -1500)
                        camera.position.x = -1500;
                    break;
                case 't':
                    camera.position.y += moveDistance;
                    if (camera.position.y > 500)
                        camera.position.y = 500;
                    break;
                case 'g':
                    camera.position.y -= moveDistance;
                    if (camera.position.y < 50)
                        camera.position.y = 50;
                    break;
                case 'y':
                    camera.position.z += moveDistance;
                    if (camera.position.z > 1500)
                        camera.position.z = 1500;
                    break;
                case 'h':
                    camera.position.z -= moveDistance;
                    if (camera.position.z < 1050)
                        camera.position.z = 1050;
                    break;
                case 'u':
                    camera.rotation.x += rotateAngle;
                    if (camera.rotation.x < 0)
                        camera.rotation.x += (2 * Math.PI);
                    if (camera.rotation.x > 6.278732645827805)
                        camera.rotation.x = 6.278732645827805;
                    break;
                case 'j':
                    camera.rotation.x -= rotateAngle;
                    if (camera.rotation.x < 0)
                        camera.rotation.x += (2 * Math.PI);
                    if (camera.rotation.x < 5.755133870229507)
                        camera.rotation.x = 5.755133870229507;
                    break;
                case 'i':
                    camera.rotation.y += rotateAngle;
                    if (camera.rotation.y < 0)
                        camera.rotation.y += (2 * Math.PI);
                    if (camera.rotation.y > 5.952051587572457)
                        camera.rotation.y = 5.952051587572457;
                    break;
                case 'k':
                    camera.rotation.y -= rotateAngle;
                    if (camera.rotation.y < 0)
                        camera.rotation.y += (2 * Math.PI);
                    if (camera.rotation.y < 5.428452811974159)
                        camera.rotation.y = 5.428452811974159;
                    break;
                case 'o':
                    camera.rotation.z += rotateAngle;
                    if (camera.rotation.z < 0)
                        camera.rotation.z += (2 * Math.PI);
                    if (camera.rotation.z > 6.53237506803245)
                        camera.rotation.z = 6.53237506803245;
                    break;
                case 'l':
                    camera.rotation.z -= rotateAngle;
                    if (camera.rotation.z < 0)
                        camera.rotation.z += (2 * Math.PI);
                    if (camera.rotation.z < 5.57244397943557)
                        camera.rotation.z = 5.57244397943557;
                    break;
                default:
                    break;
            }
        }
    }

    keyupHandler = (event) => {
        event.preventDefault();
            if (event.key == 'ArrowDown')
                socket.emit('message', 'right_paddle_down_release,' + gameNumber);
            if (event.key  == 'ArrowUp')
                socket.emit('message', 'right_paddle_up_release,' + gameNumber);
            if (event.key  == 's')
                socket.emit('message', 'left_paddle_down_release,' + gameNumber);
            if (event.key  == 'w')
                socket.emit('message', 'left_paddle_up_release,' + gameNumber);
    };

    document.addEventListener('keyup', keyupHandler);
    document.addEventListener('keydown', keydownHandler);
}

///Main function for setting up and animating game
export const renderPongGame = () => {
    const scene = new THREE.Scene();

    const existingCanvas = document.getElementById('pongCanvas');
    if (existingCanvas) {
        existingCanvas.remove();
    }

    const renderer = new THREE.WebGLRenderer();
    const pixelRatio = window.devicePixelRatio;
    renderer.setPixelRatio(pixelRatio);
	renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4));
    renderer.domElement.id = 'pongCanvas'; 
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    

    const canvas = renderer.domElement;
    canvas.setAttribute('tabindex', '0');

    canvas.addEventListener('focus', () => {
        canvasFocused = true;
    });
    
    canvas.addEventListener('blur', () => {
        canvasFocused = false;
    });


    ({ camera, p1_paddle, p2_paddle, ball} = setup3DScene(scene));
    camera.position.set(-1100, 300, 1100);
    camera.lookAt(0, 0, 0);

    const canvasBounds = canvas.getBoundingClientRect();
    const P1score = document.getElementById('P1Card');
    const P2score = document.getElementById('P2Card');
    
    P1score.style.position = 'absolute';
    P1score.style.top = canvasBounds.top + 10 + 'px';
    P1score.style.left = canvasBounds.left + 100 + 'px';
    
    P2score.style.position = 'absolute';
    P2score.style.top = canvasBounds.top + 10 + 'px';
    P2score.style.left = canvasBounds.right - P2score.offsetWidth - 100 + 'px';

    window.addEventListener('resize',() => onWindowResize(camera, renderer, canvas));


    socket.on('state', (data) => {
        updateGameState(data, p1_paddle, p2_paddle, ball)
    });

    socket.on('endstate', (data) => {
        exit_game(data, scene)
        AnimationController.stopAnimation();
    });
    
    setupEventListeners();

    if (render) {
        AnimationController.startAnimation(scene, camera, renderer);
    }
    else
    {
        AnimationController.stopAnimation();
    }
};
