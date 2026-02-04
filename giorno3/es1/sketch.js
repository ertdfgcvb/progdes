function setup() {
	createCanvas(400, 400)
	background(200)
}

function draw(){


	fill(random(255), random(255), random(255))
	textSize(136)
	textAlign(CENTER, CENTER)
	// textFont('Courier New')
	text("AG", width/2, height/2)

	let c = get(0, 0, width, height)


	translate(width/2, height/2)
	rotate(mouseX * 0.001)
	imageMode(CENTER)
	image(c, mouseX * 0.1, mouseY * 0.1, c.width * 1.1, c.height * 1.1)


}