import gradio as gr
import pandas as pd
from Functions.video_player_functions import (youtube_link_to_id, get_video_link_by_pointer, get_youtube_player_html,
                                              change_video_completion_status, get_number_of_videos)
from Functions.caption_editor_functions import request_captions_by_video_id, save_captions_to_db
from Resources.css import css
from Resources.js import yt_init_js
from Resources.localization import get_string

next_video_pointer = 0
user = "anonymous_user"
n_videos = get_number_of_videos()
placeholder_link = "https://www.youtube.com/watch?v=d37lwXaSjs4"


def get_username(profile: gr.OAuthProfile):
    global user
    if profile is None:
        user = "anonymous_user"
    else:
        user = profile.username
    return profile


def on_row_select(df, evt: gr.SelectData):
    """Handle row selection in DataFrame"""
    if evt.index is not None and len(evt.index) > 0:
        row_idx = evt.index[0]
        if row_idx < len(df):
            row = df.iloc[row_idx]
            return (
                gr.update(value=float(row['Start'])),  # start_time
                gr.update(value=str(row['Text'])),  # text_input
                gr.update(value=float(row['End'])),  # end_time
                gr.update(value=row_idx),  # selected_row_idx
                gr.update(value=get_string("update_entry_button"))  # save_entry_button
            )
    return gr.update(value=0.0), gr.update(value=""), gr.update(value=0.0), -1, get_string("save_entry_button")


# ADC-IMPLEMENTS: <gc-feature-aligned-ui-01>
def save_entry(df, start_time, text, end_time, selected_row_idx, video_id):
    """Save or update a caption entry with per-entry alignment tracking.

    Works directly with the 4-column DataFrame (Start, Text, End, Aligned).
    Sets aligned=True ONLY for the specific row being added or updated.
    All other rows retain their existing Aligned values from the DataFrame.
    The current video pointer is computed from global state and passed to
    save_captions_to_db for auto-assignment.
    """
    if user == "anonymous_user":
        return df, gr.Warning(get_string("please_sign_in"))
    if next_video_pointer == -1:
        return df, gr.Warning(get_string("all_videos_transcribed"))
    try:
        start_time = float(start_time)
        end_time = float(end_time)

        if start_time >= end_time:
            return df, gr.Warning(get_string("start_less_than_end"))

        if not text.strip():
            return df, gr.Warning(get_string("text_cannot_be_empty"))

        df_copy = df.copy()

        if selected_row_idx == -1:  # Adding new entry
            new_row = pd.DataFrame({
                'Start': [start_time],
                'Text': [text.strip()],
                'End': [end_time],
                'Aligned': [True]  # New entry gets aligned=True
            })
            df_copy = pd.concat([df_copy, new_row], ignore_index=True)
            df_copy = df_copy.sort_values('Start').reset_index(drop=True)
        else:  # Updating existing entry
            if 0 <= selected_row_idx < len(df_copy):
                df_copy.at[selected_row_idx, 'Start'] = start_time
                df_copy.at[selected_row_idx, 'Text'] = text.strip()
                df_copy.at[selected_row_idx, 'End'] = end_time
                df_copy.at[selected_row_idx, 'Aligned'] = True  # Only this row gets aligned=True
                df_copy = df_copy.sort_values('Start').reset_index(drop=True)

        # Compute the current video's pointer index from global state.
        # This is the same formula used by change_completion_status.
        current_pointer = (next_video_pointer + n_videos - 1) % n_videos
        # save_captions_to_db receives the 4-col DF directly
        save_result = save_captions_to_db(df_copy, video_id, user, current_pointer)

        return (
            df_copy,
            gr.Info(f"{save_result}")
        )

    except ValueError as e:
        return df, gr.Warning(f"{get_string('invalid_time_format')} {str(e)}")
    except Exception as e:
        return df, gr.Error(f"{get_string('error')} {str(e)}")


def clear_form():
    """Clear the editing form"""
    return (
        gr.update(value=0.0),  # start_time
        gr.update(value=""),  # text_input
        gr.update(value=0.0),  # end_time
        gr.update(value=-1),  # selected_row_idx
        gr.update(value=get_string("save_entry_button"))  # save_entry_button
    )


def validate_preview(start_time, end_time):
    """Validate times for preview playback"""
    try:
        start = float(start_time)
        end = float(end_time)
        if start == end:
            return None, gr.Warning(get_string("preview_times_equal"))
        if start >= end:
            return None, gr.Warning(get_string("preview_invalid_times"))
        return (start, end), None
    except ValueError:
        return None, gr.Warning(get_string("invalid_time_format"))


