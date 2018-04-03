/**
* Author: Mario Bartolomé
* Date: Mar 27, 2018
*
*
* Gamepad acquisition and sender through WebSockets
**/

var haveEvents = 'GamepadEvent' in window;
var controllers = {};
var rAF = window.mozRequestAnimationFrame ||
    window.requestAnimationFrame||
    window.webkitRequestAnimationFrame;
var connection;
var manual = false;
var sendingAxisEvent = "axisInput";

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
    var d = document.createElement("div");
    d.setAttribute("id", "manual_mode" + e.gamepad.index);
    var enable_control = document.createElement("button");
    enable_control.setAttribute("id", "bt_manual" + e.gamepad.index);
    var t = document.createTextNode("Enable Manual");
    enable_control.appendChild(t);
    enable_control.style.backgroundColor = "green";
    enable_control.style.color = "white";
    d.appendChild(enable_control);
    document.body.appendChild(d);
    enable_control.addEventListener("click", manageConnection.bind(this, e.gamepad));
}

function disconnecthandler(e){
    if(manual) {
        manageConnection(e.gamepad);
    }
    removegamepad(e.gamepad);
    var d = document.getElementById("manual_mode" + e.gamepad.index);
    document.body.removeChild(d);
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
    for (i=0; i < 5; i++) {
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
    var axisValues = [{}];
    for (j in controllers) {
        var controller = controllers[j];
        var d = document.getElementById("controller" + j);

        var axes = d.getElementsByClassName("axis");
        for (var i=0; i < 5; i++) {
            var a = axes[i];
            a.innerHTML = i + ": " + controller.axes[i].toFixed(4);
            var axisValue = controller.axes[i] + 1;
            a.setAttribute("value", axisValue);
            axisValues[0]["Ax"+i] = map(axisValue);

        }
        // console.log(JSON.stringify(axisValues));
        if(manual){
            // connection.send(JSON.stringify())
            // console.warn('Trying to send through WS!!' + axisValues)
            connection.emit(sendingAxisEvent, axisValues);
        }
    }
    rAF(updateStatus);
}

function map (num) {
    return num * 1000 / 2 + 1000;
}

function manageConnection(gamepad){
    var btn = document.getElementById("bt_manual" + gamepad.index);

    if(!manual) {
        btn.style.backgroundColor = "gray";
        btn.firstChild.nodeValue = "Connecting...";
        btn.disabled = true;
        connection = io.connect();
        console.log("~WebSocket to " + location.host + "~ Connecting... ");
    } else{
        if(connection != null && connection.connected){
            connection.emit('disconnect');
            connection.disconnect();

        }
    }

    connection.on('disconnect', function() {
        console.log("~WebSocket to " + location.host + "~ Closed");
        manual = false;
        allowRemoteCtrlButton(gamepad);

    });


    connection.on('connect', function() {
        console.log("~WebSocket to " + location.host + "~ Connected!");
        manual = true;
        btn.disabled = false;
        btn.style.backgroundColor = "red";
        btn.firstChild.nodeValue = "Disable Manual";
    });

    connection.on('connect_error', connectionError.bind(this, gamepad));
}

function connectionError(gamepad){

    console.error("~WebSocket to " + location.host + "~ Error: Connecting to server. ");
    alert("Couldn't enable Manual Mode.");
    manual = false;
    connection.close();
    allowRemoteCtrlButton(gamepad);
}

function allowRemoteCtrlButton(gamepad){
    var btn = document.getElementById("bt_manual" + gamepad.index);
    btn.style.backgroundColor = "green";
    btn.firstChild.nodeValue = "Enable Manual";
    btn.disabled = false;
}

if (haveEvents) {
    window.addEventListener("gamepadconnected", connecthandler);
    window.addEventListener("gamepaddisconnected", disconnecthandler);
} else {
    setInterval(scangamepads, 500);
}
