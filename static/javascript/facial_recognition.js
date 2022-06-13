//$(document).ready(function () {
//    var video = document.getElementById('video');
//    var canvas = document.getElementById('image_canvas');
//    var context = canvas.getContext('2d');
//    var w = 640, h = 480;
//
//    // Get access to the camera!
//    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
//        // Not adding `{ audio: true }` since we only want video now
//        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
//            // video.src = window.URL.createObjectURL(stream);
//            video.srcObject = stream;
//            video.play();
//        });
//    }
//
//    // Trigger photo take
//    document.getElementById("send").addEventListener("click", function() {
//        context.translate(w, 0);
//        context.scale(-1, 1);
//        context.drawImage(video, 0, 0, w, h); // copy frame from <video>
//    });
//
//    document.getElementById("image_submit").addEventListener("click", function(){
//        canvas.toBlob(upload, "image/jpeg"); // convert to file and execute function `upload`
//    })
//
//    function upload(file) {
//        // create form and append file
//        var formData =  new FormData();
//        formData.append("snap", file);
//        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
//
//        // create AJAX requests POST with file
//        $.ajax({
//            headers: {'X-CSRFToken': csrftoken},
//            type: 'POST',
//            url: '/signup/facial_capture',
//            data: formData,
//            cache: false,
//            processData: false,
//            contentType: false,
//            enctype: 'multipart/form-data',
//            success: function(data){
//                alert('response received');
//                if (data.status == 0) {
//                    console.log('status failed');
//                    window.location.reload();
//                } else {
//                    console.log('status ok');
//                    window.location.href = '/login';
//                }
//            },
//        })
//    }
//});


$(document).ready(function () {
    // Elements for taking the snapshot
    var video = document.getElementById('video');

    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');

//    var image = document.getElementById('image');
//    var image64 = document.getElementById('image64');

    var frames = 0;
    var start = window.performance.now();

    // Get access to the camera!
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Not adding `{ audio: true }` since we only want video now
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            //video.src = window.URL.createObjectURL(stream);
            video.srcObject = stream;
            video.play();

            //console.log('setInterval')
            window.setInterval(function() {
                //context.drawImage(video, 0, 0);
                context.drawImage(video, 0, 0, 320, 240); // better use size because camera may gives data in different size then <video> is displaying

//                image64.src = canvas.toDataURL();
                canvas.toBlob(upload, "image/jpeg");
            }, 100);
        });
    }

//    // Trigger photo take
//    document.getElementById("send").addEventListener("click", () => {
//        //context.drawImage(video, 0, 0);
//        context.drawImage(video, 0, 0, 320, 240); // better use size because camera may gives data in different size then <video> is displaying
//        image64.src = canvas.toDataURL();
//
//        canvas.toBlob(upload, "image/jpeg");
//    });

    function upload(file) {
        // create form
        var formData =  new FormData();

        // add file to form
        formData.append("snap", file);
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        var url = "/login/face-recognition"
        $.ajax({
            headers: {'X-CSRFToken': csrftoken},
            type: 'POST',
            url: url,
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function(data){
//                image.src = 'data:image/gif;base64,' + data;
//
                frames = frames + 1;
                var seconds = (window.performance.now() - start) / 1000;
                var fps = Math.round(frames / seconds);
                console.log(fps);

                if (data.status == 1) {
                    console.log('status ok');
                    window.location.href = '/student';
                }
//                $(img).attr('src', 'data:image/gif;base64,' + data);
//                $(img).appendTo('#image_id');
//                image.appendTo('#image');
//                alert('response received');
//                if (data.status == 0) {
//                    console.log('status failed');
//                    window.location.reload();
//                } else {
//                    console.log('status ok');
//                    window.location.href = '/login';
//                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                console.log(xhr.responseText);
            }
        })
    }
});