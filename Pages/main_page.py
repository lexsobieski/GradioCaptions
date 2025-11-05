import gradio as gr
import pandas as pd
from .Functions.video_player_functions import youtube_link_to_id, get_video_embed_by_id, get_video_link_by_pointer, get_youtube_player_html
from .Functions.caption_editor_functions import get_captions_by_video_id, save_dataframe
from .Resources.css import css
from .Resources.js import yt_init_js

next_video_pointer = 0
user = ""


def get_username(request: gr.Request):
    global user
    user = request.username


def save(df, video_id):
    return save_dataframe(df, video_id, user)


def on_row_select(df, evt: gr.SelectData):
    """Handle row selection in DataFrame"""
    if evt.index is not None and len(evt.index) > 0:
        row_idx = evt.index[0]
        if row_idx < len(df):
            row = df.iloc[row_idx]
            return (
                gr.update(visible=True),  # editing_panel
                gr.update(value=float(row['Start'])),  # start_time
                gr.update(value=str(row['Text'])),     # text_input
                gr.update(value=float(row['End'])),    # end_time
                gr.update(value=row_idx),              # selected_row_idx
                gr.update(value="Update Entry")        # save_entry_button
            )
    return gr.update(visible=False), "", "", "", -1, "Save Entry"


def show_add_entry_form():
    """Show editing panel for adding new entry"""
    return (
        gr.update(visible=True),     # editing_panel
        gr.update(value=0.0),        # start_time
        gr.update(value=""),         # text_input
        gr.update(value=0.0),        # end_time
        gr.update(value=-1),         # selected_row_idx (-1 means new entry)
        gr.update(value="Add Entry") # save_entry_button
    )


def save_entry(df, start_time, text, end_time, selected_row_idx, video_id):
    """Save or update a caption entry"""
    try:
        start_time = float(start_time)
        end_time = float(end_time)
        
        if start_time >= end_time:
            return df, gr.update(visible=True), gr.Warning("Start time must be less than end time")
        
        if not text.strip():
            return df, gr.update(visible=True), gr.Warning("Text cannot be empty")
        
        df_copy = df.copy()
        
        if selected_row_idx == -1:  # Adding new entry
            new_row = pd.DataFrame({
                'Start': [start_time],
                'Text': [text.strip()],
                'End': [end_time]
            })
            df_copy = pd.concat([df_copy, new_row], ignore_index=True)
            # Sort by start time
            df_copy = df_copy.sort_values('Start').reset_index(drop=True)
        else:  # Updating existing entry
            if 0 <= selected_row_idx < len(df_copy):
                df_copy.iloc[selected_row_idx] = [start_time, text.strip(), end_time]
                # Sort by start time
                df_copy = df_copy.sort_values('Start').reset_index(drop=True)
        
        # Save to file
        save_result = save_dataframe(df_copy, video_id, user)
        
        return (
            df_copy,
            gr.update(visible=False),  # Hide panel on success
            gr.Info(f"{save_result}")
        )
        
    except ValueError as e:
        return df, gr.update(visible=True), gr.Warning(f"Invalid time format: {str(e)}")
    except Exception as e:
        return df, gr.update(visible=True), gr.Error(f"Error: {str(e)}")


def cancel_edit():
    """Cancel editing and hide the form"""
    return gr.update(visible=False)


def get_next_components():
    global next_video_pointer
    next_video_link = get_video_link_by_pointer(next_video_pointer)
    next_video_pointer += 1
    if next_video_link is None:
        next_video_link = get_video_link_by_pointer(0)
        next_video_pointer = 1

    try:
        next_video_id = youtube_link_to_id(next_video_link)
        next_captions = get_captions_by_video_id(next_video_id)
        return next_captions, next_video_id
    except (ValueError, Exception) as e:
        empty_captions = pd.DataFrame(columns=["Start", "Text", "End"])
        return empty_captions, "error"
    


(start_captions, start_video_id) = get_next_components()

