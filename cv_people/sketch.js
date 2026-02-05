const QUALITY = "low"

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

function preload() {
	for (const head of cv) {
		console.log ("Loading head: ", head);
		const headModel = loadModel(`${head}/${QUALITY}/head.obj`, false);
		const headTexture = loadImage(`${head}/${QUALITY}/head.jpg`);
		heads.push({
			model: headModel,
			texture: headTexture,
		})
	}
}

function setup() {
	createCanvas(windowWidth, windowHeight, WEBGL)
	for (const head of heads) {
		head.model = flipY(head.model)
		head.aabb = calcBouningBox(head.model)
	}
}

function windowResized() {
	resizeCanvas(windowWidth, windowHeight)
}

function draw() {
	background(0)


	rotateX(map(mouseY, 0, height, -PI/2, PI/2))
	rotateY(map(mouseX, 0, width,  PI/2, -PI/2))

	const axisLength = max(height, width) / 3
	strokeWeight(1)
	stroke(255, 0, 0)
	line(-axisLength, 0, 0, axisLength, 0, 0)
	stroke(0, 255, 0)
	line(0, -axisLength, 0, 0, axisLength, 0)
	stroke(0, 0, 255)
	line(0, 0, -axisLength, 0, 0, axisLength)


	const numH = 6
	const numV = 4
	const spacing = 140
	const offsX = -(numH-1) * spacing / 2
	const offsZ = -(numV-1) * spacing / 2


	for (let i = 0; i < numH; i++) {
		for (let j = 0; j < numV; j++) {
			index = i * numV + j
			const head = heads[index]
			const hx = offsX + i * spacing
			const hz = offsZ + j * spacing

			push()

			const oy = sin(frameCount * 0.05 + i * 0.4 + j * 0.4) * 50
			translate(hx, oy, hz)
			scale(340)

			rotateY(sin(frameCount * 0.02 + i * 0.1 + j * 0.1) * PI)


			translate(-head.aabb.x, -head.aabb.y, -head.aabb.z)
			texture(head.texture)
			noStroke()
			textureMode(NORMAL)
			model(head.model)


			// Bouning box
			if (mouseIsPressed){
				noFill()
				stroke(255, 255, 0)
				translate(head.aabb.x, head.aabb.y, head.aabb.z)
				box(head.aabb.width, head.aabb.height, head.aabb.depth)
			}

			pop()
		}
	}
}


function flipY(model) {
	const vertices = model.vertices
	for (const vertex of vertices) {
		vertex.y = -vertex.y
	}
	return model
}

function calcBouningBox(model) {
	const vertices = model.vertices
	let minX = Infinity
	let maxX = -Infinity
	let minY = Infinity
	let maxY = -Infinity
	let minZ = Infinity
	let maxZ = -Infinity

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
		minX: minX,
		maxX: maxX,
		minY: minY,
		maxY: maxY,
		minZ: minZ,
		maxZ: maxZ,
		width: maxX - minX,
		height: maxY - minY,
		depth: maxZ - minZ,
		x: (minX + maxX) / 2,
		y: (minY + maxY) / 2,
		z: (minZ + maxZ) / 2,
	}
	return aabb
}
