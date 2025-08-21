import gradio as gr
from .Functions.auth_functions import register

with gr.Blocks() as registration:
    with gr.Column(variant="panel"):
        gr.Markdown(value="# Create Account")
        username = gr.Textbox(label="Username", show_label=True, lines=1)
        password = gr.Textbox(label="Password", show_label=True, lines=1, type="password")
        registration_button = gr.Button(value="Register")
        registration_result = gr.Markdown()

        registration_button.click(fn=register, inputs=[username, password], outputs=registration_result)
