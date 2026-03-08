# Model download

From https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF/tree/main I downloaded Qwen3-Coder-Next-MXFP4_MOE.gguf

From https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF/tree/main I downloaded Qwen3.5-35B-A3B-MXFP4_MOE.gguf 

From https://huggingface.co/unsloth/Qwen3.5-27B-GGUF/tree/main I downloaded Qwen3.5-27B-IQ4_XS.gguf and Qwen3.5-27B-Q3_K_M.gguf


# Build llama.cpp for RTX 5080 and Cuda 13.1

Clone https://github.com/ggml-org/llama.cpp, then:

```
docker build -t local/llama.cpp:server-cuda-20260307 \
--build-arg CUDA_VERSION=13.1.0 \
  --build-arg CUDA_DOCKER_ARCH=120 \
  --target server \
  -f .devops/cuda-new.Dockerfile .
```


# Running Qwen3-Coder-Next-MXFP4_MOE.gguf

```
docker run --gpus all -p 8080:8080   -v /mnt/Extra/Models:/models ghcr.io/ggml-org/llama.cpp:server-cuda   -m /models/Qwen3-Coder-Next-MXFP4_MOE.gguf   --port 8080 --host 0.0.0.0   --temp 1.0 --top-p 0.95 --top-k 40   --n-gpu-layers -1   --ctx-size 32768   --flash-attn on   --no-warmup
```

Wait a bit then  browse to http://localhost:8080 

I got about 28 tokens per second

# Running Qwen3.5-35B-A3B-MXFP4_MOE.gguf

```
docker run --gpus all -p 8080:8080   -v /mnt/Extra/Models:/models local/llama.cpp:server-cuda   -m /models/Qwen3.5-35B-A3B-MXFP4_MOE.gguf --port 8080 --host 0.0.0.0 -c 32768 -ngl -1 -ctk q8_0 -ctv q8_0 -sm none -mg 0 -np 1 -fa on
```

I got about 65 tokens per second

---

Docker Compose

docker compose up # brings up llama and opencode

docker compose run --rm opencode # run opencode in a TUI


---


<details>
  
  <summary>Testing Notes</summary>
  
## Running llama-bench

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
