import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

let socket;
let gameNumber = -1;
let render = true;
const eventListeners = new Map();


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
        console.log("connection recieved: Color war")
    });
    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
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
export const startScreenColorwar = async () => {
    try {
        await loadScript();
        connectWebSocket();

        const startScreen = document.getElementById('startScreen');
        const canvasContainer = document.getElementById('canvasContainer');
        
        await verifyUsername();
        
        startScreen.style.display = 'none';
        canvasContainer.style.display = 'block';

        socket.emit("message", "start_game," + gameNumber);
        
        socket.on('start_state', (data) => {
            startScreen.style.display = 'none';
            startScreen.remove();
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

export const updateScoreboard = (p1Score, p2Score, currentMoveCount, currentPlayerMove) => {
    const scoreLeftElement = document.querySelector('#player1Score');
    const scoreRightElement = document.querySelector('#player2Score');
    const moveCountElement = document.getElementById('moveCounter'); 
    const p1Card = document.getElementById('P1Card');
    const p2Card = document.getElementById('P2Card');
    
    if (currentPlayerMove == '0') {
        p1Card.classList.add('border-success');
        p1Card.classList.remove('border-dark');
        p1Card.style.borderWidth = '4px';
        
        p2Card.classList.add('border-dark');
        p2Card.classList.remove('border-success');
        p2Card.style.borderWidth = '1px';
    } else if (currentPlayerMove == '1') {
        p1Card.classList.add('border-dark');
        p1Card.classList.remove('border-success');
        p1Card.style.borderWidth = '1px';
        
        p2Card.classList.add('border-success');
        p2Card.classList.remove('border-dark');
        p2Card.style.borderWidth = '4px';
    }

    if (isNaN(p1Score) || isNaN(p2Score)) {
        return;
    }
    if (scoreLeftElement && scoreRightElement) {
        if (p1Score !== previousP1Score || p2Score !== previousP2Score) {
            scoreLeftElement.textContent = p1Score;
            scoreRightElement.textContent = p2Score;
            moveCountElement.textContent = currentMoveCount;
            previousP1Score = p1Score;
            previousP2Score = p2Score;
        }
    } else {
        console.error('Scoreboard elements not found.');
    }
};


function loadGameOverScreen(data) {
    const winnerInfo = document.getElementById('winnerInfo');
    const gameOverScreen = document.getElementById('gameOverScreen');
    const P1score = document.getElementById('P1Card');
    const P2score = document.getElementById('P2Card');
    const moveCount = document.getElementById('moveCard');
    P1score.style.display = 'none';
    P2score.style.display = 'none';
    moveCount.style.display = 'none';
    const valuesArray = data.split(',');
    let player1score = valuesArray[2];
    let player2score = valuesArray[3];

    const controls = document.getElementById('GameControls');
    const buttons = document.querySelectorAll('#GameControls button img');
    controls.style.display = 'none';
    buttons.forEach(button => {
        button.style.display = 'none';
    });
    const player1username = document.getElementById('player1username').value;
    const player2username = document.getElementById('player2username').value;
    let winnerText;
    if (player1score > player2score) {
        winnerText = `${player1username} wins!`;
    } else if (player1score < player2score) {
        winnerText = `${player2username} wins!`;
    } else {
        winnerText = "It's a tie!";
    } //TODO : fix this, ties arent possible

    winnerInfo.textContent = winnerText;
    gameOverScreen.style.display = 'block';
    const canvasContainer = document.getElementById('canvasContainer');
    canvasContainer.style.display = 'none';
}

function cleanupGameBoard(tileMeshes) {
    tileMeshes.forEach(tileMesh => {
        tileMesh.geometry.dispose();
        tileMesh.material.dispose();
    });
}

function exitGame(data, tileMeshes, colorTextures)
{
    updateGameState(data, tileMeshes, colorTextures)
    loadGameOverScreen(data)
    const button1 = document.querySelector('button[type="Colour 1"] img');
    const button2 = document.querySelector('button[type="Colour 2"] img');
    const button3 = document.querySelector('button[type="Colour 3"] img');
    const button4 = document.querySelector('button[type="Colour 4"] img');
    button1.removeEventListener('mouseup', () => handleMouseUpButton1(gameNumber));
    button2.removeEventListener('mouseup', () => handleMouseUpButton2(gameNumber));
    button3.removeEventListener('mouseup', () => handleMouseUpButton3(gameNumber));
    button4.removeEventListener('mouseup', () => handleMouseUpButton4(gameNumber));
    cleanupGameBoard(tileMeshes)

    const scoreboard = document.getElementById('scoreboard');
    scoreboard.remove;
    AnimationController.stopAnimation();
}


function updateGameState(data, tileMeshes, colorTextures) {
    const valuesArray = data.split(',');
    if (gameNumber == valuesArray[1]) {
        let tileLegend = [];
        let player1score = valuesArray[2];
        let player2score = valuesArray[3];
        let currentMoveCount = valuesArray[5];
        for (let i = 6; i < valuesArray.length - 1; i += 2) {
            const color = valuesArray[i];
            const owner = valuesArray[i + 1];
            const tile = { color, owner };
            tileLegend.push(tile);
        }
        let currentPlayerMove = valuesArray[ valuesArray.length -1];

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

        updateScoreboard(player1score, player2score, currentMoveCount, currentPlayerMove);

        let gameRunning =  valuesArray[4];
        if (gameRunning != 1) {
            render = false;
        }
    }
}

function setupGameBoard(data, boardStartX, boardStartY, numRows, numCols,  colorTextures, tileSize, scene) {
        
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
    updateGameState(data, tileMeshes, colorTextures);
    return tileMeshes;
}


function handleMouseUpButton1(gameNumber) {
    socket.emit('message', 'make_move,' + gameNumber + ',' + "1");
}


function handleMouseUpButton2(gameNumber) {
    socket.emit('message', 'make_move,' + gameNumber + ',' + "2");
}

function handleMouseUpButton3(gameNumber) {
    socket.emit('message', 'make_move,' + gameNumber + ',' + "3");
}

function handleMouseUpButton4(gameNumber) {
    socket.emit('message', 'make_move,' + gameNumber + ',' + "4");
}


const AnimationController = {
    animationId: null,
    
    animate: function(scene, camera, renderer) {
    
            this.animationId = requestAnimationFrame(() => this.animate(scene, camera, renderer));
            renderer.render(scene, camera);
    },
    
    stopAnimation: function() {
        // socket.emit('message', 'stop_game,' + gameNumber);
        socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
        cancelAnimationFrame(this.animationId);
    },
    
    startAnimation: function(scene, camera, renderer)
    {
        this.animate(scene, camera, renderer);
    }
};

function onWindowResize(camera, renderer) {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);

    const originalWidth = 100; 
    const originalHeight = 100; 
    const canvas = renderer.domElement;
    
    canvas.style.width = `${window.innerWidth - (window.innerWidth / 4)}px`;
    canvas.style.height = `${window.innerHeight - (window.innerHeight / 4)}px`;

    const P1score = document.getElementById('P1Card');
    const P2score = document.getElementById('P2Card');
    const moveCount = document.getElementById('moveCard');
   
    const scaleFactor = Math.min(window.innerWidth, window.innerHeight) / 1000;
    const buttons = document.querySelectorAll('#GameControls button img');
    buttons.forEach(button => {
        button.style.width = `${scaleFactor * originalWidth}px`;
        button.style.height = `${scaleFactor * originalHeight}px`;
    });

    moveCount.style.display = 'block';
    P1score.style.display = 'block';
    P2score.style.display = 'block';

    const gameControls = document.getElementById('GameControls');
    gameControls.style.display = 'block';
}

function addUniqueEventListener(button, event, handler) {
    const key = button;

    if (!eventListeners.has(key)) {
        eventListeners.set(key, new Set());
    }

    const handlers = eventListeners.get(key);

    if (!Array.from(handlers).some(({ event: e, handler: h }) => e === event && h.toString() === handler.toString())) {
        button.addEventListener(event, handler);

        handlers.add({ event, handler });

    }
}

export const renderColorwar = (gameNumber, data) => {
    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer();
    
    const existingCanvas = document.getElementById('colorCanvas');
    if (existingCanvas) {
        existingCanvas.remove();
    }
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    const scoreboard = document.getElementById('scoreboard');
    scoreboard.display = 'block';
    renderer.domElement.id = 'colorCanvas'; 
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
 
	renderer.setSize(window.innerWidth / 2 , window.innerHeight - (window.innerHeight / 4));
    let canvasFocused = true;
    const canvas = renderer.domElement;

    canvas.setAttribute('tabindex', '0');
    canvas.addEventListener('focus', () => {
        canvasFocused = true;
    });
    
    canvas.addEventListener('blur', () => {
        canvasFocused = false;
    });

    
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
        
    onWindowResize(camera, renderer);
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

    window.addEventListener('resize',() => onWindowResize(camera, renderer));

    const controls = document.getElementById('GameControls');
    controls.style.display = 'flex';
    buttons.forEach(button => {
        button.style.display = 'flex';
    });
    addLighting(scene);

    const tileMeshes = setupGameBoard(data, boardStartX, boardStartY, numRows, numCols, colorTextures, tileSize, scene);

    
    socket.on('state', (data) => {
        updateGameState(data, tileMeshes, colorTextures)
    });

	socket.on('endstate', (data) => {
        socket.emit('message', 'stop_game,' + gameNumber);
        exitGame(data, tileMeshes, colorTextures);
    });


    
    if (canvasFocused) {
        addUniqueEventListener(button1, 'mouseup', () => handleMouseUpButton1(gameNumber));
        addUniqueEventListener(button2, 'mouseup', () => handleMouseUpButton2(gameNumber));
        addUniqueEventListener(button3, 'mouseup', () => handleMouseUpButton3(gameNumber));
        addUniqueEventListener(button4, 'mouseup', () => handleMouseUpButton4(gameNumber));
    }
    
    if (render) {
        AnimationController.startAnimation(scene, camera, renderer);
    }
    else
    {
        AnimationController.stopAnimation();
    }

};
