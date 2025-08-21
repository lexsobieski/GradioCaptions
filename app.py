from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import gradio as gr
from Pages.main_page import main_page
from Pages.Functions.auth_functions import auth_function
from Pages.registration_page import registration

app = FastAPI()
MAIN_PATH = "/caption_editor"
REGISTRATION_PATH = "/registration"

index_html = f'''
<div>
<iframe src={MAIN_PATH} width=100% height=100% frameBorder="0"></iframe>
</div>
'''


@app.get("/", response_class=HTMLResponse)
def index():
    return index_html


app = gr.mount_gradio_app(app, main_page, path=MAIN_PATH, auth=auth_function)
app = gr.mount_gradio_app(app, registration, path=REGISTRATION_PATH)
