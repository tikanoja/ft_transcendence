
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

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
    socket = io.connect('https://' + window.location.hostname);
	console.log(window.location.hostname)
    socket.on('connect', () => {
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
            console.log("in setup game");
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

export const startScreen = async () => {
    try {
			await loadScript();
			connectWebSocket();
            
			const startScreen = document.getElementById('startScreen');
			const canvasContainer = document.getElementById('canvasContainer');
			const styleCheckbox = document.getElementById('styleCheckbox');
			let is3DGraphics = false;
            
            await verifyUsername()
            console.log("after verify: ", gameNumber);
            

                startScreen.style.display = 'none';
                canvasContainer.style.display = 'block';
                is3DGraphics = styleCheckbox.checked;

                // # DONT FORGET to maybe insert to here to get permission from django to start the game
                socket.emit('message', 'start_game,' + gameNumber);

                socket.on('start_game', (data) => {
                    console.log("start game was called")
                    startScreen.style.display = 'none';
                    canvasContainer.style.display = 'block';
                    console.log(data)
                    const valuesArray = data.split(',')
                    gameNumber = valuesArray[1]
                    renderPongGame(is3DGraphics, gameNumber);
                })
                
    } catch (error) {
        console.error('Error loading script:', error);
    }
};

// Define the gameOverScreen function within the same scope
function loadGameOverScreen(data) {
    const winnerInfo = document.getElementById('winnerInfo');
    const gameOverScreen = document.getElementById('gameOverScreen');
    
    const valuesArray = data.split(',');
    const p1Score = parseInt(valuesArray[8]);
    const p2Score = parseInt(valuesArray[7]);

    let winnerText;
    if (p1Score > p2Score) {
        winnerText = "Player 1 wins!";
    } else if (p1Score < p2Score) {
        winnerText = "Player 2 wins!";
    } else {
        winnerText = "It's a tie!";
    }

    winnerInfo.textContent = winnerText;
    gameOverScreen.style.display = 'block';
    canvasContainer.style.display = 'none';
}

let previousP1Score = null;
let previousP2Score = null;

export const updateScoreboard = (p1Score, p2Score) => {
    const scoreLeftElement = document.querySelector('.score-left');
    const scoreRightElement = document.querySelector('.score-right');
    
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

function exit_game(data)
{
    updateGameState(data)
    loadGameOverScreen(data)
}

export const renderPongGame = (is3DGraphics, gameNumber) => {
    const scene = new THREE.Scene();

    const existingCanvas = document.getElementById('pongCanvas');
    if (existingCanvas) {
        existingCanvas.remove();
    }
    const renderer = new THREE.WebGLRenderer();

    
    renderer.setSize(window.innerWidth - (window.innerWidth / 4), window.innerHeight - (window.innerHeight / 4));
    
    renderer.domElement.id = 'pongCanvas'; 
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
    
    socket.on('state', (data) => {
        console.log(data)
        // updateGameState(data, min_visible_x, max_visible_x, min_visible_y, max_visible_y, p1_paddle, p2_paddle, ball)
    });

    socket.on('endstate', (data) => {
        exit_game(data)
        AnimationController.stopAnimation();
    });

    //THESE ARE INVERTED DUE TO COORD DIFFERENCE
    document.addEventListener('keydown', (event) => {
        event.preventDefault();
        if (event.key == 'ArrowUp')
        {
            socket.emit('message', 'right_paddle_down,' + gameNumber);
        }
        if (event.key  == 'ArrowDown')
        {
            socket.emit('message', 'right_paddle_up,' + gameNumber);
        }
        if (event.key  == 'w')
        {
            socket.emit('message', 'left_paddle_down,' + gameNumber);
        }
        if (event.key  == 's')
        {
            socket.emit('message', 'left_paddle_up,' + gameNumber);
        }
        if (event.key == 'c')
        {
            socket.emit('message', 'stop_game,' + gameNumber);
            render = false;
        }
    });

    document.addEventListener('keyup', (event) => {
        event.preventDefault();
        if (event.key == 'ArrowUp')
            socket.emit('message', 'right_paddle_down_release,' + gameNumber);
        if (event.key  == 'ArrowDown')
            socket.emit('message', 'right_paddle_up_release,' + gameNumber);
        if (event.key  == 'w')
            socket.emit('message', 'left_paddle_down_release,' + gameNumber);
        if (event.key  == 's')
            socket.emit('message', 'left_paddle_up_release,' + gameNumber);
    });

}