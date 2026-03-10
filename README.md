# Model download

From https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF/tree/main I downloaded Qwen3-Coder-Next-MXFP4_MOE.gguf

From https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF/tree/main I downloaded Qwen3.5-35B-A3B-MXFP4_MOE.gguf 

From https://huggingface.co/unsloth/Qwen3.5-27B-GGUF/tree/main I downloaded Qwen3.5-27B-IQ4_XS.gguf and Qwen3.5-27B-Q3_K_M.gguf

From https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/tree/main I downloaded Qwen3.5-9B-Q8_0.gguf

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


Qwen3 Coder

```
docker compose -f docker-compose.coder-next.yml up llama-server
```
I got about 28 tokens per second

Qwen3.5 35B

```
docker compose -f docker-compose.35B.yml up llama-server
```

I got about 65 tokens per second

Qwen3.5 27B IQ4

```
docker compose -f docker-compose.27B.IQ4.yml up llama-server
```

I got about 17 tokens per second

Qwen3.5 27B Q3_K_M

```
docker compose -f docker-compose.27B.Q3.yml up llama-server
```

I got about 38 tokens per second

Qwen3.5 9B Q8_0

```
docker compose -f docker-compose.9B.yml up llama-server
```

I get about 58 tokens per second


## Benchmarking with llama-bench

This is a good way of running multiple benchmarks in one go, it outputs the processing speed and token generation speed. 

```
docker run --rm  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full20260307 -m /models/Qwen3.5-9B-Q8_0.gguf -ngl 99 -b 4096,8192,16384 -ub 512,1024,2048,4096,8192 -t 8 -fa 1 -ctk q8_0,f16,bf16,q4_0 -ctv q8_0,f16,bf16,q4_0 -p 512 -n 128 --mmap 1,0 
```



---

## Opencode

Docker Compose

docker compose up # brings up llama and opencode

docker compose run --rm opencode # run opencode in a TUI


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
