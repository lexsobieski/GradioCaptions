import urllib
from .db_connection import videos_ref


def youtube_link_to_id(link):
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(link)
        return parse_qs(parsed.query)['v'][0]
    except (KeyError, IndexError):
        raise ValueError(f"Invalid YouTube URL: {link}")

def get_video_embed_by_id(video_id):
    return f"""
    <div class="container">
    <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen class="video"></iframe>
    </div>"""


def get_video_link_by_pointer(pointer):
    video_link = videos_ref.child(str(pointer)).get()
    return video_link
