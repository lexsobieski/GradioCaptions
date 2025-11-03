yt_init_js = """
<script src="https://www.youtube.com/iframe_api"></script>
<script>
window.onYouTubeIframeAPIReady = function() {
    window.ytPlayer = new YT.Player('yt-container', {
        height: '360',
        width: '640',
        playerVars: { 
            origin: window.location.origin, 
            playsinline: 1 
        },
        events: {
            'onReady': function(event) {
                window.ytPlayerReady = true;
            }
        }
    });
};
</script>
"""