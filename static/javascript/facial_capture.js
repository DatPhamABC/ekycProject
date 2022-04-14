$(document).ready(function () {
    var video = document.getElementById('video');
    var canvas = document.getElementById('image_canvas');
    var context = canvas.getContext('2d');
    var w = 640, h = 480;

    // Get access to the camera!
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Not adding `{ audio: true }` since we only want video now
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            // video.src = window.URL.createObjectURL(stream);
            video.srcObject = stream;
            video.play();
        });
    }

    // Trigger photo take
    document.getElementById("send").addEventListener("click", function() {
        context.translate(w, 0);
        context.scale(-1, 1);
        context.drawImage(video, 0, 0, w, h); // copy frame from <video>
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
                alert('response received');
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
});