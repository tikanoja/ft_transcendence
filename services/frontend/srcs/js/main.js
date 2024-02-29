// Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';

export const test = () => {
    // Setup scene, camera, and renderer
    function addLighting(scene) {
        let color = 0x0000ff;
        let intensity = 8;
        let light = new THREE.DirectionalLight(color, intensity);
        light.position.set(15, 35, 20);
        light.target.position.set(15, 29, 15);
        const amb_light = new THREE.AmbientLight(0xFFFFFF);
        scene.add(light);
        scene.add(light.target);
        scene.add(amb_light);
    }

    let keyDown = false; //

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('canvasContainer').appendChild(renderer.domElement);
	const directionalLight = addLighting(scene); // Store the directional light
    

    // Create a cube
    const p1_geometry = new THREE.BoxGeometry(5, 20, 5);
    const p1_material = new THREE.MeshStandardMaterial({ color: 0xEF85A8}); //
    const p1_paddle = new THREE.Mesh(p1_geometry, p1_material);
	p1_paddle.position.set(-45, 25, 15);
    scene.add(p1_paddle);


	const p2_geometry = new THREE.BoxGeometry(5, 20, 5);
    const p2_material = new THREE.MeshStandardMaterial({ color: 0xC2C9C9});
    const p2_paddle = new THREE.Mesh(p2_geometry, p2_material);
	scene.add(p2_paddle);
	p2_paddle.position.set(45, 25, 15);
    scene.add(p2_paddle);


    const sphere = new THREE.Mesh(new THREE.SphereGeometry(5, 10, 6), new THREE.MeshPhongMaterial({color: 0xff00ff}))
    const material = new THREE.MeshPhongMaterial({ color: 0xffff00 });
    scene.add(sphere);
	var clock = new THREE.Clock();
	var time = 0;
	var delta = 0;

    camera.position.z = 100;

    // Function to update object visibility based on checkbox state
    const updateObjectVisibility = (object, checkbox) => {
        object.visible = checkbox.checked;
    };

    // Checkbox event listeners
    const cubeCheckbox = document.getElementById('cubeCheckbox');
    cubeCheckbox.addEventListener('change', () => {
        updateObjectVisibility(cube, cubeCheckbox);
    });

    const sphereCheckbox = document.getElementById('sphereCheckbox');
    sphereCheckbox.addEventListener('change', () => {
        updateObjectVisibility(sphere, sphereCheckbox);
    });

    function animate() {
        requestAnimationFrame(animate);
		// sphere.rotation.x += 0.01;
        // sphere.rotation.y += 0.01;
		// delta = clock.getDelta();
		// time += delta;
		// sphere.position.y = 0.5 + Math.abs(Math.sin(time * 3)) * 2;
		// sphere.position.z = Math.cos(time) * 4;

        renderer.render(scene, camera);
    }

    document.addEventListener('keydown', (event) => {
        if (!keyDown) {
            keyDown = true;

            const speed = 0.8; // Adjust the speed
            const moveP1 = () => {
                switch (event.key) {
                    case 'ArrowLeft':
                        p1_paddle.position.x -= speed; // Move left
                        break;
                    case 'ArrowRight':
                        p1_paddle.position.x += speed; // Move right
                        break;
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
                        p2_paddle.position.y += speed; // Move left
                        break;
                    case 's':
                        p2_paddle.position.y -= speed; // Move right
                        break;
                    case 'd':
                        p2_paddle.position.x += speed; // Move up
                        break;
                    case 'a':
                        p2_paddle.position.x-= speed; // Move down
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
    }

    function stopAnimation() {
        cancelAnimationFrame(animationId);
    }

    document.addEventListener('pagechange', (event) => {
        const page = event.detail.page;
        if (page === '/test') {
            startAnimation();
        } else {
            stopAnimation();
        }
    });
    startAnimation();
};
