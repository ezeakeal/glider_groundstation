var container, stats;
var camera, cameraTarget, scene, renderer;
var mouseX = 0, mouseY = 0;

var gliderObj;
var gliderArrow;
var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

de2ra = function(degree){ 
    return degree*(Math.PI/180); 
}


function init() {
    // Getting the container for later..
    container = document.getElementById( 'glider_div' );

    // Camera setup
    camera = new THREE.PerspectiveCamera( 45, container.clientWidth / container.clientHeight, 1, 2000 );
    camera.position.z = -15;
    camera.position.y = 7;
    camera.position.x = -10;
    cameraTarget = new THREE.Vector3( 0, 0, 0 );

    // scene
    scene = new THREE.Scene();

    // Add lighting
    var ambient = new THREE.AmbientLight( 0xAAAAAA );
    scene.add( ambient );
    var directionalLight = new THREE.DirectionalLight( 0xffeedd );
    directionalLight.position.set( 2, 5, 7 ).normalize();
    scene.add( directionalLight );

    // Setup loading manager
    var manager = new THREE.LoadingManager();
    manager.onProgress = function ( item, loaded, total ) {
        console.log( item, loaded, total );
    };

    // model
    var loader = new THREE.OBJMTLLoader( manager );
    loader.load( '/static/glider/glider.obj', '/static/glider/glider.mtl', function ( object ) {
        object.setTran
        scene.add( object );
        gliderObj = object;
        // gliderObj.rotation.order = 'ZYX';
    }, function ( xhr ) {
        if ( xhr.lengthComputable ) {
            var percentComplete = xhr.loaded / xhr.total * 100;
            console.log( Math.round(percentComplete, 2) + '% downloaded' );
        }
    }, function ( xhr ) {
    } );

    // Render arrow for glider direction
    var dir = new THREE.Vector3( 0, 0, 0 );
    dir.normalize(); //normalize the direction vector (convert to vector of length 1)
    var origin = new THREE.Vector3( 0, 0, 0 );

    northArrow = new THREE.ArrowHelper( new THREE.Vector3( 0, 0, 1 ), origin, 3, 0x00ff00 );
    scene.add( northArrow );

    gliderArrow = new THREE.ArrowHelper( dir, origin, 5, 0xffff00 );
    scene.add( gliderArrow );

    // YAW
    var plane = new THREE.Mesh(
        new THREE.PlaneBufferGeometry( 6, 6 ),
        new THREE.MeshPhongMaterial( { color: 0xFF0000, opacity: 0.2, transparent: true } )
    );
    plane.rotation.x = -Math.PI/2;
    scene.add( plane );
    // ROLL
    var plane = new THREE.Mesh(
        new THREE.PlaneBufferGeometry( 6, 10 ),
        new THREE.MeshPhongMaterial( { color: 0x00FF00, opacity: 0.2, transparent: true } )
    );
    plane.rotation.z = -Math.PI/2;
    plane.position.x = 5;
    scene.add( plane );
    // PITCH
    var plane = new THREE.Mesh(
        new THREE.PlaneBufferGeometry( 3, 6 ),
        new THREE.MeshPhongMaterial( { color: 0x0000FF, opacity: 0.2, transparent: true } )
    );
    plane.rotation.y = Math.PI/2;
    plane.position.z = -1.5;
    scene.add( plane );

    // Setup the Renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setSize( container.clientWidth, container.clientHeight );

    renderer.shadowCameraNear = 3;
    renderer.shadowCameraFar = 40;
    renderer.shadowCameraFov = 45;
    container.appendChild( renderer.domElement );

    controls = new THREE.OrbitControls( camera, renderer.domElement );

    // Setup the stats item
    stats = new Stats();
    stats.domElement.style.position = 'absolute';
    stats.domElement.style.top = '0px';
    container.appendChild( stats.domElement );
    
    document.addEventListener( 'mousemove', onDocumentMouseMove, false );
    window.addEventListener( 'resize', onWindowResize, false );
}


function onWindowResize() {
    container = document.getElementById( 'glider_div' );
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( container.clientWidth, container.clientHeight );
}

function animate() {
    requestAnimationFrame( animate );
    render(TELEMETRY); // TELEMETRY is global
    stats.update();
}

function render(telemJSON) {
    if ('orientation' in telemJSON) {
        if (gliderObj) {
            // https://gist.github.com/trevordixon/5783321
            // orientation = [roll,pitch,yaw]
            // X:PITCH Y:YAW Z:ROLL
            gliderObj.rotation.z = de2ra(parseFloat(telemJSON['orientation'][0]));
            gliderObj.rotation.x = -1 * de2ra(parseFloat(telemJSON['orientation'][1]));
            gliderObj.rotation.y = -1 * de2ra(parseFloat(telemJSON['orientation'][2]));
        }
        if (gliderArrow){
            // Update the heading arrow
            var dir = new THREE.Vector3(
                Math.sin(-1 * de2ra(parseFloat(telemJSON['heading'][0]))),
                Math.sin(de2ra(parseFloat(telemJSON['heading'][1]))),
                Math.cos(de2ra(parseFloat(telemJSON['heading'][0])))
            );
            gliderArrow.setDirection(dir)

        }
        camera.lookAt( cameraTarget );
        renderer.render( scene, camera );
    }
}

function onDocumentMouseMove( event ) {
}