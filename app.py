from functools import partial
import gradio as gr
import pandas as pd
import psutil, threading, time
import json, requests, statistics
import concurrent.futures

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

"""
app_urls = ['http://localhost:8081/completion',
        'http://localhost:8082/completion',
        'http://localhost:8083/completion',
        'http://localhost:8084/completion']
"""
app_urls = []
with open('app-urls.txt', 'r') as file:
    app_urls = [line.strip() for line in file]
    print(f'{app_urls = }')

def completion(txt, count, index):
    #print(f'+++ type(txt): {type(txt)} txt: {txt}')
    txts = prompts if not txt else [txt]*len(prompts)
    #txts = prompts
    print(f'+++ type(txts): {type(txts)} txts: {txts}')
    #print(f'+++ port: {port}')
    #url = f'http://localhost:{port}/completion'
    url = app_urls[index]
    print(f'+++ {url = }')
    data = {'prompt': txts, 'n_predict': 32}
    #gr.Info(f'Running inference: batch-size: 4', duration=3)
    for i in range(count):
        try:
            t0 = time.perf_counter()
            r = requests.post(url, json=data)
            r.raise_for_status()
            #print(r.status_code)
            #print(json.dumps(r.json(), indent=4))
            print(f'+++ Time taken: [{url}] [{i}] {time.perf_counter() - t0}')
            results_dict = r.json()['results']
            content = [ item['content'] for item in results_dict ]
            pred_n = sum( item['timings']['predicted_n'] for item in results_dict )
            pred_ms = statistics.mean( item['timings']['predicted_ms'] for item in results_dict )
            stats = f'batch-size: {len(txts)}\ttokens: {pred_n}\ttime: {pred_ms/1000:.1f}s'
            yield [content, stats]
        except requests.exceptions.RequestException as e:
            print(f'An error occurred: {e}', flush=True)
            #return None
            raise SystemExit(e)



# Create multiple functions
d = { f'completion{i}': partial(completion) for i in range(MAX_WINDOWS) }

#urls = [(url, start-cpu, numcpu), ...]
"""
urls = [('http://localhost:8000/cpu-percent', 0, 32),
        ('http://localhost:8000/cpu-percent', 32, 32),
        ('http://localhost:8000/cpu-percent', 80, 32),
        ('http://localhost:8000/cpu-percent', 112, 32)]
"""
api_urls = ()
with open('api-urls.txt', 'r') as file:
    api_urls = [tuple(line.strip().split(',')) for line in file]
    print(f'{api_urls = }')

def cpu_percent():
    def fetch_url_and_plot(data):
        url, start, ncores = data
        start = int(start)
        ncores = int(ncores)
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
        plots = list(executor.map(fetch_url_and_plot, api_urls))
        return plots


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
plots = []

clear = lambda: ""

start = '\U000025B6'
stop = '\U000023F9'

def update_start():
    return f'*Status: Running inference, batch_size:4*'

def update_stop():
    return f'*Status: Completed inference*'

