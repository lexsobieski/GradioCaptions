import pandas as pd
from Functions.db_connection import default_app
from Resources.localization import get_string


# ADC-IMPLEMENTS: <gc-transform-caption-df-01>
def save_captions_to_db(df, video_id, user, video_pointer):
    """Save captions to Firebase with per-entry alignment and video assignment.

    Args:
        df: pandas DataFrame with columns ["Start", "Text", "End", "Aligned"]
            (4-column DataFrame with per-entry aligned values already set by caller)
        video_id: YouTube video ID string
        user: HuggingFace username string
        video_pointer: Integer index of the video in the videos collection

    The Aligned column is already set correctly per-entry by save_entry in app.py.
    This function simply renames columns to Firebase field names and writes.
    It also writes the current user to videos/{video_pointer}/assigned_to.
    """
    try:
        data = df.copy()
        # The Aligned column is already set correctly per-entry by the caller.
        # Just rename columns to Firebase field names.
        data.columns = ['start_time', 'text', 'end_time', 'aligned']
        df_json = data.to_dict(orient="index")
        default_app.database().child("video_captions").child(video_id).child("captions").set(df_json)

        # Auto-assign: write the current user to the video's assigned_to field
        # video_pointer is passed directly by the caller -- no resolution needed
        default_app.database().child("videos").child(str(video_pointer)).child("assigned_to").set(user)
        return get_string("save_successful")
    except Exception as e:
        return f"{get_string('save_failed')} {str(e)}"


# ADC-IMPLEMENTS: <gc-transform-firebase-df-01>
def request_captions_by_video_id(video_id):
    """Read captions from Firebase and return a 4-column DataFrame.

    Returns all 4 columns: Start, Text, End, Aligned. The caller
    (get_next_components in app.py) returns this 4-column DataFrame
    directly to the gr.DataFrame for display.
    """
    response = default_app.database().child("video_captions").child(video_id).child("captions").get().val()
    if response is None:
        captions = pd.DataFrame(columns=["end_time", "start_time", "text", "aligned"])
    else:
        captions = pd.DataFrame(response)
        if 'aligned' not in captions.columns:
            captions['aligned'] = False
    captions_edit = captions[['start_time', 'text', 'end_time', 'aligned']]
    captions_edit.columns = ["Start", "Text", "End", "Aligned"]
    return captions_edit
