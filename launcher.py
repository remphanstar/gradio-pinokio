import gradio as gr, tempfile, shutil, threading, queue, time
from pinokio_runner import list_apps, install_app, start_app

LOG_LIMIT = 400   # keep last N lines in the log panel

class LogBuffer:
    def __init__(self):
        self.q = queue.Queue()
        self.lines = []

    def __call__(self, line:str):
        self.q.put(line)

    def read(self):
        while True:
            try:
                line = self.q.get_nowait()
                self.lines.append(line)
                self.lines = self.lines[-LOG_LIMIT:]
            except queue.Empty:
                break
        return "\n".join(self.lines)

def task_thread(fn, *args):
    def _wrap():
        try:
            fn(*args)
        except Exception as e:
            args[-1](f"❌ {e}")
    t = threading.Thread(target=_wrap, daemon=True)
    t.start()

apps = list_apps()

with gr.Blocks(title="Gradio-Pinokio") as demo:
    gr.Markdown("# Gradio-Pinokio\nRun any Pinokio script from the cloud.")

    with gr.Row():
        app_dropdown = gr.Dropdown(choices=list(apps.keys()), label="Select App")
        install_btn  = gr.Button("Install")
        start_btn    = gr.Button("Start")
    log_box = gr.Code(label="Live Log", language="bash", interactive=False, lines=25)

    buffers = {}

    def do_install(app_name):
        buf = buffers.setdefault(app_name, LogBuffer())
        task_thread(install_app, apps[app_name], buf)
        return gr.update(interactive=False), buf.read

    def do_start(app_name):
        buf = buffers.setdefault(app_name, LogBuffer())
        task_thread(start_app, apps[app_name], buf)
        return gr.update(interactive=False), buf.read

    install_btn.click(do_install, app_dropdown, [install_btn, log_box])
    start_btn.click(do_start, app_dropdown, [start_btn, log_box])

    def refresh_logs():
        if app_dropdown.value and app_dropdown.value in buffers:
            return buffers[app_dropdown.value].read()
        return ""

    demo.load(refresh_logs, None, log_box, every=1)

if __name__ == "__main__":
    demo.queue().launch(share=True)
