#!/bin/bash

llama_image='ghcr.io/amperecomputingai/llama.cpp:1.2.6'

ncores=32
start=0
end=0
mem_node=0

for i in {0..3}; do
    echo "Welcome, iteration $i!"
    #start=$(( $i * $ncores ))
    #end=$(( $start + $ncores - 1))
    suffix=$(( $i + 1 ))
    end=$(( $start + $ncores - 1 ))
    if [ $end -gt 80 ]; then
        mem_node=1
    fi
    echo "cpu: $start-$end mem_node: $mem_node"
    docker run -d -it --rm --network host \
        --name "llama-aio-$i" \
        -v $HOME:/app -w /app \
        --cpuset-cpus $start-$end \
        --cpuset-mems $mem_node \
        --entrypoint "./dev/llama-scaling/start-llama-server-$suffix.sh" \
        $llama_image

    start=$(( $end + 1 ))
    if [ $i -eq 1 ]; then
        start=80
    fi
done

#./cpu-pin.sh

#--cpuset-cpus $start-$end \
#--entrypoint "./dev/llama-scaling/start-llama-server-5.sh" \
#docker container update --cpuset-cpus 0-15  llama-aio-1
