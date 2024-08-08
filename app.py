import gradio as gr
import requests

url = 'http://localhost:8081/completion'
ex_text = [
    ["The Moon's orbit around Earth has"],
    ["The smooth Borealis basin in the Northern Hemisphere covers 40%"],
]

def completion(txt:str, count:int):
    data = {'prompt': txt, 'n_predict': 32}
    for i in range(count):
        print(f'[{i}]: request post')
        r = requests.post(url, json=data)
        #print(r.status_code)
        yield r.json()['content']

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
        for i in range(2):
            with gr.Column():
                txt_inp.append(gr.Textbox(label='Input Text'))
                examples.append(gr.Examples(ex_text, txt_inp[i]))
                txt_out.append(gr.Textbox(label='Output Text', lines=4))
                with gr.Row(variant='panel'):
                    numbers.append(gr.Number(5, label='Loop', container=False, scale=0))
                    strt_btn.append(gr.Button('Start', variant='primary', scale=2))
                    #loop_btn.append(gr.Button('Loop', variant='primary'))
                    stop_btn.append(gr.Button('Stop', variant='stop', scale=1))
                    strt_btn_evt.append(strt_btn[i].click(completion, [txt_inp[i], numbers[i]], txt_out[i]))
                    stop_btn_evt.append(stop_btn[i].click(clear, None, txt_out[i], cancels=strt_btn_evt[i]))

#    strt_btn1_evt = strt_btn1.click(completion, inp1, out1)
#    stop_btn1_evt = stop_btn1.click(clear, None, out1, cancels=strt_btn1_evt)
    #strt_btn1_evt = strt_btn1.click(completion, txt_inp[0], txt_out[0])
    #stop_btn1_evt = stop_btn1.click(clear, None, txt_out[0], cancels=strt_btn1_evt)

if __name__ == '__main__':
    demo.queue()
    demo.launch(debug=True)
