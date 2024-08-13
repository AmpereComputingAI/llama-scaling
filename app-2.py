import copy
import psutil
import gradio as gr
import requests
import grequests
import httpx
import pandas as pd

MAX_WINDOWS = 2

url = 'http://localhost:8080/completion'
ex_text = [
    ["The Moon's orbit around Earth has"],
    ["The smooth Borealis basin in the Northern Hemisphere covers 40%"],
]

completions = []

def create_completions(txt, count):
    def dynamic_func(*args):
        data = {'prompt': txt, 'n_predict': 32}
        for i in range(int(count)):
            print(f'[{i}]: request post')
            r = requests.post(url, json=data)
            #print(r.status_code)
            yield r.json()['content']

    return dynamic_func

def completion(txt, count):
    data = {'prompt': txt, 'n_predict': 32}
    for i in range(count):
        print(f'[{i}]: request post')
        r = requests.post(url, json=data)
        #print(r.status_code)
        yield r.json()['content']

def completion0(txt, count):
    data = {'prompt': txt, 'n_predict': 32}
    for i in range(count):
        print(f'[{i}]: request post')
        r = requests.post(url, json=data)
        #print(r.status_code)
        yield r.json()['content']

def completion1(txt, count):
    data = {'prompt': txt, 'n_predict': 32}
    for i in range(count):
        print(f'[{i}]: request post')
        r = requests.post(url, json=data)
        #print(r.status_code)
        yield r.json()['content']

#for i in range(MAX_WINDOWS):
#    completions.append(copy.deepcopy(completion))

async def async_completion(txt:str, count:int):
    data = {'prompt': txt, 'n_predict': 32}
    for i in range(count):
        print(f'[{count}]: [{i}]: request post')
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, json=data)
            yield r.json()['content']


def grequests_completion(txt:str, count:int):
    data = {'prompt': txt, 'n_predict': 32}
    r = grequests.post(url, json=data)
    r = grequests.map(r)[0]
    return r

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
    btn = gr.Button()
    btn.click(cpu_percent, None, plot, every=1)
    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS):
            with gr.Column():
                txt_inp.append(gr.Textbox(label='Input Text'))
                examples.append(gr.Examples(ex_text, txt_inp[i]))
                txt_out.append(gr.Textbox(label='Output Text', lines=4))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(5, label='Loop', container=False, scale=0))
                    strt_btn.append(gr.Button('Start', variant='primary', scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button('Stop', variant='stop', scale=1))
                    #strt_btn_evt.append(strt_btn[i].click(completion, [txt_inp[i], numbers[i]], txt_out[i]))
                    #stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))
        strt_btn_evt.append(strt_btn[i].click(completion0, [txt_inp[0], numbers[1]], txt_out[0]))
        strt_btn_evt.append(strt_btn[i].click(completion1, [txt_inp[1], numbers[1]], txt_out[1]))
        for i in range(MAX_WINDOWS):
            #strt_btn_evt.append(strt_btn[i].click(completion, [txt_inp[i], numbers[i]], txt_out[i]))
            stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))

#    strt_btn1_evt = strt_btn1.click(completion, inp1, out1)
#    stop_btn1_evt = stop_btn1.click(clear, None, out1, cancels=strt_btn1_evt)
    #strt_btn1_evt = strt_btn1.click(completion, txt_inp[0], txt_out[0])
    #stop_btn1_evt = stop_btn1.click(clear, None, txt_out[0], cancels=strt_btn1_evt)

if __name__ == '__main__':
    #demo.queue(default_concurrency_limit=2)
    demo.queue()
    demo.launch(debug=True)
