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

export const verifyUsername = () => {
    return new Promise((resolve, reject) => {
        const username1Element = document.getElementById('player1');
        const username2Element = document.getElementById('player2');
        const username1 = username1Element.innerText.trim();
        const username2 = username2Element.innerText.trim();
        const usernameString = username1 + "," + username2;
        
        socket.emit("username", usernameString);

        socket.on('setup_game', (data) => {
            console.log("in setup game", gameNumber);
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
export const startScreenColorwar = async () => {
    try {
        await loadScript();
        connectWebSocket();

        const startScreen = document.getElementById('startScreen');
        const playButton = document.getElementById('ColorwarPlayButton');
        const canvasContainer = document.getElementById('canvasContainer');

        await verifyUsername();
        socket.emit("message", "start_game")

        socket.on('message', (data) => {
            console.log(data)
        });
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
    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer();
    let render = true;
    renderer.setSize(window.innerWidth, window.innerHeight);

    const canvasContainer = document.getElementById('canvasContainer');
    canvasContainer.innerHTML = '';
    canvasContainer.appendChild(renderer.domElement);
    
    const pixelRatio = window.devicePixelRatio;
    renderer.setPixelRatio(pixelRatio);
	renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4)); 
    
    const video = document.getElementById('video');
    video.play();
    const texture = new THREE.VideoTexture(video);
    scene.background = texture;

    const numRows = 36;
    const numCols = 35;

    const canvasWidth = window.innerWidth - 250;
    const canvasHeight = window.innerHeight;

    const tileSizeFraction = 0.2;
    const tileSize = Math.min(canvasWidth, canvasHeight) * tileSizeFraction;

    const boardWidth = numCols * tileSize;
    const boardHeight = numRows * tileSize;

    const boardStartX = (canvasWidth - boardWidth) / 1.5;
    const boardStartY = (canvasHeight - boardHeight)/ 1.8;

    // Texture for the tiles
    const textureLoader = new THREE.TextureLoader();

    const baseTileTexture = textureLoader.load("../textures/BackTile_05.png", () => {
        console.log("Base tile loaded successfully.");
    });

    const colorOneTexture = textureLoader.load("../textures/tileBlue_01.png", () => {
        console.log("Color 1 loaded successfully.");
    });

    const colorTwoTexture = textureLoader.load("../textures/tileGreen_01.png", () => {
        console.log("Color 2 loaded successfully.");
    });

    const colourThreeTexture = textureLoader.load("../textures/tilePink_01.png", () => {
        console.log("Color 3 loaded successfully.");
    });

    function updateGameState(data)
    {
        console.log(data)
        const tileData = [];
        // Generate tile data for the grid
        for (let row = 0; row < numRows; row++) {
            for (let col = 0; col < numCols; col++) {
                const x = boardStartX + col * tileSize;
                const y = boardStartY + row * tileSize;
                tileData.push({ position: { x, y }, baseTileTexture });
            }
        }
    
        const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xff00ff });
    
        tileData.forEach((tileInfo, index) => {
            const tileId = index;
            const tileGeometry = new THREE.PlaneGeometry(tileSize, tileSize);
            const tileMaterial = new THREE.MeshBasicMaterial({ map: tileInfo.tileTexture });
            const tileMesh = new THREE.Mesh(tileGeometry, tileMaterial);
            tileMesh.position.set(tileInfo.position.x, tileInfo.position.y, 0);
            scene.add(tileMesh);
        });
    }
    // Set up orthographic camera
    const camera = new THREE.PerspectiveCamera(
        75,
        canvasWidth / canvasHeight,
        1,
        10000
    );

    // Calculate distance from the board based on its size
    const distance = Math.max(boardWidth, boardHeight) / (2 * Math.tan(Math.PI * camera.fov / 360));

    // Position the camera
    camera.position.set(0, 20, distance + 1000); // Adjust camera position to be in front of the scene
    camera.lookAt(scene.position);

    addLighting(scene);


    document.addEventListener('keydown', (event) => {
		event.preventDefault();
			if (event.key == 'c')
		{
			socket.emit('message', 'stop_game,' + gameNumber);
			render = false;
		}
    });
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
