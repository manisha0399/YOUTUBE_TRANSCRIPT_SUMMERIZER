// Initializing Constants for use

const download_button = document.getElementById("download_button");

function downloadScript() {
    // Creating hyperlink element with tagName "a"
    var element = document.createElement('a');
    // Setting HREF to the script text
    element.setAttribute('href', 'data:application/octet-stream; data:text/plain;charset=utf-8,' +
        encodeURIComponent(download_info.script));
    // Setting download file name in the format "script_videoID_algo_percent.txt"
    element.setAttribute('download', "script_" +
        download_info.video_id + "_" + download_info.video_algo + "_" + download_info.video_percent + ".txt");
    // Making the hyperlink invisible and appending it to the body
    element.style.display = 'none';
    document.body.appendChild(element);

    // Clicking hyperlink to download script into text file and removing the invisible hyperlink.
    element.click();
    document.body.removeChild(element);
}