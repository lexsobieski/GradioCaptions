import urllib
from Functions.db_connection import default_app


def get_youtube_player_html():
    """Returns the static HTML container for YouTube player (API loaded in page head)"""
    return """
<div style="margin:0 auto; width: fit-content;">
  <div id="yt-container" style="width: 640px; height: 360px;"></div>
</div>
"""


def youtube_link_to_id(link):
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(link)
        if parsed.hostname in ('youtu.be',):
            return parsed.path.lstrip('/')
        return parse_qs(parsed.query)['v'][0]
    except (KeyError, IndexError):
        raise ValueError(f"Invalid YouTube URL: {link}")


def get_video_embed_by_id(video_id):
    """Returns just the video ID - actual loading happens via JavaScript in main_page"""
    return video_id


# ADC-IMPLEMENTS: <gc-feature-assignment-01>
def get_video_link_by_pointer(pointer, show_incomplete_only):
    """Get video link with optional incomplete-only filtering.

    Args:
        pointer: Video index in the database
        show_incomplete_only: If True, skip videos marked as complete

    Returns:
        Video URL string, or None if the video is filtered out
    """
    video = default_app.database().child("videos").child(str(pointer)).get().val()
    if video is None:
        return None
    if show_incomplete_only and video.get("complete", False):
        return None
    return video["url"]


def change_video_completion_status(is_complete, video_pointer):
    default_app.database().child("videos").child(str(video_pointer)).child("complete").set(is_complete)


def get_number_of_videos():
    n_videos = len(default_app.database().child("videos").get().val())
    return n_videos
