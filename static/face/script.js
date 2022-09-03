const video = document.getElementById('videoShow');
const angry = document.getElementById('angry');
const disgusted = document.getElementById('disgusted');
const fearful = document.getElementById('fearful');
const happy = document.getElementById('happy');
const neutral = document.getElementById('neutral');
const sad = document.getElementById('sad');
const surprised = document.getElementById('surprised');

Promise.all([
    // faceapi.nets.ssdMobilenetv1.loadFromUri('../static/models'),
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/face/models'),
    faceapi.nets.faceLandmark68Net.loadFromUri('/static/face/models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('/static/face/models'),
    faceapi.nets.faceExpressionNet.loadFromUri('/static/face/models'),
]).then(startVideo);

function startVideo() {
    // navigator.mediaDevices.getUserMedia(
    //     {video: {}}).then(function (stream) {
    //     video.srcObject = stream;
    // }, function (err) {
    //     console.error(err);
    // })
    video.src = '/media/mp4/interviewer.mp4';
}

video.addEventListener('play', () => {
    // const canvas = faceapi.createCanvasFromMedia(video)
    // document.body.insertBefore(canvas, document.getElementById('table'))
    // document.body.append(canvas)
    // const displaySize = {width: video.width, height: video.height}
    // faceapi.matchDimensions(canvas, displaySize)
    setInterval(async () => {
        const detections = await faceapi.detectSingleFace(video,
            new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceExpressions()
        // console.log(detections)
        if (detections) {
            const obj = detections['expressions']
            console.log(obj)
            angry.innerHTML = obj['angry'].toFixed(4)
            disgusted.innerHTML = obj['disgusted'].toFixed(4)
            fearful.innerHTML = obj['fearful'].toFixed(4)
            happy.innerHTML = obj['happy'].toFixed(4)
            neutral.innerHTML = obj['neutral'].toFixed(4)
            sad.innerHTML = obj['sad'].toFixed(4)
            surprised.innerHTML = obj['surprised'].toFixed(4)
        }
        // const resizeDetections = faceapi.resizeResults(detections, displaySize)
        // canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
        // faceapi.draw.drawDetections(canvas, resizeDetections)
        // faceapi.draw.drawFaceLandmarks(canvas, resizeDetections)
        // faceapi.draw.drawFaceExpressions(canvas, resizeDetections)
    }, 100)
});
