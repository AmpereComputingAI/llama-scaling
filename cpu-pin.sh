#!/bin/bash

#docker container update --cpuset-cpus 0-15  llama-aio-1
#docker container update --cpuset-cpus 16-31 llama-aio-2
#docker container update --cpuset-cpus 32-47 llama-aio-3
#docker container update --cpuset-cpus 48-64 llama-aio-4
#docker container update --cpuset-cpus 80-95  llama-aio-5
#docker container update --cpuset-cpus 96-111 llama-aio-6
#docker container update --cpuset-cpus 112-127 llama-aio-7
#docker container update --cpuset-cpus 128-143 llama-aio-8

# 32x4
docker container update --cpuset-cpus 0-31 --cpuset-mems 0 llama-aio-0
docker container update --cpuset-cpus 32-63 --cpuset-mems 0 llama-aio-1
#docker container update --cpuset-cpus 80-111 --cpuset-mems 1 llama-aio-2
#docker container update --cpuset-cpus 112-143 --cpuset-mems 1 llama-aio-3
