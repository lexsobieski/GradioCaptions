import gradio as gr
import firebase_admin
from firebase_admin import db
from auth_functions import auth_function
from video_player_functions import youtube_link_to_id, get_youtube_video
from caption_editor_functions import get_captions, save, captions
from Resources.css import css

cred_obj = firebase_admin.credentials.Certificate('Resources/key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://video-link-db-default-rtdb.europe-west1.firebasedatabase.app/"
    })
videos_ref = db.reference("/Videos")
users_ref = db.reference("/Users")

video_links = videos_ref.get()[1:]
current_video = 0


def auth(username, password):
    return auth_function(username, password, users_ref)


def get_next_captions():
    global current_video, video_links
    return get_captions(youtube_link_to_id(video_links[current_video]))
    # global current_video, videos
    # return get_captions(videos[current_video])


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

app.launch(auth=auth)
