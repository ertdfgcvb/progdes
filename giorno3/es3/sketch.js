const k = [
	0.00, 0.00,
	2.14, 0.00,
	2.14, 5.14,
	4.53, 2.61,
	7.15, 2.61,
	4.60, 5.24,
	7.48, 10.0,
	4.96, 10.0,
	3.06, 6.81,
	2.12, 7.96,
	2.12, 10.0,
	0.00, 10.0,
]

function setup() {
	createCanvas(400, 400)
}

function draw() {
	background(200)
	stroke(0)

	const num = 60
	for (let i=0; i<num; i++) {
		push()
		translate(width/2, height/2)
		rotate(sin((frameCount + (i + 1)) * 0.03))
		const s = 10 + num - i * 0.8
		beginShape()
		for (let i=0; i<k.length; i+=2) {
			const x1 = (k[i  ] - 3.25) * s
			const y1 = (k[i+1] - 6) * s
			vertex(x1, y1)
		}
		endShape(CLOSE)
		pop()
	}
}
