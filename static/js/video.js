let video;
let canvas;
let context;
let outputImage;
let streamActive = false;
let stream;

window.onload = function() {
    video = document.createElement('video');
    video.setAttribute("style", "display: none;");
    document.body.appendChild(video);

    outputImage = document.getElementById('outputImage');
    canvas = document.createElement('canvas');
    context = canvas.getContext('2d');

    document.getElementById('videoElement').onclick = toggleStream;
};

function toggleStream() {
    console.log("Button pressed");
    if (streamActive) {
        stopStream();
    } else {
        startStream();
    }
}

function startStream() {
    if (!current_webcam) {
        console.error("No webcam selected.");
        return;
    }

    let constraints = {
        video: { deviceId: { exact: current_webcam } }
    };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(newStream => {
            stream = newStream;
            video.srcObject = stream;
            video.play();
            streamActive = true;
            setInterval(captureFrame, 100); // Capture frame every 100ms
        })
        .catch(err => {
            console.error("Error accessing webcam:", err);
        });
}

function stopStream() {
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
    streamActive = false;
}

function captureFrame() {
    if (!streamActive) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

    canvas.toBlob(sendFrame, 'image/jpeg');
}

function sendFrame(blob) {
    let formData = new FormData();
    formData.append('frame', blob);

    fetch('/yolo', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        let imageUrl = URL.createObjectURL(blob);
        outputImage.src = imageUrl;
    })
    .catch(err => {
        console.error("Error receiving processed frame:", err);
    });
}

document.getElementById('captureButton').onclick = captureAndSendImage;

function captureAndSendImage() {
    if (!streamActive) {
        alert("Stream is not active.");
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

    canvas.toBlob(function(blob) {
        let formData = new FormData();
        formData.append('image', blob);

        fetch('/analyse', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.task_id) {
                window.location.href = `/analyse/${data.task_id}`;
            } else {
                console.error("Invalid response from server");
            }
        })
        .catch(err => {
            console.error("Error sending image:", err);
        });
    }, 'image/jpeg');
}