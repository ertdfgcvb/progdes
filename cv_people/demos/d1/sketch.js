const QUALITY = "low"
const CV_PATH = "../../"

const cv = [
	"cv1/biazquez_alessandro",
	"cv1/conconi_laura",
	"cv1/leon_krndija",
	"cv1/mignami_nicole",
	"cv1/seker_hakan",
	"cv1/stanga_vito",
	"cv1/videira_alice",
	"cv2/aktas_tuana",
	"cv2/balinzo_giada",
	"cv2/barattini_davide",
	"cv2/belli_nahele",
	"cv2/boredatti_olivia",
	"cv2/broggini_melissa",
	"cv2/degennaro_carla",
	"cv2/falcone_daniele",
	"cv2/guante_elisabeth",
	"cv2/hess_lorenzo",
	"cv2/lopopolo_greta",
	"cv2/maghetti_simone",
	"cv2/mazzola_luca",
	"cv2/panteni_laura",
	"cv2/riva_gregorio",
	"cv2/scofano_mattia",
	"cv2/vasti_riccardo",
]

const heads = []

let font
let drawAxes = false
let drawBouningBox = false

function preload() {
	font = loadFont("../Inter-Regular.otf")

}

function setup() {
	createCanvas(windowWidth, windowHeight, WEBGL)
	pixelDensity(displayDensity())


	for (const head of cv) {
		console.log ("Loading head: ", head)
		const headModel = loadModel(`${CV_PATH}/${head}/${QUALITY}/head.obj`, {
			normalize : false,
			successCallback: (model) => {
				headData.aabb = calcBouningBox(model)
				headData.loaded = true
			},
			errorCallback: (error) => {
				console.error("Error loading model: ", error)
			}
		})
		const headTexture = loadImage(`${CV_PATH}/${head}/${QUALITY}/head.jpg`)

		const headData = {
			model: headModel,
			texture: headTexture,
			aabb: calcBouningBox(headModel),
			loaded: false,
			name: head,
		}

		heads.push(headData)
	}

	textFont(font)
	textSize(16)
}

function draw() {
	background(0)
	textFont(font)

	push()

	rotateX(map(mouseY, 0, height, -PI/2, PI/2))
	rotateY(map(mouseX, 0, width,  PI/2, -PI/2))

	if (drawAxes) {
		const axisLength = min(height, width)
		drawAxis(axisLength, axisLength, axisLength)
	}

	const numH = 36
	const numV = 34
	const spacing = 140
	const offsX = -(numH-1) * spacing / 2
	const offsZ = -(numV-1) * spacing / 2

	for (let i = 0; i < numH; i++) {
		for (let j = 0; j < numV; j++) {
			index = (i * numV + j) % heads.length
			const head = heads[index]
			const hx = offsX + i * spacing
			const hz = offsZ + j * spacing

			push()

			const oy = sin(frameCount * 0.05 + i * 0.4 + j * 0.4) * 50
			translate(hx, oy, hz)
			scale(340)

			rotateY(sin(frameCount * 0.02 + i * 0.1 + j * 0.1) * PI)

			if (drawBouningBox){
				noFill()
				stroke(255)
				box(head.aabb.width, head.aabb.height, head.aabb.depth)
			}

			if (drawAxes) {
				drawAxis(head.aabb.width, head.aabb.height, head.aabb.depth)
			}


			translate(-head.aabb.x, -head.aabb.y, -head.aabb.z)
			texture(head.texture)
			noStroke()
			textureMode(NORMAL)
			model(head.model)

			pop()
		}
	}
	pop()

	// Loader
	let str = ""
	for (const head of heads) {
		if (!head.loaded) {
			str += "loading: " + head.name + "\n"
		}
	}

	if (str.length > 0) {
		camera()
		translate(-width/2, -height/2)
		text(str, 10, 30)
	}

}

function keyPressed() {
	if (key === 'a') {
		drawAxes = !drawAxes
	}
	if (key === 'b') {
		drawBouningBox = !drawBouningBox
	}
}

function windowResized() {
	resizeCanvas(windowWidth, windowHeight)
}

function drawAxis(xLen, yLen, zLen) {
	xLen = xLen / 2
	yLen = yLen / 2
	zLen = zLen / 2
	strokeWeight(1)
	stroke(255, 0, 0)
	line(-xLen, 0, 0, xLen, 0, 0)
	stroke(0, 255, 0)
	line(0, -yLen, 0, 0, yLen, 0)
	stroke(0, 0, 255)
	line(0, 0, -zLen, 0, 0, zLen)
}

function flipY(model) {
	const vertices = model.vertices
	for (const vertex of vertices) {
		vertex.y = -vertex.y
	}
	return model
}

function calcBouningBox(model) {
	if (!model) {
		return {x: 0, y: 0, z: 0, width: 0, height: 0, depth: 0}
	}
	let minX = Infinity
	let maxX = -Infinity
	let minY = Infinity
	let maxY = -Infinity
	let minZ = Infinity
	let maxZ = -Infinity

	const vertices = model.vertices

	for (const vertex of vertices) {
		const x = vertex.x
		const y = vertex.y
		const z = vertex.z

		minX = Math.min(minX, x)
		maxX = Math.max(maxX, x)
		minY = Math.min(minY, y)
		maxY = Math.max(maxY, y)
		minZ = Math.min(minZ, z)
		maxZ = Math.max(maxZ, z)
	}

	const aabb = {
		// minX: minX,
		// maxX: maxX,
		// minY: minY,
		// maxY: maxY,
		// minZ: minZ,
		// maxZ: maxZ,
		width: maxX - minX,
		height: maxY - minY,
		depth: maxZ - minZ,
		x: (minX + maxX) / 2,
		y: (minY + maxY) / 2,
		z: (minZ + maxZ) / 2,
	}
	return aabb
}