def update_speed_buttons(selected_speed):
    """Return updates for all speed buttons, highlighting the selected one"""
    speeds = [0.25, 0.5, 0.75, 1, 2]
    return [
        gr.update(variant="primary" if speed == selected_speed else "secondary")
        for speed in speeds
    ]


def change_completion_status(completion_status):
    if user == "anonymous_user":
        return gr.Warning(get_string("please_sign_in"))

    global next_video_pointer
    try:
        change_video_completion_status(completion_status, (next_video_pointer + n_videos - 1) % n_videos)
        return gr.Info(get_string("change_video_completion_status_success"))
    except Exception as e:
        return gr.Error(f"{get_string('error')} {str(e)}")


# ADC-IMPLEMENTS: <gc-feature-assignment-01>
def get_next_components(show_incomplete_only):
    """Get the next video and its captions as a 4-column DataFrame.

    Returns:
        captions: 4-column DataFrame [Start, Text, End, Aligned] for the UI
        next_video_id: YouTube video ID string

    Args:
        show_incomplete_only: If True, skip videos marked as complete
    """
    global next_video_pointer
    next_video_link = placeholder_link
    if next_video_pointer != -1:
        next_video_link = get_video_link_by_pointer(next_video_pointer, show_incomplete_only)
        next_video_pointer = (next_video_pointer + 1) % n_videos

        for _ in range(n_videos + 1):
            if next_video_link is not None:
                break
            next_video_link = get_video_link_by_pointer(next_video_pointer, show_incomplete_only)
            next_video_pointer = (next_video_pointer + 1) % n_videos
        if next_video_link is None:
            next_video_link = placeholder_link
            next_video_pointer = -1

    try:
        next_video_id = youtube_link_to_id(next_video_link)
        captions = request_captions_by_video_id(next_video_id)
        return captions, next_video_id
    except (ValueError, Exception):
        empty_captions = pd.DataFrame(columns=["Start", "Text", "End", "Aligned"])
        return empty_captions, "error"


(start_captions, start_video_id) = get_next_components(True)

