from fastapi import FastAPI
import psutil

app = FastAPI()

@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.get('/cpu-percent')
def get_cpu_percent():
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    return {'cpu-percent': cpu_percent}
