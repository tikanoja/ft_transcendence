// Import required modules
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.137.5/build/three.module.js';
export const test = () => {
	// Setup scene, camera, and renderer
	const scene = new THREE.Scene();
	const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
	const renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth, window.innerHeight);
	document.getElementById('canvasContainer').appendChild(renderer.domElement);
	
	// Create a cube
	const geometry = new THREE.BoxGeometry(1, 1, 1);
	const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
	const cube = new THREE.Mesh(geometry, material);
	scene.add(cube);
	
	camera.position.z = 5;
	
	function animate() {
		requestAnimationFrame(animate);
		cube.rotation.x += 0.01;
		cube.rotation.y += 0.01;
		renderer.render(scene, camera);
	}
	
	document.addEventListener('keydown', (event) => {
		const speed = 0.1; // Adjust the speed
		switch (event.key) {
			case 'ArrowLeft':
				cube.position.x -= speed; // Move left
				break;
			case 'ArrowRight':
				cube.position.x += speed; // Move right
				break;
			case 'ArrowUp':
				cube.position.y += speed; // Move up
				break;
			case 'ArrowDown':
				cube.position.y -= speed; // Move down
				break;
		}
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
}

// Initial call to start the animation

