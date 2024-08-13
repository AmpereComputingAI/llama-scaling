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

url = 'http://localhost:8080/completion'
ex_text = [
    ["The Moon's orbit around Earth has"],
    ["The smooth Borealis basin in the Northern Hemisphere covers 40%"],
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
    cpu_num = list(map(str, range(80)))
    #print(cpu_num)
    cpu_util = psutil.cpu_percent(interval=1, percpu=True)
    df = pd.DataFrame({'CPU': cpu_num, 'Percent': cpu_util[:80]})
    df = df.sort_values(by='CPU')
    #print(df)
    return gr.BarPlot(df, x='CPU', y='Percent', title='CPU Usage')


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
    gr.HTML("<h1 style='text-align: center'>Llama Chat Linear Scaling</h1>")
    plot = gr.BarPlot()
    with gr.Row():
        btn1 = gr.Button('Start', variant='secondary', size='sm')
        btn2 = gr.Button('Stop', variant='secondary', size='sm')
        btn1_evt = btn1.click(cpu_percent, None, plot, every=1)
        btn2.click(clear, None, None, cancels=btn1_evt)
    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS):
            with gr.Column(min_width=128):
                txt_inp.append(gr.Textbox(label='Input Text'))
                examples.append(gr.Examples(ex_text, txt_inp[i]))
                txt_out.append(gr.Textbox(label='Output Text', lines=4))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False))
                    strt_btn.append(gr.Button('Start', variant='primary', size='sm'))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button('Stop', variant='stop', size='sm'))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i]], txt_out[i]))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))

if __name__ == '__main__':
    demo.queue(default_concurrency_limit=4)
    demo.launch(debug=True)
