from functools import partial
#import concurrent
import gradio as gr
import requests
import pandas as pd
import psutil, threading, time

MAX_WINDOWS = 8
MAX_REQUESTS = 3
NUM_THREADS = 16
#MAX_CPUS = MAX_WINDOWS * NUM_THREADS
MAX_CPUS = 64
BASE_PORT = 8081

#url = 'http://localhost:8081/completion'
prompts = [
    "The Moon's orbit around Earth has",
    "Explore the Wonders of Space Exploration",
    "Mysterious island, hidden treasure inside",
    "Wildflowers blooming in the meadow"
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

"""
def completion(txt, count):
    # Create a ThreadPoolExecutor for parallel requests
    txts = prompts if not txt else [ txt for i in range(len(prompts)) ]
    print(f'+++ type(txts): {type(txts)} txts: {txts}')

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
"""
import json
import statistics

def completion(txt, count, port):
    # Create a ThreadPoolExecutor for parallel requests
    #txts = prompts if not txt else [ txt for i in range(len(prompts)) ]
    txts = prompts
    #print(f'+++ type(txts): {type(txts)} txts: {txts}')
    print(f'+++ port: {port}')
    url = f'http://localhost:{port}/completion'
    data = {'prompt': txts, 'n_predict': 32}
    for i in range(count):
        try:
            t0 = time.perf_counter()
            r = requests.post(url, json=data)
            r.raise_for_status()
            #print(r.status_code)
            #return r.json()['content']
            print(f'+++ Time taken: [{port}] [{i}] {time.perf_counter() - t0}')
            #r_dict = r.json().values()
            #print(f'+++ {type(r_dict)}')
            #r_dict = r.json()["results"][0]
            #print(f'+++ {r_dict}')
            #r_dict_list = list(list(r_dict)[0])
            #for i in r_dict_list:
            #    print(f'+++ {type(i)}')
            #print(f'{r_dict_list[0].keys()}')
            #print(f'{r_dict_list[0].values()}')

            #print(f'+++ {list(r_dict.keys())}')
            #print(f'+++ {list(r_dict.values())}')
            #print(json.dumps(r.json(), indent=4))
            results_dict = r.json()['results']
            content = [ item['content'] for item in results_dict ]
            pred_n = sum( item['timings']['predicted_n'] for item in results_dict )
            pred_ms = statistics.mean( item['timings']['predicted_ms'] for item in results_dict )
            stats = f'sequences: {len(txts)}    tokens: {pred_n}    time: {pred_ms/1000:.1f}s'
            yield [content, stats]
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
            return None



# Create multiple functions
d = { f'completion{i}': partial(completion) for i in range(MAX_WINDOWS) }

import concurrent.futures
import requests

#urls = [(url, start-cpu, numcpu), ...]
urls = [('http://localhost:8000/cpu-percent', 0, 64),
        ('http://localhost:8000/cpu-percent', 80, 64)]

def cpu_percent():
    #cpu_num = range(MAX_CPUS)
    #cpu_util = psutil.cpu_percent(interval=1, percpu=True)
    #df = pd.DataFrame({'CPU': cpu_num, 'Percent': cpu_util[:MAX_CPUS]})
    #return gr.BarPlot(df, x='CPU', y='Percent', title='CPU Usage', x_lim=[0, MAX_CPUS-1], y_lim=[0, 100], container=False)

    def fetch_url_and_plot(data):
        # Simulate a URL fetch operation (replace with your actual implementation)
        url, start, ncores = data
        end = start + ncores
        #print(f'+++: start: {start} end: {end}')
        try:
            r = requests.get(url)
            r.raise_for_status()
            cpu_util = r.json()['cpu-percent']
            df = pd.DataFrame({'CPU': range(start, end), 'Percent': cpu_util[start:end]})
            return gr.BarPlot(df, x='CPU', y='Percent', title='CPU Usage', x_lim=[start, end-1], y_lim=[0, 100], container=False)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
            return []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        plots = list(executor.map(fetch_url_and_plot, urls))
        return plots


"""
import numpy as np
import plotly.express as px

def cpu_percent():
    cpu_data = psutil.cpu_percent(percpu=True)
    #return px.bar(x=range(len(cpu_data)), y=cpu_data)
    #data = np.array(cpu_data[:64]).reshape(-1,32)
    #return px.imshow(data)
    #fig = px.imshow(data,
    #                labels=dict(x="CPUs", y="CPUs", color="Utilization"),
    #                x = [ i for i in range(0, data.shape[1]) ],
    #                y = [ i for i in range(0, data.shape[0]) ],
    #                color_continuous_scale=["green", "yellow", "red"])
    #fig['layout']['yaxis']['autorange'] = "reversed"
    #fig.update_xaxes(showline=True, linecolor='black', linewidth=1, mirror=True)
    #fig.update_yaxes(showline=True, linecolor='black', linewidth=1, mirror=True)
    #return fig

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    cpu_num = list(map(str, range(MAX_CPUS)))
    ax.bar(cpu_num, cpu_data[:64])

    return plt
"""


txt_inp = []
txt_out = []
txt_stats = []
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

with gr.Blocks(theme=gr.themes.Glass()) as demo:
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
            plot1 = gr.BarPlot()
            plot2 = gr.BarPlot()
        with gr.Column(min_width=64, variant='panel', scale=1):
            btn1 = gr.Button(start, variant='secondary', size='sm')
            btn2 = gr.Button(stop, variant='secondary', size='sm')
            btn1_evt = btn1.click(cpu_percent, None, [plot1, plot2], every=1)
            btn2.click(clear, None, None, cancels=btn1_evt)
    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS//2):
            with gr.Column(min_width=128, variant='panel'):
                gr.Markdown(f'*User {i+1}*')
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(prompts, txt_inp[i], label='Prompts', examples_per_page=4))
                gr.Markdown(f'*Output Text and Stats*')
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                txt_stats.append(gr.Textbox(label='Output Stats', lines=1, container=False))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, min_width=10, minimum=1, scale=1))
                    port = gr.Number(BASE_PORT + i, visible=False)
                    strt_btn.append(gr.Button(start, variant='secondary', size='sm', min_width=10, scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button(stop, variant='secondary', size='sm', min_width=10, scale=1))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i], port], [txt_out[i], txt_stats[i]], trigger_mode='once'))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, None, cancels=strt_btn_evt[i]))

    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS//2, MAX_WINDOWS):
            with gr.Column(min_width=128):
                gr.Markdown(f'*User {i+1}*')
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(prompts, txt_inp[i], label='Prompts'))
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                txt_stats.append(gr.Textbox(label='Output Stats', lines=1, container=False))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, min_width=10, minimum=1, scale=1))
                    port = gr.Number(BASE_PORT + i, visible=False)
                    strt_btn.append(gr.Button(start, variant='secondary', size='sm', min_width=10, scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button(stop, variant='secondary', size='sm', min_width=10, scale=1))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i], port], [txt_out[i], txt_stats[i]]))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, None, cancels=strt_btn_evt[i]))

if __name__ == '__main__':
    demo.queue(default_concurrency_limit=4)
    demo.launch(allowed_paths=["static/ampere_logo_primary_stacked_rgb.png"], debug=True)
