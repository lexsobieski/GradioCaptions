import pandas as pd
import json


def get_captions_by_video_id(video_id):
    with open("Resources/captions.jsonl") as file:
        captions = pd.read_json(file, lines=True)

    captions_edit = captions[captions['file'] == video_id]
    captions_edit = captions_edit[['start_time', 'text', 'end_time']]
    captions_edit.columns = ["Start", "Text", "End"]
    return captions_edit


def save_dataframe(df, video_id, user):
    cols = ["clean_text", "start_time", "user_id", "signer", "file", "end_time", "url", "text"]
    other_captions_data = []
    new_captions_data = []
    file_name = "Resources/captions.jsonl"

    with open(file_name) as f:
        for line in f:
            caption = json.loads(line)
            if caption['file'] == video_id:
                new_captions_data.append(caption)
            else:
                other_captions_data.append(caption)

    other_captions = pd.DataFrame(data=other_captions_data, columns=cols)
    new_captions = pd.DataFrame(data=new_captions_data, columns=cols)
    try:
        new_captions['start_time'] = df['Start'].apply(lambda x: float(x))
        new_captions['text'] = df['Text']
        new_captions['end_time'] = df['End'].apply(lambda x: float(x))
        new_captions['user_id'] = user

        all_captions = pd.concat([other_captions, new_captions], ignore_index=True)

        all_captions.to_json('Resources/captions.jsonl', orient='records', lines=True)
        return "Save successful!"
    except ValueError:
        return "Save failed: Incorrect input format"
