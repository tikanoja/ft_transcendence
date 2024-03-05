// Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

// import { increaseButtonClickHandler, decreaseButtonClickHandler } from './buttonHandlers.js';
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
    
    playButton.addEventListener('click', () => {
        
        startScreen.style.display = 'none'; // Hide the start screen
        canvasContainer.style.display = 'block';
        renderPongGame(is3DGraphics); 
    });

    styleCheckbox.addEventListener('change', (event) => {
        console.log("changed    ", is3DGraphics);
        is3DGraphics = event.target.checked; 
    });
};

// Modify the updateScoreboard function to call retrieveButtonClickHandler
export const updateScoreboard = () => {
    retrieveButtonClickHandler().then(data => {
        const p1ScoreElement = document.getElementById('score-left');
        const p2ScoreElement = document.getElementById('score-right');
        p1ScoreElement.textContent = `Player 1: ${data.p1Score}`;
        p2ScoreElement.textContent = `Player 2: ${data.p2Score}`;
    }).catch(error => {
        console.error('Error updating scoreboard:', error);
    });
};

// // Function to handle fetching scoreboard data from the API
// function retrieveButtonClickHandler() {
//     fetch('pong/get_number/') // Assuming this is the correct API endpoint
//     .then(data => {
//         // Update the scoreboard numbers on the webpage with the parsed data
//         const p1ScoreElement = document.getElementById('score-left'); // Assuming you have elements with IDs for displaying scores
//         const p2ScoreElement = document.getElementById('score-right');
//         p1ScoreElement.textContent = `Player 1: ${data.p1Score}`; // Assuming the API response contains data for player 1's score
//         p2ScoreElement.textContent = `Player 2: ${data.p2Score}`; // Assuming the API response contains data for player 2's score
//     })
//     .catch(error => {
//         console.error('Error fetching scoreboard data:', error);
//     });
// }




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

   let keyDown = false;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight);
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    const directionalLight = addLighting(scene); //
   
    
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
        // updateScoreboard();
        renderer.render(scene, camera);
    }

    document.addEventListener('keydown', (event) => {
        if (!keyDown) {
            keyDown = true;

            const speed = 3.0;
            const moveP1 = () => {
                switch (event.key) {
                    case 'ArrowUp':
                        increaseButtonClickHandler();
                        p1_paddle.position.y += speed; // Move up
                        break;
                    case 'ArrowDown':
                        decreaseButtonClickHandler();
                        p1_paddle.position.y -= speed; // Move down
                        break;
                }
            };
            const moveP2 = () => {
                switch (event.key) {
                    case 'w':
                        increaseButtonClickHandler();
                        p2_paddle.position.y += speed; // Move up
                        break;
                        case 's':
                        decreaseButtonClickHandler();
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
