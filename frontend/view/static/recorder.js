/*
*  Copyright (c) 2016 The WebRTC project authors. All Rights Reserved.
*
*  Use of this source code is governed by a BSD-style license
*  that can be found in the LICENSE file in the root of the source
*  tree.
*/

'use strict';

/* globals main */

// This code is adapted from
// https://rawgit.com/Miguelao/demos/master/mediarecorder.html

'use strict';

/* globals main, MediaRecorder */

let mediaSource = new MediaSource();
mediaSource.addEventListener('sourceopen', handleSourceOpen, false);
let mediaRecorder;
let recordedBlobs;
let sourceBuffer;

let videoField = document.getElementById('v');

let recordButton = document.querySelector('button#record');
let downloadButton = document.querySelector('button#download');
recordButton.onclick = toggleRecording;
downloadButton.onclick = download;


// window.isSecureContext could be used for Chrome

let isSecureOrigin = location.protocol === 'https:' ||
    location.hostname === 'localhost';
if (!isSecureOrigin) {
    alert('getUserMedia() must be run from a secure origin: HTTPS or localhost.' +
        '\n\nChanging protocol to HTTPS');
    location.protocol = 'HTTPS';
}

let stream = videoField.captureStream(); // frames per second
console.log('Started stream capture from videoField element: ', stream);

function handleSourceOpen(event) {
    console.log('MediaSource opened');
    sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"');
    console.log('Source buffer: ', sourceBuffer);
}

function handleDataAvailable(event) {
    if (event.data && event.data.size > 0) {
        recordedBlobs.push(event.data);
    }
}

function handleStop(event) {
    console.log('Recorder stopped: ', event);
}

function toggleRecording() {
    if (recordButton.textContent === 'Start Recording') {
        startRecording();
    } else {
        stopRecording();
        recordButton.textContent = 'Start Recording';
        downloadButton.disabled = false;
    }
}

// The nested try blocks will be simplified when Chrome 47 moves to Stable
function startRecording() {
    let options = {mimeType: 'video/webm'};
    recordedBlobs = [];
    try {
        mediaRecorder = new MediaRecorder(stream, options);
    } catch (e0) {
        console.log('Unable to create MediaRecorder with options Object: ', e0);
        try {
            options = {mimeType: 'video/webm,codecs=vp9'};
            mediaRecorder = new MediaRecorder(stream, options);
        } catch (e1) {
            console.log('Unable to create MediaRecorder with options Object: ', e1);
            try {
                options = 'video/vp8'; // Chrome 47
                mediaRecorder = new MediaRecorder(stream, options);
            } catch (e2) {
                alert('MediaRecorder is not supported by this browser.\n\n' +
                    'Try Firefox 29 or later, or Chrome 47 or later, with Enable experimental Web Platform features enabled from chrome://flags.');
                console.error('Exception while creating MediaRecorder:', e2);
                return;
            }
        }
    }
    console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
    recordButton.textContent = 'Stop Recording';
    downloadButton.disabled = true;
    mediaRecorder.onstop = handleStop;
    mediaRecorder.ondataavailable = handleDataAvailable;
    mediaRecorder.start(100); // collect 100ms of data
    console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {
    mediaRecorder.stop();
    console.log('Recorded Blobs: ', recordedBlobs);
}


function download() {
    let blob = new Blob(recordedBlobs, {type: 'video/webm'});
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = new Date().toISOString() + '.webm';
    document.body.appendChild(a);
    a.click();
    setTimeout(function() {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 100);
}