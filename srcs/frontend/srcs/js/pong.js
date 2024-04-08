// // Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';
// import { start_game_loop, stop_game_loop, start_game, stop_game, left_paddle_up, left_paddle_up_release , left_paddle_down, left_paddle_down_release , right_paddle_up, right_paddle_up_release , right_paddle_down, right_paddle_down_release, get_game_state, get_games_running} from './index.js'
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
    // Register event handlers
    socket.on('connect', () => {
        socket.emit('message', 'hello from JS');
    });
    //TODO: this happens to get game state
    socket.on('message', (data) => {
        console.log('Message from server:', data);
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

            socket.emit('message', 'start_background_loop');
            renderPongGame(is3DGraphics);
        });

    } catch (error) {
        console.error('Error loading script:', error);
    }
};

	
export const updateScoreboard = (p1Score, p2Score) => {
    const scoreLeftElement = document.querySelector('.score-left');
    const scoreRightElement = document.querySelector('.score-right');

    if (scoreLeftElement && scoreRightElement) {
        scoreLeftElement.textContent = `P1 SCORE: ${p1Score}`;
        scoreRightElement.textContent = `P2 SCORE: ${p2Score}`;
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
    //const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const camera = new THREE.OrthographicCamera(window.innerWidth / - 2, window.innerWidth / 2, window.innerHeight / 2, window.innerHeight / - 2, 1, 1000);
    // scene.add( camera );
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(0, 0, 1);
    scene.add(directionalLight);

    const p1_paddle = create2DPaddle(0x808080); // Old-school TV Pong grey
    const p2_paddle = create2DPaddle(0x808080);
    const ball = new THREE.Mesh(new THREE.PlaneGeometry(15, 15), new THREE.MeshStandardMaterial({color: 0x808080}));
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
    p1_paddle.position.set(-100,  0, 0); // this will be set from API call as well
    p2_paddle.position.set(100, 0, 0);

    return camera;
}



function create2DPaddle(color) {
    // Adjust the dimensions of the paddle geometry based on the ratios
    let widthRatio = 20 / 1920
    let heightRatio = 90 / 1080

	let screenWidth = window.innerWidth;
    let screenHeight = window.innerHeight;

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

export const renderPongGame = (is3DGraphics) => {
    const scene = new THREE.Scene();
    let camera;

    const renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4));
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
    ///set up is completed by this point, game is now rendering/////
    // var clock = new THREE.Clock();
    // var time = 0;
    // var delta = 0;

    camera.position.set(0, 0, 100);
    let p1_paddle_y, p1_paddle_x, p2_paddle_y, p2_paddle_x, ball_x, ball_y, p1_score, p2_score;

    function updateGameState() {
		//TODO: this happens to get game state, does this have to happen live or in updateGameState okay?, definately a better way to parse these?
		socket.on('state', (data) => {
			console.log('State from server:', data);
			const parsedData = JSON.parse(data);
		    const valuesString = parsedData.status.split(': ')[1];
		    const valuesArray = valuesString.split(',');

		    ball_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[0]);
		    ball_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[1]);
		    p2_paddle_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[2]);
		    p2_paddle_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[3]);
		    p1_paddle_x = min_visible_x + (max_visible_x - min_visible_x) * parseFloat(valuesArray[4]);
		    p1_paddle_y = min_visible_y + (max_visible_y - min_visible_y) * parseFloat(valuesArray[5]);
			p2_score = parseInt(valuesArray[6]);
			p1_score = parseInt(valuesArray[7]);

			p1_paddle.position.set(p1_paddle_x, p1_paddle_y, 0); 
			p2_paddle.position.set(p2_paddle_x, p2_paddle_y, 0); 
			ball.position.set(ball_x,  ball_y, 0);
			console.log('values array', valuesArray);
			updateScoreboard(p1_score, p2_score);
		});
    }

    // Update the game state 50 times per second
    // const gameStateInterval = setInterval(updateGameState, 1000 / 50)

    // Update the game state  times per second for debugging THIS IS FOR DEBUGGING ONLY
    const gameStateInterval = setInterval(updateGameState, 3000);


    function animate() {
        requestAnimationFrame(animate);
        if (render == false)
        {
            stopAnimation();
			//TODO: this happens on exit from game
			socket.on('disconnect', () => {
				console.log('Disconnected from server');
			});
			//TODO: this is the background loop, this needs to be run if 0 games are running AFTER stopping the game Orthographic Camera
			stop_game_loop();

        }
        else
        {
            renderer.render(scene, camera);
        }
    }
    //THESE ARE INVERTED DUE TO COORD DIFFERENCE
	document.addEventListener('keydown', (event) => {
		event.preventDefault();
		if (event.key == 'ArrowUp')
        {
			socket.emit('message', 'right_paddle_down');
        }
        if (event.key  == 'ArrowDown')
        {
			socket.emit('message', 'right_paddle_up');
        }
        if (event.key  == 'w')
        {
			socket.emit('message', 'left_paddle_down');
        }
        if (event.key  == 's')
        {
			socket.emit('message', 'left_paddle_up');
        }
		if (event.key == 'c') {
			render = false;
		}
    });

    document.addEventListener('keyup', (event) => {
		event.preventDefault();
		if (event.key == 'ArrowUp')
        {
			socket.emit('message', 'right_paddle_down_release');
        }
        if (event.key  == 'ArrowDown')
        {
			socket.emit('message', 'right_paddle_up_release');
        }
        if (event.key  == 'w')
        {
			socket.emit('message', 'left_paddle_down_release');
        }
        if (event.key  == 's')
        {
			socket.emit('message', 'left_paddle_up_release');
        }

    });


    let animationId;

    function startAnimation() {

        animationId = requestAnimationFrame(animate);
        animate();
    }

		function stopAnimation() {

        //TODO: this would need to take into account which game number this is?
        stop_game().then(response => {
            console.log('response from stop_game', response);
            
        }).catch(error => {
            console.error('Error with stopping game:', error);
        });

        //TODO: this would be depended on whether there were other games running, if there are it wont run "game running call"
        stop_game_loop().then(response => {
            console.log('response from stop_game_loop', response);
            
        }).catch(error => {
            console.error('Error with stopping game:', error);
        });

        clearInterval(gameStateInterval);
        cancelAnimationFrame(animationId);
        render = true
    }
    if (render)
    {
        startAnimation();
    }
};
