import copy
from functools import partial
import concurrent
import psutil
import gradio as gr
import requests
import pandas as pd
import threading

MAX_WINDOWS = 8
MAX_REQUESTS = 1
NUM_THREADS = 16
#MAX_CPUS = MAX_WINDOWS * NUM_THREADS
MAX_CPUS = 160

url = 'http://localhost:8080/completion'
prompts = [
    ["The Moon's orbit around Earth has"],
    ["Explore the Wonders of Space Exploration"],
    ["Mysterious island, hidden treasure inside"],
    ["Wildflowers blooming in the meadow"],
]

def completion_one(txt):
    data = {'prompt': txt, 'n_predict': 32}
    print(f'+++ Thread ID: {threading.current_thread().name}')
#    for i in range(count):
#        print(f'[{i}]: request post')
#        r = requests.post(url, json=data)
#        #print(r.status_code)
#        yield r.json()['content']
    #print(f'[{i}]: request post')
    try:
        r = requests.post(url, json=data)
        r.raise_for_status()
        #print(r.status_code)
        return r.json()['content']
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None

def completion(txt, count):
    # Create a ThreadPoolExecutor for parallel requests
    if not txt:
        txts = prompts
    else:
        txts = [ txt for i in range(len(prompts)) ]
    print(f'+++ txts: {txts}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=count, thread_name_prefix='my-thread') as executor:
        # Submit the requests and retrieve the responses
        futures = [executor.submit(completion_one, prompt) for prompt in txts]
        #responses = [future.result() for future in futures]
        #[ print(f'+++ {r}') for r in responses ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(f'+++ {result}')
            #yield responses
            yield result


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

start = '\U000025B6'
stop = '\U000023F9'

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
    with gr.Row():
        with gr.Column(variant='panel', scale=25):
            plot = gr.BarPlot()
        with gr.Column(min_width=64, variant='panel', scale=1):
            btn1 = gr.Button(start, variant='secondary', size='sm')
            btn2 = gr.Button(stop, variant='secondary', size='sm')
            btn1_evt = btn1.click(cpu_percent, None, plot, every=1)
            btn2.click(clear, None, None, cancels=btn1_evt)
    with gr.Row(variant='panel'):
        #for i in range(MAX_WINDOWS):
        for i in range(MAX_WINDOWS//2):
            with gr.Column(min_width=128, variant='panel'):
                gr.Markdown(f'*Client {i}*')
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(prompts, txt_inp[i]))
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, min_width=10, minimum=1, scale=1))
                    strt_btn.append(gr.Button(start, variant='secondary', size='sm', min_width=10, scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button(stop, variant='secondary', size='sm', min_width=10, scale=1))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i]], txt_out[i], trigger_mode='once'))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))

    with gr.Row(variant='panel'):
        #for i in range(MAX_WINDOWS):
        for i in range(MAX_WINDOWS//2, MAX_WINDOWS):
            with gr.Column(min_width=128):
                gr.Markdown(f'*Client {i}*')
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(prompts, txt_inp[i]))
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, min_width=10, minimum=1, scale=1))
                    strt_btn.append(gr.Button(start, variant='secondary', size='sm', min_width=10, scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button(stop, variant='secondary', size='sm', min_width=10, scale=1))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i]], txt_out[i]))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))

if __name__ == '__main__':
    demo.queue(default_concurrency_limit=MAX_WINDOWS)
    demo.launch(allowed_paths=["static/ampere_logo_primary_stacked_rgb.png"], debug=True)
