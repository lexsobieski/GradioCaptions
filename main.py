import gradio as gr
import pandas as pd
import re
import firebase_admin
from firebase_admin import db
import hashlib
import jsonlines
import json

cred_obj = firebase_admin.credentials.Certificate('key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://video-link-db-default-rtdb.europe-west1.firebasedatabase.app/"
    })
videos_ref = db.reference("/Videos")

with open("captions.jsonl") as file:
    captions = pd.read_json(file, lines=True)

# videos = ["Aj9SDSAOXf4", "c2ORbHSQ5pw"]
current_video = 0
video_links = videos_ref.get()[1:]

css = """
.container {
    position: relative;
    width: 100%;
    height: 0;
    padding-bottom: 56.25%;
}
.video {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}"""


def auth_function(username, password):
    return True


def youtube_link_to_id(link):
    video_id = re.findall("=(.*?)&", link)
    if len(video_id) == 0:
        video_id = re.findall("=(.*)", link)
    return video_id[0]


def get_captions(video_id):
    global captions
    captions_edit = captions[captions['file'] == video_id]
    captions_edit = captions_edit[['start_time', 'text', 'end_time']]
    captions_edit.columns = ["Start", "Text", "End"]
    return captions_edit


def get_next_captions():
    global current_video, video_links
    return get_captions(youtube_link_to_id(video_links[current_video]))
    # global current_video, videos
    # return get_captions(videos[current_video])


def get_youtube_video(video_id):
    return f"""
    <div class="container">
    <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen class="video"></iframe>
    </div>"""


def get_next_youtube_video():
    global current_video, video_links
    current_video += 1
    if current_video == len(video_links):
        current_video = 0
    return get_youtube_video(youtube_link_to_id(video_links[current_video]))
    # global current_video, videos
    # current_video += 1
    # if current_video == len(videos):
    #     current_video = 0
    # return get_youtube_video(videos[current_video])


def refresh_components():
    next_video = get_next_youtube_video()
    next_captions = get_next_captions()
    return next_video, next_captions


def save(df):
    try:
        global captions
        captions['start_time'] = df['Start'].apply(lambda x: float(x))
        captions['text'] = df['Text']
        captions['end_time'] = df['End'].apply(lambda x: float(x))
        captions.to_json('captions2.jsonl', orient='records', lines=True)
        return "Save successful!"
    except ValueError:
        return "Save failed: Incorrect input format"


with gr.Blocks(css=css) as app:
    gr.Markdown("## Caption Editor")
    with gr.Row():
        with gr.Column():
            caption_editor = gr.DataFrame(interactive=True,
                                          value=get_captions(youtube_link_to_id(video_links[current_video])),
                                          datatype=["number", "str", "number"],
                                          row_count=(get_captions(youtube_link_to_id(video_links[current_video])).shape[0], "fixed"),
                                          col_count=(3, "fixed"), column_widths=["20%", "60%", "20%"])
            save_button = gr.Button("Save")
            save_result = gr.Markdown()
        with gr.Column():
            video_embed = gr.HTML(value=get_youtube_video(youtube_link_to_id(video_links[0])))
            next_video_button = gr.Button("Next")

    next_video_button.click(fn=refresh_components, outputs=[video_embed, caption_editor])
    save_button.click(fn=save, inputs=caption_editor, outputs=save_result)

app.launch(auth=auth_function)
