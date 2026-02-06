const NUM_H = 19
const NUM_V = 19
const NUM_RAND = Math.floor(Math.random() * 3) + 1
const SPACING = 35
const MODEL_SCALE = 600
const DEF_ROTY_ANGLE = -Math.PI/2
const DEF_OFFS_Y = -0.30 // Unità mesh!

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

const randomSel = []
for (let i = 0; i < NUM_RAND; i++) {
	const cvHead = Math.floor(Math.random() * cv.length)
	const head = cv.splice(cvHead, 1)[0]
	randomSel.push(head)
}


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

	textFont(font)
	textSize(16)

	const QUALITY = "low"
	const PATH = "../../"

	loadHeads(heads, randomSel, PATH, QUALITY)
}

function draw() {
	background(0)

	push()

	rotateX(map(mouseY, 0, height, -PI*0.3, PI*0.3))
	rotateY(map(mouseX, 0, width,  PI, -PI))

	if (drawAxes) {
		const axisLength = min(height, width)
		drawAxis(axisLength, axisLength, axisLength)
	}

	const offsX = -(NUM_H-1) * SPACING / 2
	const offsZ = -(NUM_V-1) * SPACING / 2

	const nx = frameCount * 0.0033
	const ny = frameCount * 0.0032


	for (let i = 0; i < NUM_H; i++) {
		for (let j = 0; j < NUM_V; j++) {
			index = (i * NUM_V + j) % heads.length
			const head = heads[index]
			const hx = offsX + i * SPACING
			const hz = offsZ + j * SPACING

			const oy = map(noise(nx + i * 0.1, ny + j * 0.1), 0, 1, -70, 70)
			const ry = sin(frameCount * 0.02 + i * 0.2 + j * 0.2) * HALF_PI

			push()

			// Posizionmaneto nello spazio
			translate(hx, oy, hz)

			scale(MODEL_SCALE)

			// Tutti i modelli hanno un'altezza diversa,
			// lo spostamento verticale deve essere calcolato in base all'altezza della bounding box - offset
			translate(0, head.aabb.height/2 + DEF_OFFS_Y, 0)
			rotateY(ry + DEF_ROTY_ANGLE)

			push()
			translate(-head.aabb.x, -head.aabb.y, -head.aabb.z)
			noStroke()
			texture(head.texture)
			textureMode(NORMAL)
			model(head.model)
			pop()


			if (drawBouningBox){
				noFill()
				stroke(255)
				box(head.aabb.width, head.aabb.height , head.aabb.depth)
			}
			if (drawAxes) {
				drawAxis(head.aabb.width * 1.5, head.aabb.height * 1.5, head.aabb.depth * 1.5)
			}

			pop()
		}
	}
	pop()

	// Loader
	let str = ""
	for (const head of heads) {
		if (!head.loaded) {
			str += "Loading: " + head.name + "\n"
		}
	}

	if (str.length > 0) {
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

function loadHeads(target, source, path = '../../', quality = 'low') {
	for (const head of source) {
		console.log ("Loading head: ", head)
		const headModel = loadModel(`${path}/${head}/${quality}/head.obj`, {
			normalize : false,
			successCallback: (model) => {
				headData.model = flipY(model)
				headData.aabb = calcBouningBox(model)
				headData.loaded = true
				console.log (headData.aabb)
			},
			errorCallback: (error) => {
				console.error("Error loading model: ", error)
			}
		})
		const headTexture = loadImage(`${path}/${head}/${quality}/head.jpg`)

		const headData = {
			model: headModel,
			texture: headTexture,
			aabb: calcBouningBox(headModel),
			loaded: false,
			name: head,
		}
		target.push(headData)
	}
}

function calcBouningBox(model) {

	if (!model) return new AABB()

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

	return new AABB(
		(minX + maxX) / 2,
		(minY + maxY) / 2,
		(minZ + maxZ) / 2,
		maxX - minX,
		maxY - minY,
		maxZ - minZ,
	)
}

class AABB {
	constructor(x = 0, y = 0, z = 0, width = 0, height = 0, depth = 0) {
		this.x = x
		this.y = y
		this.z = z
		this.width = width
		this.height = height
		this.depth = depth
	}
 }