with gr.Blocks(css=css, head=yt_init_js) as main_page:
    gr.Markdown("## Caption Editor")
    current_video_id = gr.Textbox(value=start_video_id, visible=False, interactive=False)
    selected_row_idx = gr.Number(value=-1, visible=False)
    
    with gr.Row():
        with gr.Column(scale=2, min_width=600):
            # Video player and "next video button
            video_embed = gr.HTML(value=get_youtube_player_html())
            next_video_button = gr.Button("Next")
        with gr.Column(scale=1, min_width=200):
            # Read-only DataFrame with add button
            caption_editor = gr.DataFrame(interactive=False,
                                          elem_id="tbl",
                                          value=start_captions,
                                          datatype=["number", "str", "number"],
                                          col_count=(3, "fixed"), 
                                          column_widths=["20%", "60%", "20%"],
                                          headers=["Start", "Text", "End"],
                                          wrap=True)
            add_entry_button = gr.Button("Add Entry", variant="secondary")
    
    with gr.Row():
    # Editing panel (initially hidden) - spans full width
        with gr.Group(visible=False) as editing_panel:
            gr.Markdown("### Edit Caption Entry")
            with gr.Row(equal_height=False):
                with gr.Column():
                    start_time_input = gr.Textbox(label="Start Time (seconds)", value="0.000", interactive=False)
                    insert_start_time_button = gr.Button("Insert Current Time")
                with gr.Column():
                    text_input = gr.Textbox(label="Caption Text", placeholder="Enter caption text...")

                with gr.Column():
                    end_time_input = gr.Textbox(label="End Time (seconds)", value="0.000", interactive=False)
                    insert_end_time_button = gr.Button("Insert Current Time")

            with gr.Row(equal_height=False):
                save_entry_button = gr.Button("Save Entry", variant="primary")
                cancel_button = gr.Button("Cancel", variant="secondary")
    
    save_result = gr.Markdown()

    # Event handlers
    next_video_button.click(
        fn=get_next_components,
        outputs=[caption_editor, current_video_id]
    )
    
    # Load video when current_video_id changes
    current_video_id.change(
        fn=None,
        inputs=current_video_id,
        outputs=None,
        js="""(videoId) => {
            if (window.ytPlayer && window.ytPlayer.cueVideoById) {
                console.log('[Video Load] Calling cueVideoById with:', videoId);
                window.ytPlayer.cueVideoById(videoId);
            } else {
                console.error('[Video Load] Player not ready yet');
            }
        }"""
    )
    
    # Handle row selection in DataFrame
    caption_editor.select(
        fn=on_row_select,
        inputs=[caption_editor],
        outputs=[editing_panel, start_time_input, text_input, end_time_input, selected_row_idx, save_entry_button]
    )
    
    # Handle add entry button
    add_entry_button.click(
        fn=show_add_entry_form,
        outputs=[editing_panel, start_time_input, text_input, end_time_input, selected_row_idx, save_entry_button]
    )
    
    # Handle save entry
    save_entry_button.click(
        fn=save_entry,
        inputs=[caption_editor, start_time_input, text_input, end_time_input, selected_row_idx, current_video_id],
        outputs=[caption_editor, editing_panel, save_result]
    )

    insert_start_time_button.click(fn=None, inputs=None, outputs=start_time_input,
      js="() => window.ytPlayer ? +window.ytPlayer.getCurrentTime().toFixed(3) : 0")

    insert_end_time_button.click(fn=None, inputs=None, outputs=end_time_input,
      js="() => window.ytPlayer ? +window.ytPlayer.getCurrentTime().toFixed(3) : 0")

    
    # Handle cancel
    cancel_button.click(
        fn=cancel_edit,
        outputs=[editing_panel]
    )
    
    # Load initial video on page load
    main_page.load(
        fn=None,
        inputs=current_video_id,
        outputs=None,
        js="""(videoId) => {
            const checkPlayer = setInterval(() => {
                if (window.ytPlayer && window.ytPlayer.cueVideoById) {
                    clearInterval(checkPlayer);
                    window.ytPlayer.cueVideoById(videoId);
                }
            }, 100);
        }"""
    )
    
    main_page.load(get_username)  # Disabled when auth is disabled
