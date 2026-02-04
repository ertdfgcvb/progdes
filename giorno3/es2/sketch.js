function setup() {
	createCanvas(400, 400)
}

function draw() {
	background(200)
	noFill()
	stroke(0)

	let px = mouseX
	let py = mouseY
	let s  = 10

	beginShape()
	vertex(px + 0.00 * s + random(-2,2), py + 0.00 * s + random(-2,2))
	vertex(px + 2.14 * s + random(-2,2), py + 0.00 * s + random(-2,2))
	vertex(px + 2.14 * s + random(-2,2), py + 5.14 * s + random(-2,2))
	vertex(px + 4.53 * s + random(-2,2), py + 2.61 * s + random(-2,2))
	vertex(px + 7.15 * s + random(-2,2), py + 2.61 * s + random(-2,2))
	vertex(px + 4.60 * s + random(-2,2), py + 5.24 * s + random(-2,2))
	vertex(px + 7.48 * s + random(-2,2), py + 10.0 * s + random(-2,2))
	vertex(px + 4.96 * s + random(-2,2), py + 10.0 * s + random(-2,2))
	vertex(px + 3.06 * s + random(-2,2), py + 6.81 * s + random(-2,2))
	vertex(px + 2.12 * s + random(-2,2), py + 7.96 * s + random(-2,2))
	vertex(px + 2.12 * s + random(-2,2), py + 10.0 * s + random(-2,2))
	vertex(px + 0.00 * s + random(-2,2), py + 10.0 * s + random(-2,2))
	endShape(CLOSE)


}