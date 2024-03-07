// Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

//TODO:the size of paddles, ball and their positioning MUST BE DYNAMIC!
//TODO: A better looking start screen the also shows user name, and opponent name
//TODO: center line for court look
//TODO: visable scoreboard with API calls
//TODO: Make lighting better
//TODO: boundrys working, potentially a canvas boarder



let is3DGraphics = false; // Default to 3D graphics
// Import required modules


export const startScreen = () => {
    const startScreen = document.getElementById('startScreen');
    const playButton = document.getElementById('playButton');
    const canvasContainer = document.getElementById('canvasContainer');
    const styleCheckbox = document.getElementById('styleCheckbox');
    
    playButton.addEventListener('click', () => {
        
        startScreen.style.display = 'none';
        canvasContainer.style.display = 'block';
        renderPongGame(is3DGraphics); 
    });

    styleCheckbox.addEventListener('change', (event) => {
        is3DGraphics = event.target.checked; 
    });
};

export const updateScoreboard = () => {
        get_game_state().then(response => {
        const p1Score = response.p1_score;
        const p2Score = response.p2_score;
        document.querySelector('.score-left').textContent = `P1 SCORE: ${p1Score}`;
        document.querySelector('.score-right').textContent = `P2 SCORE: ${p2Score}`;
    }).catch(error => {
        console.error('Error retrieving scoreboard:', error);
    });
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
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(0, 0, 1);
    scene.add(directionalLight);
    let p1_paddle, p2_paddle, ball;
    p1_paddle = create2DPaddle(0x808080); // Old-school TV Pong grey
    p2_paddle = create2DPaddle(0x808080);
    ball = new THREE.Mesh(new THREE.PlaneGeometry(5, 5), new THREE.MeshStandardMaterial({color: 0x808080}));
    scene.add(p2_paddle);
    scene.add(ball);
    scene.add(p1_paddle);
    get_game_state().then(response => {
        console.log("setting up scene:  ", response)
        p1_paddle.position.set(response.p1_pos, response.p1_pos_y, 0);
        p2_paddle.position.set(response.p2_pos, response.p2_pos_y, 0);
    }).catch(error => {
        console.error('Error fetching paddle position from API:', error);
    });
    return camera;
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

    return camera; // Return the camera object
}
function create2DPaddle(color) {
    const geometry = new THREE.BoxGeometry(5, 20, 0);
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
    let camera; // Declare camera variable

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight);
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    
    let p1_paddle, p2_paddle, ball;
    if (is3DGraphics) {
        camera = setup3DScene(scene);
    } else {
        camera = setup2DScene(scene);
    }
    ///set up is completed by this point, game is now rendering/////

    var clock = new THREE.Clock();
    var time = 0;
    var delta = 0;

    camera.position.z = 200;



    function animate() {
        requestAnimationFrame(animate);
        updateScoreboard();
        get_game_state().then(response => {
            console.log("Animate:  ", response)
            // p1_paddle.position.set(response.p1_pos, response.p1_pos_y, 0);
            // p2_paddle.position.set(response.p2_pos, response.p2_pos_y, 0);
            renderer.render(scene, camera);
        }).catch(error => {
            console.error('Error fetching game state:', error);
        });
        }
        renderer.render(scene, camera);

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
