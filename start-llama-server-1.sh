#!/bin/bash

#export LLAMA_ARG_THREADS=32
#export LLAMA_ARG_N_PARALLEL=4

/llm/llama-server -m /app/models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf -t 32 --port 8081 -np 4
