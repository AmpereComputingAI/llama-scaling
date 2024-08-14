import copy
from functools import partial
import psutil
import gradio as gr
import requests
import grequests
import httpx
import pandas as pd

MAX_WINDOWS = 4
MAX_REQUESTS = 3
NUM_THREADS = 16
MAX_CPUS = MAX_WINDOWS * NUM_THREADS

url = 'http://localhost:8080/completion'
ex_text = [
    ["The Moon's orbit around Earth has"],
    ["Explore the Wonders of Space Exploration"],
    ["Mysterious island, hidden treasure inside"],
    ["Wildflowers blooming in the meadow"],
]

def completion(txt, count):
    data = {'prompt': txt, 'n_predict': 32}
    for i in range(count):
        print(f'[{i}]: request post')
        r = requests.post(url, json=data)
        #print(r.status_code)
        yield r.json()['content']

# Create multiple functions
d = { f'completion{i}': partial(completion) for i in range(MAX_WINDOWS) }

def cpu_percent():
    #cpu_util = []
    cpu_num = list(map(str, range(MAX_CPUS)))
    #print(cpu_num)
    cpu_util = psutil.cpu_percent(interval=1, percpu=True)
    df = pd.DataFrame({'CPU': cpu_num, 'Percent': cpu_util[:MAX_CPUS]})
    df = df.sort_values(by='CPU')
    #print(df)
    return gr.BarPlot(df, x='CPU', y='Percent', title='CPU Usage', container=False)


txt_inp = []
txt_out = []
examples = []
strt_btn = []
loop_btn = []
stop_btn = []
numbers = []
strt_btn_evt = []
stop_btn_evt = []

clear = lambda: ""

with gr.Blocks() as demo:
    with gr.Row(variant='panel'):
        #gr.set_static_paths(paths=["static/"])
        with gr.Column(variant='panel', scale=4):
            t1 = 'Llama Chat Linear Scaling'
            subtitle = 'on Ampere CPUs'
            gr.Markdown(f'<center><h1 style="font-size:3em">{t1}<br />{subtitle}</h1></center>')
        with gr.Column(variant='panel', scale=1):
            gr.Markdown('<img src="file/static/ampere_logo_primary_stacked_rgb.png" alt="images" border="0" style="float:right">')
            #gr.Markdown('<img src="/file=/static/ampere_logo_primary_stacked_rgb.png">')
            #gr.HTML('<img src="file/static/ampere_logo_primary_stacked_rgb.png" alt="images" border="0" style="float:right">')
            #gr.Image("/file=static/ampere_logo_primary_stacked_rgb.png")
    plot = gr.BarPlot()
    with gr.Row():
        btn1 = gr.Button('Start', variant='secondary', size='sm')
        btn2 = gr.Button('Stop', variant='secondary', size='sm')
        btn1_evt = btn1.click(cpu_percent, None, plot, every=1)
        btn2.click(clear, None, None, cancels=btn1_evt)
    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS):
            with gr.Column(min_width=128):
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(ex_text, txt_inp[i]))
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, scale=1))
                    strt_btn.append(gr.Button('Start', variant='primary', size='sm', scale=3))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button('Stop', variant='stop', size='sm', scale=1))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i]], txt_out[i]))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))

if __name__ == '__main__':
    demo.queue(default_concurrency_limit=4)
    demo.launch(allowed_paths=["static/ampere_logo_primary_stacked_rgb.png"], debug=True)
