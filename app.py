import gradio as gr
import firebase_admin
from firebase_admin import db
from auth_functions import auth_function
from video_player_functions import youtube_link_to_id, get_video_embed_by_id, get_video_link_by_pointer
from caption_editor_functions import get_captions_by_video_id, save, captions
from Resources.css import css

cred_obj = firebase_admin.credentials.Certificate('Resources/key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://video-link-db-default-rtdb.europe-west1.firebasedatabase.app/"
    })
videos_ref = db.reference("/Videos")
users_ref = db.reference("/Users")

next_video_pointer = 0


def auth(username, password):
    return auth_function(username, password, db_ref=users_ref)


def get_next_components():
    global next_video_pointer
    next_video_link = get_video_link_by_pointer(next_video_pointer, db_ref=videos_ref)
    next_video_pointer += 1
    if next_video_link is None:
        next_video_link = get_video_link_by_pointer(0, db_ref=videos_ref)
        next_video_pointer = 1

    next_video_id = youtube_link_to_id(next_video_link)

    next_video = get_video_embed_by_id(next_video_id)
    next_captions = get_captions_by_video_id(next_video_id)
    return next_video, next_captions


(start_video, start_captions) = get_next_components()

with gr.Blocks(css=css) as app:
    gr.Markdown("## Caption Editor")
    with gr.Row():
        with gr.Column():
            caption_editor = gr.DataFrame(interactive=True,
                                          value=start_captions,
                                          datatype=["number", "str", "number"],
                                          row_count=(start_captions.shape[0], "fixed"),
                                          col_count=(3, "fixed"), column_widths=["20%", "60%", "20%"])
            save_button = gr.Button("Save")
            save_result = gr.Markdown()
        with gr.Column():
            video_embed = gr.HTML(value=start_video)
            next_video_button = gr.Button("Next")

    next_video_button.click(fn=get_next_components, outputs=[video_embed, caption_editor])
    save_button.click(fn=save, inputs=caption_editor, outputs=save_result)

app.launch(auth=auth)
