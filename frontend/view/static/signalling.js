RTCPeerConnection = window.RTCPeerConnection || /*window.mozRTCPeerConnection ||*/ window.webkitRTCPeerConnection;
RTCSessionDescription = /*window.mozRTCSessionDescription ||*/ window.RTCSessionDescription;
RTCIceCandidate = /*window.mozRTCIceCandidate ||*/ window.RTCIceCandidate;

function signal(url, onStream, onError, onClose, onMessage) {
    if ("WebSocket" in window) {
        console.log("opening web socket: " + url);
        var ws = new WebSocket(url);
        var pc;

        ws.onopen = function () {
            /* First we create a peer connection */
            var config = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]};
            var options = {optional: []};
            pc = new RTCPeerConnection(config, options);

            pc.onicecandidate = function (event) {
                if (event.candidate) {
                    var candidate = {
                        sdpMLineIndex: event.candidate.sdpMLineIndex,
                        sdpMid: event.candidate.sdpMid,
                        candidate: event.candidate.candidate
                    };
                    var request = {
                        what: "addIceCandidate",
                        data: JSON.stringify(candidate)
                    };
                    ws.send(JSON.stringify(request));
                } else {
                    console.log("end of candidates.");
                }
            };

            if ('ontrack' in pc) {
                pc.ontrack = function (event) {
                    onStream(event.streams[0]);
                };
            } else {  // onaddstream() deprecated
                pc.onaddstream = function (event) {
                    onStream(event.stream);
                };
            }

            pc.onremovestream = function (event) {
                console.log("the stream has been removed: do your stuff now");
            };

            pc.ondatachannel = function (event) {
                console.log("a data channel is available: do your stuff with it");
                // For an example, see https://www.linux-projects.org/uv4l/tutorials/webrtc-data-channels/
            };

            /* kindly signal the remote peer that we would like to initiate a call */
            var request = {
                what: "call",
                options: {
                    force_hw_vcodec: true,
                    vformat: 65 /* 1280x720@15fps */
                }
            };
            console.log("send message " + JSON.stringify(request));
            ws.send(JSON.stringify(request));
        };

        ws.onmessage = function (evt) {
            var msg = JSON.parse(evt.data);
            var what = msg.what;
            var data = msg.data;

            console.log("received message " + JSON.stringify(msg));

            switch (what) {
                case "offer":
                    var mediaConstraints = {
                        optional: [],
                        mandatory: {
                            OfferToReceiveAudio: true,
                            OfferToReceiveVideo: true
                        }
                    };
                    pc.setRemoteDescription(new RTCSessionDescription(JSON.parse(data)),
                            function onRemoteSdpSuccess() {
                                pc.createAnswer(function (sessionDescription) {
                                    pc.setLocalDescription(sessionDescription);
                                    var request = {
                                        what: "answer",
                                        data: JSON.stringify(sessionDescription)
                                    };
                                    ws.send(JSON.stringify(request));
                                }, function (error) {
                                    onError("failed to create answer: " + error);
                                }, mediaConstraints);
                            },
                            function onRemoteSdpError(event) {
                                onError('failed to set the remote description: ' + event);
                                ws.close();
                            }
                    );

                    var request = {
                        what: "generateIceCandidates"
                    };
                    ws.send(JSON.stringify(request));
                    break;

                case "answer":
                    break;

                case "message":
                    if (onMessage) {
                        onMessage(msg.data);
                    }
                    break;

                case "iceCandidates":
                    var candidates = JSON.parse(msg.data);
                    for (var i = 0; candidates && i < candidates.length; i++) {
                        var elt = candidates[i];
                        var candidate = new RTCIceCandidate({sdpMLineIndex: elt.sdpMLineIndex, candidate: elt.candidate});
                        pc.addIceCandidate(candidate,
                                function () {
                                    console.log("IceCandidate added: " + JSON.stringify(candidate));
                                },
                                function (error) {
                                    console.error("addIceCandidate error: " + error);
                                }
                        );
                    }
                    break;
            }
        };

        ws.onclose = function (event) {
            console.log('socket closed with code: ' + event.code);
            if (pc) {
                pc.close();
                pc = null;
                ws = null;
            }
            if (onClose) {
                onClose();
            }
        };

        ws.onerror = function (event) {
            onError("An error has occurred on the websocket (make sure the address is correct)!");
        };

        this.hangup = function() {
            if (ws) {
                var request = {
                    what: "hangup"
                };
                console.log("send message " + JSON.stringify(request));
                ws.send(JSON.stringify(request));
            }
        };

    } else {
        onError("Sorry, this browser does not support Web Sockets. Bye.");
    }
}
