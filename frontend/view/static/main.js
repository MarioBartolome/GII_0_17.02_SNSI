(function () {
    var signalObj = null;

    window.addEventListener('DOMContentLoaded', function () {
        var isStreaming = false;
        var start = document.getElementById('start');
        var stop = document.getElementById('stop');
        var video = document.getElementById('v');

        start.addEventListener('click', function (e) {
            var address = document.getElementById('address').textContent;
            var protocol = location.protocol === "https:" ? "wss:" : "ws:";
            var wsurl = protocol + '//' + address;

            if (!isStreaming) {
                signalObj = new signal(wsurl,
                        function (stream) {
                            console.log('got a stream!');

                            video.srcObject = stream;
                            video.play();
                        },
                        function (error) {
                            alert(error);
                        },
                        function () {
                            console.log('websocket closed. bye bye!');
                            video.srcObject = null;
                            isStreaming = false;
                        },
                        function (message) {
                            alert(message);
                        }
                );
            }
        }, false);

        stop.addEventListener('click', function (e) {
            if (signalObj) {
                signalObj.hangup();
                signalObj = null;
            }
        }, false);

        // Wait until the video stream can play
        video.addEventListener('canplay', function (e) {
            if (!isStreaming) {
                isStreaming = true;
            }
        }, false);


    });
})();
