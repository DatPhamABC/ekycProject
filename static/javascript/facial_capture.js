$(document).ready(function () {
    var video = document.getElementById('video');
    var canvas = document.getElementById('image_canvas');
    var context = canvas.getContext('2d');
    var videoCanvas = document.getElementById("videoCanvas");
    var videoContext = videoCanvas.getContext('2d');
    var w = 640, h = 480;

    // Get access to the camera!
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Not adding `{ audio: true }` since we only want video now
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            video.srcObject = stream;
            video.play();
        });
    }

    canvas.width = video.width;
    canvas.height = video.height;

    context.translate(canvas.width, 0);
    context.scale(-1, 1);

    video.onplay = function() {
        setTimeout(drawImage , 1000/60);
    };

    // Trigger photo take
    document.getElementById("send").addEventListener("click", function() {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
    });

    document.getElementById("image_submit").addEventListener("click", function(){
        canvas.toBlob(upload, "image/jpeg"); // convert to file and execute function `upload`
    })

    function upload(file) {
        // create form and append file
        var formData =  new FormData();
        formData.append("snap", file);
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // create AJAX requests POST with file
        $.ajax({
            headers: {'X-CSRFToken': csrftoken},
            type: 'POST',
            url: '/signup/facial_capture',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function(data){
                if (data.status == 0) {
                    console.log('status failed');
                    window.location.reload();
                } else {
                    console.log('status ok');
                    window.location.href = '/login';
                }
            },
        })
    }

    function drawImage(){
        videoCanvas.width = video.videoWidth;
        videoCanvas.height = video.videoHeight;

        videoContext.translate(videoCanvas.width, 0);
        videoContext.scale(-1, 1);
        videoContext.drawImage(video, 0, 0, videoCanvas.width, videoCanvas.height);

        var faceArea = 300;
        var pX=videoCanvas.width/2 - faceArea/2;
        var pY=videoCanvas.height/2 - faceArea/2;

        videoContext.rect(pX,pY,faceArea,faceArea);
        videoContext.lineWidth = "6";
        videoContext.strokeStyle = "red";
        videoContext.stroke();


        setTimeout(drawImage , 1000/60);
    }
});