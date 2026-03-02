---
title: USL-Editor
emoji: 🌖
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
hf_oauth: true
---

# Database structure
2 main endpoints: Videos and video_captions.

### videos
Contains a json object with YouTube links to the videos and 
a boolean for whether the captions for that video are complete.

Example entry: 
```
0: 
    url: "https://www.youtube.com/watch?v=tkMg8g8vVUo"
    complete: true
```

Keys are `integers`. 
They define the order in which the videos show up on the page. 
Videos for which the captions are complete will be skipped.

Values are json objects with `url` and `complete` keys. All keys are mandatory.
`url`s are video link `strings`.
Format is flexible, can optionally include `https://` or a query string.

`complete`s are booleans.

`url` is read-only, `complete` is writable.
Editing/uploading new entries requires changing access rules. 

### video_captions
Contains a json object with video information, namely captions.

Example entry:
```
tkMg8g8vVUo:
    captions:
        0:
            start_time: 0
            text: "text"         # first caption line
            end_time: 1
        1:
            start_time: 1
            text: "text 2"       # second caption line
            end_time: 1.5
    username: "user"            # user who last edited captions
    signer: 1                   # (optional) signer in the video
```

Keys are video id `strings`.

Contains a json object. All keys are optional.
Relevant endpoints are `captions` and `username`, although any number of other objects can be added.

`captions` contains a json object with the captions to the video. 
Keys are `integers`. 
Values are json objects with `start_time`, `text` and `end_time` endpoints.
All keys are mandatory.
`start_time` and `end_time` must have a numeric value type.
`text` is a string.

`username` contains a `string` value.
It is the HuggingFace username of the person who last edited/saved captions for this video.

By default, data is read only.
The `username` endpoint is writable.
The `captions` endpoint is writable, as long as:
- written data has children
- all children have the required `start_time`, `text` and `end_time` children
- `start_time` and `end_time` are numeric

# Database connection

Connecting a Space to the database:
- Go to `Firebase` > `Project settings` > `General` > `Your apps` > `Caption_editor`
- In "SDK setup and configuration" select `Config`
- Copy only the config object value
- Go to space `Settings` > `Variables and secrets` > `Secrets` > `New secret`
- Add a secret with the name `FIREBASE_CONFIG` and value of the config object copied previously.
Note that it must be a valid json object, so the key names must be in double quotes.
- Done!