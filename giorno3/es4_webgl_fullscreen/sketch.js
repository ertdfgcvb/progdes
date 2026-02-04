
function setup() {
	createCanvas(innerWidth, innerHeight, WEBGL)
}

function windowResized() {
	resizeCanvas(innerWidth, innerHeight)
}


function draw() {
	background(200)

	rotateX(sin(frameCount * 0.0052) * 5)
	rotateY(sin(frameCount * 0.0066) * 5)
	rotateZ(sin(frameCount * 0.0078) * 5)



	const l = map(sin(frameCount * 0.061), -1, 1, 100, 200)

	box(l * 3, l, l)
	box(l, l * 3, l)
	box(l, l, l * 3)

}
