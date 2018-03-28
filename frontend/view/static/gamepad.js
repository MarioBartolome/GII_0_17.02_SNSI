var haveEvents = 'GamepadEvent' in window;
var controllers = {};
var rAF = window.mozRequestAnimationFrame ||
    window.requestAnimationFrame||
    window.webkitRequestAnimationFrame;


function scangamepads() {
    var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
    for (var i = 0; i < gamepads.length; i++) {
        if (gamepads[i]) {
            if (!(gamepads[i].index in controllers)) {
                addgamepad(gamepads[i]);
            } else {
                controllers[gamepads[i].index] = gamepads[i];
            }
        }
    }
}

function connecthandler(e){
    addgamepad(e.gamepad);
}

function disconnecthandler(e){
    removegamepad(e.gamepad);
}

function removegamepad(gamepad){
    var d = document.getElementById("controller" + gamepad.index);
    document.body.removeChild(d);
    delete controllers[gamepad.index];
}

function addgamepad(gamepad) {
    controllers[gamepad.index] = gamepad;
    var d = document.createElement("div");
    d.setAttribute("id", "controller" + gamepad.index);
    var t = document.createElement("h4");
    t.appendChild(document.createTextNode(" Controller: " + gamepad.id));
    d.appendChild(t);

    var a = document.createElement("div");
    a.className = "axes";
    for (i=0; i<gamepad.axes.length; i++) {
        e = document.createElement("progress");
        e.className = "axis";
        //e.id = "a" + i;
        e.setAttribute("max", "2");
        e.setAttribute("value", "0");
        e.innerHTML = i;
        a.appendChild(e);
    }
    d.appendChild(a);
    document.body.appendChild(d);
    rAF(updateStatus);
}

function updateStatus(){
    scangamepads();
    for (j in controllers) {
        var controller = controllers[j];
        var d = document.getElementById("controller" + j);

        var axes = d.getElementsByClassName("axis");
        for (var i=0; i<controller.axes.length; i++) {
            var a = axes[i];
            a.innerHTML = i + ": " + controller.axes[i].toFixed(4);
            a.setAttribute("value", controller.axes[i] + 1);
        }
    }
    rAF(updateStatus);
}


if (haveEvents) {
    window.addEventListener("gamepadconnected", connecthandler);
    window.addEventListener("gamepaddisconnected", disconnecthandler);
} else {
    setInterval(scangamepads, 500);
}
