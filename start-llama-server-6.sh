#!/bin/bash

/llm/llama-server -m /app/models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf -t 32 --port 8086 -np 4
