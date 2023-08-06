$(document).ready( function() {
    var options = {
        audioWidth: 200,
        success: function (mediaElement, domObject) {

           $('.sermon-player').bind("click", function(event){
            var parent_container = $(this).attr('rel');
            var target = parent_container + " .mejs-container";
            console.log(target);
            console.log($(target).attr('class'));
            $(target).gtoggle();
});

        }
    }
$('video,audio').mediaelementplayer(options);

function checkFile(event) {
        var fileElement = document.getElementById("form-widgets-audio_file-input");
        var fileExtension = "";
        if (fileElement.value.lastIndexOf(".") > 0) {
            fileExtension = fileElement.value.substring(fileElement.value.lastIndexOf(".") + 1, fileElement.value.length);
        }
        if (fileExtension == "mp3") {
            return true;
        }
        else {
            alert("You must select a mp3 file for upload");
            return false;
        }
    }

$("form#form").bind("submit",checkFile);

});
