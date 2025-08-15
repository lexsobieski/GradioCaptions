import pandas as pd
import numpy as np


def get_captions_by_video_id(video_id):
    with open("Resources/captions.jsonl") as file:
        captions = pd.read_json(file, lines=True)

    captions_edit = captions[captions['file'] == video_id]
    captions_edit = captions_edit[['start_time', 'text', 'end_time']]
    captions_edit.columns = ["Start", "Text", "End"]
    return captions_edit


def save_dataframe(df, video_id, user):
    try:
        with open("Resources/captions.jsonl") as file:
            captions = pd.read_json(file, lines=True)

        other_captions = captions[captions['file'] != video_id].copy()
        new_captions = captions[captions['file'] == video_id].copy()

        new_captions['start_time'] = np.where(df['Start'].isnull(),
                                              new_captions['start_time'],
                                              df['Start'].apply(lambda x: float(x)))
        new_captions['text'] = np.where(df['Text'].isnull(),
                                        new_captions['text'],
                                        df['Text'])
        new_captions['end_time'] = np.where(df['End'].isnull(),
                                            new_captions['end_time'],
                                            df['End'].apply(lambda x: float(x)))
        new_captions['user_id'] = user

        all_captions = pd.concat([other_captions, new_captions], ignore_index=True)

        all_captions.to_json('Resources/captions.jsonl', orient='records', lines=True)
        return "Save successful!"
    except ValueError:
        return "Save failed: Incorrect input format"
