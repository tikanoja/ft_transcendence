import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

let socket;
let gameNumber = -1;
let made_listner = 0;
let setup_done = 0;

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
        console.log(gameNumber);
        console.log("after verify: ", gameNumber);
        
        startScreen.style.display = 'none';
        canvasContainer.style.display = 'block';
        // # DONT FORGET to maybe insert to here to get permission from django to start the game
        socket.emit("message", "start_game," + gameNumber);
        
        socket.on('start_state', (data) => {
            startScreen.style.display = 'none';
            canvasContainer.style.display = 'block';
            const valuesArray = data.split(',');
            gameNumber = valuesArray[1];
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
    const moveCountElement = document.querySelector('.move-count');

    if (isNaN(p1Score) || isNaN(p2Score)) {
        return;
    }
    if (scoreLeftElement && scoreRightElement) {
        if (p1Score !== previousP1Score || p2Score !== previousP2Score) {
            scoreLeftElement.textContent = `P1 Score: ${p1Score}`;
            scoreRightElement.textContent = `P2 Score: ${p2Score}`;
            moveCountElement.textContent = `Moves: ${currentMoveCount}`;
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
   
    const camera = new THREE.PerspectiveCamera(
        75,
        canvasWidth / canvasHeight,
        -2,
        10000
    );

    const distance = Math.max(boardWidth, boardHeight) / (2 * Math.tan(Math.PI * camera.fov / 290));
    camera.position.set(0, 20, distance);
    camera.lookAt(scene.position);
    
    const textureLoader = new THREE.TextureLoader();
    let colourOneSrc = "../textures/purple_square.png";
    let colourOneSrc_1 = "../textures/purple_1_sm.png";
    let colourOneSrc_2 = "../textures/purple_2_sm.png";

    let colourTwoSrc = "../textures/red_square.png";
    let colourTwoSrc_1 = "../textures/red_1_sm.png";
    let colourTwoSrc_2 = "../textures/red_2_sm.png";

    let colourThreeSrc = "../textures/green_square.png";
    let colourThreeSrc_1 = "../textures/green_1_sm.png";
    let colourThreeSrc_2 = "../textures/green_2_sm.png";

    let colourFourSrc = "../textures/blue_square.png";
    let colourFourSrc_1 = "../textures/blue_1_sm.png";
    let colourFourSrc_2 = "../textures/blue_2_sm.png";

    const buttons = document.querySelectorAll('#GameControls button img');
    const button1 = document.querySelector('button[type="Colour 1"] img');
    const button2 = document.querySelector('button[type="Colour 2"] img');
    const button3 = document.querySelector('button[type="Colour 3"] img');
    const button4 = document.querySelector('button[type="Colour 4"] img');
   
    const colorTextures = {
        colorOne: {
            0: {
                texture: textureLoader.load(colourOneSrc, (texture) => {
                    button1.src = texture.image.src;
                })
            },
            1: {
                texture: textureLoader.load(colourOneSrc_1, () => {})
            },
            2: {
                texture: textureLoader.load(colourOneSrc_2, () => {})
            }
        },
        colorTwo: {
            0: {
                texture: textureLoader.load(colourTwoSrc, (texture) => {
                    button2.src = texture.image.src;
                })
            },
            1: {
                texture: textureLoader.load(colourTwoSrc_1, () => {})
            },
            2: {
                texture: textureLoader.load(colourTwoSrc_2, () => {})
            }
        },
        colorThree: {
            0: {
                texture: textureLoader.load(colourThreeSrc, (texture) => {
                    button3.src = texture.image.src;
                })
            },
            1: {
                texture: textureLoader.load(colourThreeSrc_1, () => {})
            },
            2: {
                texture: textureLoader.load(colourThreeSrc_2, () => {})
            }
        },
        colorFour: {
            0: {
                texture: textureLoader.load(colourFourSrc, (texture) => {
                    button4.src = texture.image.src;
                })
            },
            1: {
                texture: textureLoader.load(colourFourSrc_1, () => {})
            },
            2: {
                texture: textureLoader.load(colourFourSrc_2, () => {})
            }
        }
    };

    const controls = document.getElementById('GameControls');
    controls.style.display = 'flex';
    buttons.forEach(button => {
        button.style.display = 'flex';
    });
    addLighting(scene);


    function updateGameState(data, tileMeshes) {
        const valuesArray = data.split(',');
        if (gameNumber == valuesArray[1]) {
    
            let tileLegend = [];
            let player1score = valuesArray[2];
            let player2score = valuesArray[3];
            let currentMoveCount = valuesArray[5];
    
            for (let i = 6; i < valuesArray.length; i += 2) {
                const color = valuesArray[i];
                const owner = valuesArray[i + 1];
                const tile = { color, owner };
                tileLegend.push(tile);
            }
    
            tileLegend.forEach((tileInfo, index) => {
                let tileTexture;
                if (tileInfo.color === '1') {
                    tileTexture = colorTextures.colorOne[tileInfo.owner].texture;
                } else if (tileInfo.color === '2') {
                    tileTexture = colorTextures.colorTwo[tileInfo.owner].texture;
                } else if (tileInfo.color === '3') {
                    tileTexture = colorTextures.colorThree[tileInfo.owner].texture;
                } else if (tileInfo.color === '4') {
                    tileTexture = colorTextures.colorFour[tileInfo.owner].texture;
                }
    
                const tileMesh = tileMeshes[index];
                tileMesh.material.map = tileTexture;
                tileMesh.material.needsUpdate = true;
            });
    
            updateScoreboard(player1score, player2score, currentMoveCount);
    
            let gameRunning =  valuesArray[4];
            if (gameRunning != 1) {
                render = false;
            }
            console.log(render);
        }
    }
    
    function setupGameBoard(data) {
        
        const tileMeshes = [];
    
        for (let row = 0; row < numRows; row++) {
            for (let col = 0; col < numCols; col++) {
                const x = boardStartX + col * tileSize;
                const y = boardStartY + row * tileSize;
    
                const tileGeometry = new THREE.PlaneGeometry(tileSize, tileSize);
                const tileMaterial = new THREE.MeshBasicMaterial();
                const tileMesh = new THREE.Mesh(tileGeometry, tileMaterial);
                tileMesh.position.set(x, y, 0);
                scene.add(tileMesh);
                tileMeshes.push(tileMesh);
            }
        }
        updateGameState(data, tileMeshes);
        return tileMeshes;
    }

    const tileMeshes = setupGameBoard(data);
    
    ///////////////////////////////////////////



    document.addEventListener('keydown', (event) => {
		event.preventDefault();
			if (event.key == 'c')
		{
			socket.emit('message', 'stop_game,' + gameNumber);
			render = false;
		}
    });
    
    socket.on('state', (data) => {
        updateGameState(data, tileMeshes)
    });

    function exit_game(data)
	{
        updateGameState(data, tileMeshes)
        loadGameOverScreen(data)
		stopAnimation()
	}

	socket.on('endstate', (data) => {
        exit_game(data)
    });

    function handleMouseUpButton1() {
        console.log('Button 1 released');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "1");
    }
    
    function handleMouseUpButton2() {
        console.log('Button 2 released');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "2");
    }

    function handleMouseUpButton3() {
        console.log('Button 3 released');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "3");
    }
    
    function handleMouseUpButton4() {
        console.log('Button 4 released');
        socket.emit('message', 'make_move,' + gameNumber + ',' + "4");
    }
    
    if (made_listner == 0)
    {
        button1.addEventListener('mouseup', handleMouseUpButton1);
        button2.addEventListener('mouseup', handleMouseUpButton2);
        button3.addEventListener('mouseup', handleMouseUpButton3);
        button4.addEventListener('mouseup', handleMouseUpButton4);
        made_listner = 1
    }

  
    let animationId;

    function animate() {
        animationId = requestAnimationFrame(animate);
        renderer.render(scene, camera);

    }


    function startAnimation() {

        animationId = requestAnimationFrame(animate);
        animate();
    }

	function stopAnimation() {
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
    else
    {
        stopAnimation()
    }

};
