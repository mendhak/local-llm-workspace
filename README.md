This project provides a local, self contained environment for running LLMs with chat or coding capabilities. It uses llama-server and opencode in docker containers, and provides some docker compose files to run various models.

Some aspects of the project are specific to my hardware, but the general approach should be transferable to other systems.  

# Motivation

I want to run LLMs locally for privacy, cost, and dependency reasons. While it won't achieve the same performance as cloud hosted models, it can be good enough for simple tasks like chat and coding. 

I also want to be able to run local models safely without compromising the security of my host system. This is achieved by running llama and opencode in isolated docker containers, and sharing only necessary files and ports. 




# Model download

These are various models I downloaded and tried and found useful. They can be interchanged in the docker compose files. 


| Model | Source | 
|-------|--------|
| **Qwen 3.5 35B** - `Qwen3.5-35B-A3B-MXFP4_MOE.gguf` | [unsloth/Qwen3.5-35B-A3B-GGUF](https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF) |
| **Qwen 3.5 35B** - `Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf` | [unsloth/Qwen3.5-35B-A3B-GGUF](https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF) |
| **Qwen 3.5 27B** - `Qwen3.5-27B.Q3_K_M.gguf` | [Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF](https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF) |
| **Qwen 3.5 27B** - `Qwen3.5-27B.Q4_K_S.gguf` | [Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF](https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF) |
| **Qwen 3.5 27B** - `Qwen3.5-27B-IQ4_XS.gguf` | [unsloth/Qwen3.5-27B-GGUF](https://huggingface.co/unsloth/Qwen3.5-27B-GGUF) |
| **Qwen 3.5 9B** - `Qwen3.5-9B-Q8_0.gguf` | [unsloth/Qwen3.5-9B-GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) |
| **Qwen 3 Coder Next** - `Qwen3-Coder-Next-MXFP4_MOE.gguf` | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) |
| **Qwen 3 Coder Next** - `Qwen3-Coder-Next-UD-IQ4_XS.gguf` | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) |
| **Qwen 3.5 4B** - `Qwen3.5-4B-Q4_K_M.gguf` | [unsloth/Qwen3.5-4B-GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) |

# Build llama.cpp for RTX 5080 and Cuda 13.1

On my system, the CUDA version was newer than the llama.cpp docker images had, so I had to build it myself. 

Clone https://github.com/ggml-org/llama.cpp, then:

```
docker build -t local/llama.cpp:server-cuda-20260307 \
--build-arg CUDA_VERSION=13.1.0 \
  --build-arg CUDA_DOCKER_ARCH=120 \
  --target server \
  -f .devops/cuda-new.Dockerfile .
```


# Running llama-server with various models 

In all cases, run the docker compose command, wait a bit, then browse to http://localhost:8080 



## Qwen3.5 35B, for general chat

This is a MOE - mixture of experts. It doesn't load the whole model into GPU, just parts as needed. It does work quite fast, good for general purpose chat. It can be used with the MCP for some web search capabilities.

```
docker compose -f docker-compose.35B.yml -f compose-extras.mcp.yml up 
```

I got about 65 tokens per second. 

To make use of the MCP servers, add these URLs in llama chat's MCP settings. Yes, it's `localhost`. 

* http://localhost:8096/server/time/mcp
* http://localhost:8096/server/fetch/mcp
* http://localhost:8096/server/ddg-search/mcp

## Qwen3.5 27B, for coding

A few variants here, the IQ4 is the most recent, and the Q3 is a bit faster. Both are good for coding. 

 IQ4 with opencode:

```
docker compose -f docker-compose.27B.IQ4.yml 
```

I got about 17 tokens per second

Q3 with opencode:

```
docker compose -f docker-compose.27B.Q3.yml up
```

I got about 38 tokens per second


## Qwen3 Coder, for coding

```
docker compose -f docker-compose.coder-next.yml up 
```
I got about 28 tokens per second

## Qwen3.5 9B Q8_0

```
docker compose -f docker-compose.9B.yml up llama-server
```

I get about 58 tokens per second

## Qwen3.5 4B, lightweight CPU option

A small, fast model that runs on CPU without requiring GPU. Good for simple tasks or systems without CUDA.

