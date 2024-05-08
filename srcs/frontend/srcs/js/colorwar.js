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
            const valuesArray = data.split(',');
            gameNumber = valuesArray[1];
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
            const canvasContainer = document.getElementById('canvasContainer');

            await verifyUsername();
            console.log(gameNumber)
            console.log("after verify: ", gameNumber);
            

            startScreen.style.display = 'none';
            canvasContainer.style.display = 'block';
            
            // # DONT FORGET to maybe insert to here to get permission from django to start the game
            socket.emit("message", "start_game," + gameNumber)
            
            socket.on('state', (data) => {
                startScreen.style.display = 'none';
                canvasContainer.style.display = 'block';
                const valuesArray = data.split(',')
                gameNumber = valuesArray[1]
                renderColorwar(gameNumber, data);
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

let previousP1Score = null;
let previousP2Score = null;

export const updateScoreboard = (p1Score, p2Score, currentMoveCount) => {
    const scoreLeftElement = document.querySelector('.score-left');
    const scoreRightElement = document.querySelector('.score-right');
    //TODO: THIS NEEDS TO IMPLIMENT CURRENT MOVE COUNT BUT DOES NOT YET
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

export const renderColorwar = (gameNumber, data) => {
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
    
    scene.background = new THREE.Color(0x332D2D);

    const numRows = 19;
    const numCols = 36;
    const canvasWidth = window.innerWidth - 250;
    const canvasHeight = window.innerHeight;

    const tileSize = Math.min(canvasWidth, canvasHeight)

    const boardWidth = numCols * tileSize;
    const boardHeight = numRows * tileSize;
    const boardStartX = (canvasWidth - boardWidth) / 1.9;
    const boardStartY = (canvasHeight - boardHeight)/ 2;

    
    const textureLoader = new THREE.TextureLoader();
    let colourOneSrc = "../textures/purple_square.png";
    let colourTwoSrc = "../textures/red_square.png";
    let colourThreeSrc = "../textures/yellow_square.png";
    let colourFourSrc = "../textures/blue_square.png";

    const button1 = document.querySelector('button[type="Colour 1"] img');
    const button2 = document.querySelector('button[type="Colour 2"] img');
    const button3 = document.querySelector('button[type="Colour 3"] img');
    const button4 = document.querySelector('button[type="Colour 4"] img');


    textureLoader.load(colourOneSrc, (texture) => {
        button1.src = texture.image.src;
    });

    textureLoader.load(colourTwoSrc, (texture) => {
        button2.src = texture.image.src;
    });

    textureLoader.load(colourThreeSrc, (texture) => {
        button3.src = texture.image.src;
    });

    textureLoader.load(colourFourSrc, (texture) => {
        button4.src = texture.image.src;
    });

    const colorOneTexture = textureLoader.load(colourOneSrc, () => {
        console.log("Color 2 loaded successfully.");
    });
    
    const colorTwoTexture = textureLoader.load(colourTwoSrc, () => {
        console.log("Color 2 loaded successfully.");
    });
    
    const colourThreeTexture = textureLoader.load(colourThreeSrc, () => {
        console.log("Color 3 loaded successfully.");
    });
    const colourFourTexture = textureLoader.load(colourFourSrc, () => {
        console.log("Color 3 loaded successfully.");
    });

    updateGameState(data);
    function updateGameState(data)
    {
        const valuesArray = data.split(',')
        if (gameNumber == valuesArray[1])
        {
            let player1score = valuesArray[2];
            let player2score = valuesArray[3];
            let currentMoveCount = valuesArray[5];
            let tileLegend = [];
            let tileData = [];

            for (let i = 6; i < valuesArray.length; i += 2) {
                const color = valuesArray[i];
                const owner = valuesArray[i + 1];
                const tile = { color, owner };
                tileLegend.push(tile);
            }

            let legendIndex = 0;
            for (let row = 0; row < numRows; row++) {
                for (let col = 0; col < numCols; col++) {
                    const x = boardStartX + col * tileSize;
                    const y = boardStartY + row * tileSize;

                    const color = tileLegend[legendIndex].color;
                    const owner = tileLegend[legendIndex].owner;

                    let tileTexture;

                    if (color === '1')
                    {
                        tileTexture = colorOneTexture;
                    }
                    else if (color === '2') 
                    {
                        tileTexture = colorTwoTexture;
                    }
                    else if  (color === '3') 
                    {
                         tileTexture = colourThreeTexture;
                    }
                    else if (color === '4')
                    {
                        tileTexture = colourFourTexture;
                    }
                    tileData.push({ position: { x, y }, tileTexture });
                    legendIndex++;
                }
            }
            // new THREE.TextGeometry( text, parameters ); maybe texts ??
            
            tileData.forEach((tileInfo) => {
                const tileGeometry = new THREE.PlaneGeometry(tileSize, tileSize);
                const tileMaterial = new THREE.MeshBasicMaterial({ map: tileInfo.tileTexture });
                const tileMesh = new THREE.Mesh(tileGeometry, tileMaterial);
                tileMesh.position.set(tileInfo.position.x, tileInfo.position.y, 0);
                scene.add(tileMesh);
            });
            
            updateScoreboard(player1score, player2score, currentMoveCount);
            let gameRunning =  valuesArray[4];
            if (gameRunning != 1)
                render = false
        }
    }

    const camera = new THREE.PerspectiveCamera(
        75,
        canvasWidth / canvasHeight,
        -2,
        10000
    );
    const distance = Math.max(boardWidth, boardHeight) / (2 * Math.tan(Math.PI * camera.fov / 290));
    camera.position.set(0, 20, distance);
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


    button1.addEventListener('click', function() {
        console.log('Button 1 clicked');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "1")
    });

    button2.addEventListener('click', function() {
        console.log('Button 2 clicked');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "2")
    });

    button3.addEventListener('click', function() {
        console.log('Button 3 clicked');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "3")
    });

    button4.addEventListener('click', function() {
        console.log('Button 4 clicked');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "4")
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
        animate();
    }

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
