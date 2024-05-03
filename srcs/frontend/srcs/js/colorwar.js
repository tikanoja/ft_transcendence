import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

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
    socket = io.connect('https://' + window.location.hostname, {path: "/colorwar/socket.io"});
    socket.on('connect', () => {
        console.log("connect recieved: Color war")
    });
    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
}

// export const verifyUsername = () => {
//     return new Promise((resolve, reject) => {
//         const username1Element = document.getElementById('player1');
//         const username2Element = document.getElementById('player2');
//         const username1 = username1Element.innerText.trim();
//         const username2 = username2Element.innerText.trim();
//         const usernameString = username1 + "," + username2;
        
//         socket.emit("username", usernameString);

//         socket.on('setup_game', (data) => {
//             console.log("in setup game");
//             const valuesArray = data.split(',');
//             gameNumber = valuesArray[1];
//             console.log("after setup game: ", gameNumber);
//             resolve(gameNumber);
//         });

//         socket.on('error', (error) => {
//             reject('Error verifying username:', error);
//         });
//     });
// };

export const startScreenColorwar = async () => {
    try {
        await loadScript();
        connectWebSocket();

        const startScreen = document.getElementById('startScreen');
        const playButton = document.getElementById('ColorwarPlayButton');
        const canvasContainer = document.getElementById('canvasContainer');

        // await verifyUsername();
        
        playButton.addEventListener('click', () => {
            startScreen.style.display = 'none';
            canvasContainer.style.display = 'block';
            renderColorwar()
        });
    } catch (error) {
        console.error('Error loading script:', error);
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

export const renderColorwar = () => {
    console.log("in renderer")

    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    scene.background = new THREE.Color(0xabcdef)   
    const existingCanvas = document.getElementById('colorCanvas');
    if (existingCanvas) {
        existingCanvas.remove();
    }
    const pixelRatio = window.devicePixelRatio;
    renderer.setPixelRatio(pixelRatio);
	renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4));
    renderer.domElement.id = 'colorCanvas'; // Set an id for the new canvas
    document.getElementById('canvasContainer').appendChild(renderer.domElement);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    // const camera = new THREE.OrthographicCamera(window.innerWidth / -2, window.innerWidth / 2, window.innerHeight / 2, window.innerHeight / -2, 1, 1000);
    camera.position.set(100, 200, 1000);
    const tileSize = 50; // Size of each tile
    const numRows = 8; // Number of rows in the grid
    const numCols = 8; // Number of columns in the grid
    
    // Initialize an array to store tile data
    const tileData = [];
    
    // Generate tile data for the grid
    for (let row = 0; row < numRows; row++) {
        for (let col = 0; col < numCols; col++) {
            // Determine the color based on row and column index
            const color = (row + col) % 2 === 0 ? 0xffffff : 0x000000;
            
            // Calculate the position of the tile
            const x = col * tileSize;
            const y = row * tileSize;
            
            // Add tile data to the array
            tileData.push({ position: { x, y }, color });
        }
    }
    
    // Create tiles based on the tile data
    tileData.forEach(tileInfo => {
        const geometry = new THREE.PlaneGeometry(tileSize, tileSize);
        const material = new THREE.MeshBasicMaterial({ color: tileInfo.color });
        const tile = new THREE.Mesh(geometry, material);
        tile.position.set(tileInfo.position.x, tileInfo.position.y, 0); // Set z position to 0
        scene.add(tile);
    });

    const ball = new THREE.Mesh(new THREE.SphereGeometry(10, 32, 32), new THREE.MeshPhongMaterial({ color: 0xff00ff }));
    scene.add(ball);
    addLighting(scene);
    console.log("ball added");

    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }

    animate();
};