with gr.Blocks(theme=gr.themes.Base()) as demo:
    with gr.Row(variant='panel'):
        #gr.set_static_paths(paths=["static/"])
        with gr.Column(variant='panel', scale=4):
            t1 = 'Llama-3-8B Scale Out'
            subtitle = 'on Ampere CPUs'
            gr.Markdown(f'<center><h1 style="font-size:3em">{t1}<br />{subtitle}</h1></center>')
        with gr.Column(variant='panel', scale=1):
            gr.Markdown('<img src="file/static/ampere_logo_primary_stacked_rgb.png" alt="images" border="0" style="float:right">')
            #gr.Markdown('<img src="/file=/static/ampere_logo_primary_stacked_rgb.png">')
            #gr.HTML('<img src="file/static/ampere_logo_primary_stacked_rgb.png" alt="images" border="0" style="float:right">')
            #gr.Image("/file=static/ampere_logo_primary_stacked_rgb.png")
    with gr.Group():
        with gr.Row(variant='panel'):
            """
            with gr.Column(min_width=64, variant='panel', scale=25):
                plot1 = gr.BarPlot()
            with gr.Column(min_width=64, variant='panel', scale=25):
                plot2 = gr.BarPlot()
            with gr.Column(min_width=64, variant='panel', scale=1):
                btn1 = gr.Button(start, variant='secondary', size='sm')
                btn2 = gr.Button(stop, variant='secondary', size='sm')
                btn1_evt = btn1.click(cpu_percent, None, [plot1, plot2], every=1)
                btn2.click(clear, None, None, cancels=btn1_evt)
            """
            for i in range(MAX_WINDOWS//2):
                with gr.Column(min_width=128, variant='panel'):
                    plots.append(gr.BarPlot())
        with gr.Row(variant='panel'):
            btn1 = gr.Button(start, variant='secondary', size='sm')
            btn2 = gr.Button(stop, variant='secondary', size='sm')
            btn1_evt = btn1.click(cpu_percent, None, plots, every=1)
            btn2.click(clear, None, None, cancels=btn1_evt)

    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS//2):
            with gr.Column(min_width=128, variant='panel'):
                gr.Markdown(f'User {i+1}')
                status = gr.Markdown(f'*Status: Ready to run*')
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(prompts, txt_inp[i], label='Prompts', examples_per_page=4))
                gr.Markdown(f'*Output Text and Stats*')
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                txt_stats.append(gr.Textbox(label='Output Stats', lines=1, container=False))
                #txt_stats.append(gr.Markdown(label='Output Text', show_label=True))
                #txt_stats.append(gr.JSON(container=False, min_width=100))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, min_width=10, minimum=1, scale=1))
                    #port = gr.Number(BASE_PORT + i, visible=False)
                    index = gr.Number(i, visible=False)
                    strt_btn = gr.Button(start, variant='secondary', size='sm', min_width=10, scale=2)
                    stop_btn = gr.Button(stop, variant='secondary', size='sm', min_width=10, scale=1)
                    strt_btn_evt = strt_btn.click(update_start, None, status).then(
                        d[f'completion{i}'], [txt_inp[i], numbers[i], index], [txt_out[i], txt_stats[i]], trigger_mode='once', show_progress='minimal').then(
                        update_stop, None, status)
                    stop_btn_evt = stop_btn.click(clear, None, None, cancels=strt_btn_evt)

    """
    with gr.Row(variant='panel'):
        for i in range(MAX_WINDOWS//2, MAX_WINDOWS):
            with gr.Column(min_width=128):
                gr.Markdown(f'*User {i+1}*')
                txt_inp.append(gr.Textbox(label='Input Text', container=False, placeholder='Prompt'))
                examples.append(gr.Examples(prompts, txt_inp[i], label='Prompts'))
                txt_out.append(gr.Textbox(label='Output Text', lines=4, max_lines=4, container=False))
                txt_stats.append(gr.Textbox(label='Output Stats', lines=1, container=False))
                #txt_stats.append(gr.Markdown())
                #txt_stats.append(gr.JSON(container=False))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(MAX_REQUESTS, label='Loop', container=False, min_width=10, minimum=1, scale=1))
                    port = gr.Number(BASE_PORT + i, visible=False)
                    strt_btn.append(gr.Button(start, variant='secondary', size='sm', min_width=10, scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button(stop, variant='secondary', size='sm', min_width=10, scale=1))
                    strt_btn_evt.append(strt_btn[i].click(d[f'completion{i}'], [txt_inp[i], numbers[i], port], [txt_out[i], txt_stats[i]], show_progress='minimal'))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, None, cancels=strt_btn_evt[i]))
    """

if __name__ == '__main__':
    demo.queue(default_concurrency_limit=4)
    demo.launch(server_name='0.0.0.0', allowed_paths=["static/ampere_logo_primary_stacked_rgb.png"], debug=True)