```
docker compose -f docker-compose.4BCPU.yml up
```

I get about 12 tokens per second



# Opencode

Opencode runs in the terminal, and we want to let it use the above llama-server, but operate on any project's files. 

The way I do it is to add a function in my `~/.bashrc` that starts the opencode docker container. It points at the config file included here, and passes the current directory as the workspace. 

```
opencode() {
docker run -it --rm --network container:llama-server -v "/home/mendhak/Projects/llama-cpp-qwen-models/opencode.json:/root/.config/opencode/opencode.json" -v "${PWD}:/workspace" -w /workspace ghcr.io/anomalyco/opencode
}
```

I can then just run `opencode` in any directory. It will start the container, connect to the llama server, and let me use opencode in that directory.



# Notes on benchmarking with llama-bench

This is a good way of running multiple benchmarks in one go, it outputs the processing speed and token generation speed. 

```
docker run --rm  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full20260307 -m /models/Qwen3.5-9B-Q8_0.gguf -ngl 99 -b 4096,8192,16384 -ub 512,1024,2048,4096,8192 -t 8 -fa 1 -ctk q8_0,f16,bf16,q4_0 -ctv q8_0,f16,bf16,q4_0 -p 512 -n 128 --mmap 1,0 
```


---


<details>
  
  <summary>Testing Notes</summary>

  
## Running llama-bench


  For the 9B:

```
docker run --rm  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full20260307 -m /models/Qwen3.5-9B-Q8_0.gguf -ngl 99 -b 4096,8192,16384 -ub 512,1024,2048,4096,8192 -t 8 -fa 1 -ctk q8_0,f16,bf16,q4_0 -ctv q8_0,f16,bf16,q4_0 -p 512 -n 128 --mmap 1,0 

docker run --rm  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full20260307 -m /models/Qwen3.5-9B-Q8_0.gguf -ngl 99 -b 8192,16384 -ub 1024 -t 8 -fa 1 -ctk f16 -ctv f16 -p 512,2048,8192 -n 128,512,1024 -d 0,4096,8192,16384
```

Other bench: 

  ```
  docker run  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full -m /models/Qwen3.5-35B-A3B-MXFP4_MOE.gguf --n-prompt 1024 --n-gen 0 --batch-size 1024,2048 --n-gpu-layers 99 --n-cpu-moe 38 --flash-attn 1
  ```


## Using the official Cuda 12 image

```
docker run -e GGML_CUDA_GRAPH_OPT=1 --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models ghcr.io/ggml-org/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE_F16.gguf --port 8080 --host 0.0.0.0  -b 2048  -cmoe -c 131072  --min-p 0.05 --temp 1.0 --top-p 0.95 --top-k 40
```

7t/s

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models ghcr.io/ggml-org/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE_F16.gguf --port 8080 --host 0.0.0.0  
```

23t/s

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models ghcr.io/ggml-org/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE_BF16.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 
```

19t/s

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models ghcr.io/ggml-org/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE_F16.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 -c 64000 -fa 1 -np 1 --no-mmap
```


## Starting over with local image built for Cuda 13

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40
```

20-23 tokens/second. 

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --ctx-size 32768
```

19 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --ctx-size 32768 --flash-attn on
```

23 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --ctx-size 32768 --flash-attn on --no-mmap 
```

just crashes

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --ctx-size 32768 --flash-attn on --mlock
```

20-22 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --ctx-size 32768 --flash-attn on --mlock --n-gpu-layers 999
```

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --fit on
```

20-23 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --cpu-moe
```

7-10 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --n-cpu-moe 47
```

7-10 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --n-gpu-layers -1
```

28 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --n-gpu-layers -1 --ctx-size 32768 --flash-attn on --mlock
```

27 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 --temp 1.0 --top-p 0.95 --top-k 40 --n-gpu-layers -1 --ctx-size 16384 --threads 8  --mlock --flash-attn on
```

23-26 tokens/second

```
docker run --gpus all -p 8080:8080 -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda   -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf   --port 8080 --host 0.0.0.0   --n-gpu-layers -1   --ctx-size 32768   --flash-attn on
```

22-24 tokens/second
  
  </details>
