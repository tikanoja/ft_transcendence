// Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';


//TODO: seperate into 2 scene creation functions that allow for the 2d scene to render with different lights and cameras.
//TODO:the size of paddles, ball and their positioning MUST BE DYNAMIC!
//TODO: A better looking start screen the also shows user name, and opponent name
//TODO: center line for court look
//TODO: visable scoreboard with API calls
//TODO: Make lighting better
//TODO: boundrys working, potentially a canva boarder



let is3DGraphics = false; // Default to 3D graphics

export const startScreen = () => {
    const startScreen = document.getElementById('startScreen');
    const playButton = document.getElementById('playButton');
    const canvasContainer = document.getElementById('canvasContainer');
    const styleCheckbox = document.getElementById('styleCheckbox');
    const scoreboard = document.getElementById('styleCheckbox');
    
    playButton.addEventListener('click', () => {
        
        startScreen.style.display = 'none'; // Hide the start screen
        canvasContainer.style.display = 'block'; // Show the game canvas
        scoreboard.style.display = 'block';
     
        renderPongGame(is3DGraphics); // Start the game with selected graphics option
    });

    styleCheckbox.addEventListener('change', (event) => {
        console.log("changed    ", is3DGraphics);
        is3DGraphics = event.target.checked; 
    });
};

export const renderPongGame = (is3DGraphics) => {
    
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

    var p1_score = 0;
    var p2_score = 0;

    // <div id=”scoreboard”>Player 1:  &emsp; Player 2: 0</div>
    // sendRequest('pong/get_number/', function (response) {
    //     console.log('Current number:', response.number);
    // })
    document.getElementById("scoreboard").innerHTML = "Player 1: " + p1_score + " &emsp; SCORE: " + p2_score; 
    
    let keyDown = false;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    const directionalLight = addLighting(scene);

    function create2DPaddle(color) {
        const geometry = new THREE.BoxGeometry(5, 20, 1);
        const material = new THREE.MeshStandardMaterial({ color });
        return new THREE.Mesh(geometry, material);
    }

    // Function to create a 3D paddle
    function create3DPaddle(color) {
        const geometry = new THREE.BoxGeometry(5, 20, 5);
        const material = new THREE.MeshPhongMaterial({ color });
        return new THREE.Mesh(geometry, material);
    }

    
    let p1_paddle, p2_paddle, ball;
    console.log(is3DGraphics);
    if (is3DGraphics) {
        p1_paddle = create3DPaddle(0xEF85A8);
        p2_paddle = create3DPaddle(0xC2C9C9);
        ball = new THREE.Mesh(new THREE.SphereGeometry(5, 10, 6), new THREE.MeshPhongMaterial({color: 0xff00ff}))
    } else {
        p1_paddle = create2DPaddle(0x808080); // Old-school TV Pong grey
        p2_paddle = create2DPaddle(0x808080); 
        ball = new THREE.Mesh(new THREE.PlaneGeometry(5, 5), new THREE.MeshStandardMaterial({color: 0x808080}));
    }
    
    scene.add(p1_paddle);
    scene.add(p2_paddle);
    scene.add(ball);
    // Set the positions of the paddles
    p1_paddle.position.set(-100,  0, 0);
    p2_paddle.position.set(100, 0, 0);


    var clock = new THREE.Clock();
    var time = 0;
    var delta = 0;


    camera.position.z = 200;

;

    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }

    document.addEventListener('keydown', (event) => {
        if (!keyDown) {
            keyDown = true;

            const speed = 3.0;
            const moveP1 = () => {
                switch (event.key) {
                    case 'ArrowUp':
                        p1_paddle.position.y += speed; // Move up
                        break;
                    case 'ArrowDown':
                        p1_paddle.position.y -= speed; // Move down
                        break;
                }
            };
            const moveP2 = () => {
                switch (event.key) {
                    case 'w':
                        p2_paddle.position.y += speed; // Move up
                        break;
                    case 's':
                        p2_paddle.position.y -= speed; // Move down
                        break;
                }
            };

            const moveLoop = () => {
                if (keyDown) {
                    moveP1();
                    moveP2();
                    requestAnimationFrame(moveLoop);
                }
            };

            moveLoop();
        }
    });
    document.addEventListener('keyup', () => {
        keyDown = false;
    });

    let animationId;

    function startAnimation() {

        animationId = requestAnimationFrame(animate);
        animate();
    }

    function stopAnimation() {
        cancelAnimationFrame(animationId);
    }

    document.addEventListener('pagechange', (event) => {
        const page = event.detail.page;
        if (page != '/test') {
            stopAnimation();
        }
    });
    startAnimation();
};
