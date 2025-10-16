import gradio as gr
import pandas as pd
from .Functions.video_player_functions import youtube_link_to_id, get_video_embed_by_id, get_video_link_by_pointer
from .Functions.caption_editor_functions import get_captions_by_video_id, save_dataframe
from .Resources.css import css

next_video_pointer = 0
user = ""


def get_username(request: gr.Request):
    global user
    user = request.username


def save(df, video_id):
    return save_dataframe(df, video_id, user)


def get_next_components():
    global next_video_pointer
    next_video_link = get_video_link_by_pointer(next_video_pointer)
    next_video_pointer += 1
    if next_video_link is None:
        next_video_link = get_video_link_by_pointer(0)
        next_video_pointer = 1

    try:
        next_video_id = youtube_link_to_id(next_video_link)

        next_video = get_video_embed_by_id(next_video_id)
        next_captions = get_captions_by_video_id(next_video_id)
        return next_video, next_captions, next_video_id
    except (ValueError, Exception) as e:
        error_html = f"<div>Error loading video: {str(e)}</div>"
        empty_captions = pd.DataFrame(columns=["Start", "Text", "End"])
        return error_html, empty_captions, "error"
    


(start_video, start_captions, start_video_id) = get_next_components()

with gr.Blocks(css=css) as main_page:
    gr.Markdown("## Caption Editor")
    current_video_id = gr.Textbox(value=start_video_id, visible=False, interactive=False)
    with gr.Row():
        with gr.Column():
            caption_editor = gr.DataFrame(interactive=True,
                                          value=start_captions,
                                          datatype=["number", "str", "number"],
                                          row_count=(start_captions.shape[0], "fixed"),
                                          col_count=(3, "fixed"), column_widths=["20%", "60%", "20%"])
            save_button = gr.Button(value="Save")
            save_result = gr.Markdown()
        with gr.Column():
            video_embed = gr.HTML(value=start_video)
            next_video_button = gr.Button("Next")

    next_video_button.click(fn=get_next_components,
                            outputs=[video_embed, caption_editor, current_video_id])
    save_button.click(fn=save,
                      inputs=[caption_editor, current_video_id],
                      outputs=save_result)
    main_page.load(get_username)
