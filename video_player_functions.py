import re


def youtube_link_to_id(link):
    video_id = re.findall("=(.*?)&", link)
    if len(video_id) == 0:
        video_id = re.findall("=(.*)", link)
    return video_id[0]


def get_youtube_video(video_id):
    return f"""
    <div class="container">
    <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen class="video"></iframe>
    </div>"""