with gr.Blocks(css=css, head=yt_init_js, fill_width=True) as main_page:
    user_state = gr.State("anonymous_user")
    pointer_state = gr.State(0)

    current_video_id = gr.Textbox(value="", visible=False, interactive=False)
    selected_row_idx = gr.Number(value=-1, visible=False)

    main_page.load(get_username, outputs=user_state)

    with gr.Row(variant="panel"):
        with gr.Column(scale=4):
            gr.Markdown(f"## {get_string('app_title')}")
        with gr.Column(scale=4):
            @gr.render(inputs=user_state)
            def check_login(logged_in_user):
                if logged_in_user == "anonymous_user":
                    gr.Markdown(get_string("please_log_in"), rtl=True)
                else:
                    gr.Markdown(f"{get_string('logged_in_as')} {logged_in_user.username}", rtl=True)
        with gr.Column(scale=1, min_width=50):
            gr.LoginButton(value=get_string("log_in_button"), logout_value=get_string("log_in_button"))

    # Top row: Video player (left) + Controls & Editing panel (right)
    with gr.Row():
        with gr.Column(scale=2, min_width=600):
            video_embed = gr.HTML(value=get_youtube_player_html())

        with gr.Column(scale=1, min_width=500):
            with gr.Group():
                gr.Markdown(f"### {get_string('playback_controls_title')}")
                with gr.Row():
                    seek_back_1s_btn = gr.Button(get_string("seek_back_1s"), size="sm", min_width=60)
                    seek_back_100ms_btn = gr.Button(get_string("seek_back_100ms"), size="sm", min_width=80)
                    play_pause_btn = gr.Button(get_string("play_button"), size="sm", min_width=80, variant="primary")
                    seek_forward_100ms_btn = gr.Button(get_string("seek_forward_100ms"), size="sm", min_width=80)
                    seek_forward_1s_btn = gr.Button(get_string("seek_forward_1s"), size="sm", min_width=60)
                gr.Markdown(f"**{get_string('speed_label')}**")
                with gr.Row():
                    speed_025_btn = gr.Button("0.25x", size="sm", min_width=60)
                    speed_05_btn = gr.Button("0.5x", size="sm", min_width=60)
                    speed_075_btn = gr.Button("0.75x", size="sm", min_width=60)
                    speed_1_btn = gr.Button("1x", size="sm", min_width=60, variant="primary")
                    speed_2_btn = gr.Button("2x", size="sm", min_width=60)

            with gr.Group():
                gr.Markdown(f"### {get_string('edit_caption_title')}")
                gr.Markdown(f"**{get_string('start_time_label')}**")
                with gr.Row():
                    start_time_input = gr.Textbox(show_label=False, value="0.000", interactive=False, scale=0, min_width=100)
                    insert_start_time_button = gr.Button(get_string("insert_time_button"), scale=1)
                    goto_start_time_button = gr.Button(get_string("goto_time_button"), scale=1)
                gr.Markdown(f"**{get_string('caption_text_label')}**")
                text_input = gr.Textbox(show_label=False, placeholder=get_string("caption_text_placeholder"))
                gr.Markdown(f"**{get_string('end_time_label')}**")
                with gr.Row():
                    end_time_input = gr.Textbox(show_label=False, value="0.000", interactive=False, scale=0, min_width=100)
                    insert_end_time_button = gr.Button(get_string("insert_time_button"), scale=1)
                    goto_end_time_button = gr.Button(get_string("goto_time_button"), scale=1)
                with gr.Row():
                    save_entry_button = gr.Button(get_string("save_entry_button"), variant="primary")
                    preview_button = gr.Button(get_string("preview_button"), variant="secondary")
                    clear_button = gr.Button(get_string("cancel_button"), variant="secondary")

    # Bottom row: Caption table (left) + Navigation & checkboxes (right)
    with gr.Row():
        with gr.Column(scale=2):
            caption_editor = gr.DataFrame(
                interactive=False,
                elem_id="tbl",
                datatype=["number", "str", "number", "bool"],
                col_count=(4, "fixed"),
                column_widths=["12%", "60%", "12%", "16%"],
                headers=[get_string("header_start"), get_string("header_text"), get_string("header_end"), get_string("header_aligned")],
                wrap=True
            )

        with gr.Column(scale=1, min_width=200):
            next_video_button = gr.Button(get_string("next_button"), key="next_video", variant="primary")
            show_incomplete_only_checkbox = gr.Checkbox(label=get_string("show_incomplete_only_checkbox"), value=True)
            editing_complete_checkbox = gr.Checkbox(label=get_string("editing_complete_checkbox"))

    info_window = gr.Markdown()

    main_page.load(
        fn=get_next_components,
        outputs=[caption_editor, current_video_id],
        js="""() => {
            const checkPlayer = setInterval(() => {
                if (window.ytPlayer && window.ytPlayer.cueVideoById) {
                    clearInterval(checkPlayer);
                    // cue video dynamically once captions arrive
                }
            }, 100);
        }"""
    )

    next_video_button.click(
        fn=get_next_components,
        inputs=[show_incomplete_only_checkbox],
        outputs=[caption_editor, current_video_id]
    )
    next_video_button.click(
        fn=lambda: False,
        outputs=editing_complete_checkbox
    )
    next_video_button.click(
        fn=clear_form,
        outputs=[start_time_input, text_input, end_time_input, selected_row_idx, save_entry_button]
    )

    show_incomplete_only_checkbox.input(
        fn=lambda: gr.Info(get_string("show_incomplete_only_change")),
        outputs=info_window
    )

    current_video_id.change(
        fn=None,
        inputs=current_video_id,
        outputs=None,
        js="""(videoId) => {
            if (window.ytPlayer && window.ytPlayer.cueVideoById) {
                console.log('[Video Load] cueVideoById', videoId);
                window.ytPlayer.cueVideoById(videoId);
            }
        }"""
    )

    caption_editor.select(
        fn=on_row_select,
        inputs=[caption_editor],
        outputs=[start_time_input, text_input, end_time_input, selected_row_idx, save_entry_button]
    )

    editing_complete_checkbox.input(
        fn=change_completion_status,
        inputs=editing_complete_checkbox,
        outputs=info_window
    )

    save_entry_button.click(
        fn=save_entry,
        inputs=[caption_editor, start_time_input, text_input, end_time_input,
                selected_row_idx, current_video_id],
        outputs=[caption_editor, info_window]
    )

    insert_start_time_button.click(
        fn=None, inputs=None, outputs=start_time_input,
        js="() => window.ytPlayer ? +window.ytPlayer.getCurrentTime().toFixed(3) : 0"
    )
    insert_end_time_button.click(
        fn=None, inputs=None, outputs=end_time_input,
        js="() => window.ytPlayer ? +window.ytPlayer.getCurrentTime().toFixed(3) : 0"
    )

    goto_start_time_button.click(
        fn=None, inputs=[start_time_input], outputs=None,
        js="(time) => { if (window.ytPlayer) { window.ytPlayer.seekTo(parseFloat(time), true); window.ytPlayer.pauseVideo(); } }"
    )
    goto_end_time_button.click(
        fn=None, inputs=[end_time_input], outputs=None,
        js="(time) => { if (window.ytPlayer) { window.ytPlayer.seekTo(parseFloat(time), true); window.ytPlayer.pauseVideo(); } }"
    )

    clear_button.click(
        fn=clear_form,
        outputs=[start_time_input, text_input, end_time_input, selected_row_idx, save_entry_button]
    )

    preview_button.click(
        fn=validate_preview,
        inputs=[start_time_input, end_time_input],
        outputs=[gr.State(), info_window]
    ).success(
        fn=None,
        inputs=[start_time_input, end_time_input],
        js="""(startTime, endTime) => {
            if (window.ytPlayer) {
                const start = parseFloat(startTime);
                const end = parseFloat(endTime);
                window.ytPlayer.seekTo(start, true);
                window.ytPlayer.playVideo();
                if (window.previewInterval) clearInterval(window.previewInterval);
                window.previewInterval = setInterval(() => {
                    if (window.ytPlayer.getCurrentTime() >= end) {
                        window.ytPlayer.pauseVideo();
                        clearInterval(window.previewInterval);
                    }
                }, 20);
            }
        }"""
    )

    # Playback control handlers
    seek_back_1s_btn.click(
        fn=None, inputs=None, outputs=None,
        js="() => { if (window.ytPlayer) { window.ytPlayer.seekTo(Math.max(0, window.ytPlayer.getCurrentTime() - 1), true); } }"
    )
    seek_back_100ms_btn.click(
        fn=None, inputs=None, outputs=None,
        js="() => { if (window.ytPlayer) { window.ytPlayer.seekTo(Math.max(0, window.ytPlayer.getCurrentTime() - 0.1), true); } }"
    )
    seek_forward_100ms_btn.click(
        fn=None, inputs=None, outputs=None,
        js="() => { if (window.ytPlayer) { window.ytPlayer.seekTo(window.ytPlayer.getCurrentTime() + 0.1, true); } }"
    )
    seek_forward_1s_btn.click(
        fn=None, inputs=None, outputs=None,
        js="() => { if (window.ytPlayer) { window.ytPlayer.seekTo(window.ytPlayer.getCurrentTime() + 1, true); } }"
    )
    play_pause_btn.click(
        fn=None, inputs=None, outputs=play_pause_btn,
        js=f"""() => {{
            if (window.ytPlayer) {{
                const state = window.ytPlayer.getPlayerState();
                if (state === 1) {{
                    window.ytPlayer.pauseVideo();
                    return "{get_string('play_button')}";
                }} else {{
                    window.ytPlayer.playVideo();
                    return "{get_string('pause_button')}";
                }}
            }}
            return "{get_string('play_button')}";
        }}"""
    )

    # Speed control handlers
    speed_outputs = [speed_025_btn, speed_05_btn, speed_075_btn, speed_1_btn, speed_2_btn]
    speed_025_btn.click(
        fn=lambda: update_speed_buttons(0.25), outputs=speed_outputs,
        js="() => { if (window.ytPlayer) { window.ytPlayer.setPlaybackRate(0.25); } }"
    )
    speed_05_btn.click(
        fn=lambda: update_speed_buttons(0.5), outputs=speed_outputs,
        js="() => { if (window.ytPlayer) { window.ytPlayer.setPlaybackRate(0.5); } }"
    )
    speed_075_btn.click(
        fn=lambda: update_speed_buttons(0.75), outputs=speed_outputs,
        js="() => { if (window.ytPlayer) { window.ytPlayer.setPlaybackRate(0.75); } }"
    )
    speed_1_btn.click(
        fn=lambda: update_speed_buttons(1), outputs=speed_outputs,
        js="() => { if (window.ytPlayer) { window.ytPlayer.setPlaybackRate(1); } }"
    )
    speed_2_btn.click(
        fn=lambda: update_speed_buttons(2), outputs=speed_outputs,
        js="() => { if (window.ytPlayer) { window.ytPlayer.setPlaybackRate(2); } }"
    )

main_page.launch(share=True)
