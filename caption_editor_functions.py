import pandas as pd

with open("Resources/captions.jsonl") as file:
    captions = pd.read_json(file, lines=True)


def get_captions_by_video_id(video_id):
    global captions
    captions_edit = captions[captions['file'] == video_id]
    captions_edit = captions_edit[['start_time', 'text', 'end_time']]
    captions_edit.columns = ["Start", "Text", "End"]
    return captions_edit


def save(df):
    try:
        global captions
        captions['start_time'] = df['Start'].apply(lambda x: float(x))
        captions['text'] = df['Text']
        captions['end_time'] = df['End'].apply(lambda x: float(x))
        captions.to_json('Resources/captions2.jsonl', orient='records', lines=True)
        return "Save successful!"
    except ValueError:
        return "Save failed: Incorrect input format"
