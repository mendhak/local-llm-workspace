This project provides a local, self contained environment for running LLMs with chat or coding capabilities. It uses llama-server and opencode in docker containers, and provides some docker compose files to run various models.

Some aspects of the project are specific to my hardware, but the general approach should be transferable to other systems.  

# Motivation

I want to run LLMs locally for privacy, cost, and dependency reasons. While it won't achieve the same performance as cloud hosted models, it can be good enough for simple tasks like chat and coding. 

I also want to be able to run local models safely without compromising the security of my host system. This is achieved by running llama and opencode in isolated docker containers, and sharing only necessary files and ports. 




# Model download

These are various models I downloaded and tried and found useful. They can be interchanged in the docker compose files. 


| Model | Source | Used In |
|-------|--------|---------|
| **Qwen3.6 35B** - `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` | [unsloth/Qwen3.6-35B-A3B-GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF) | `chat/qwen35B.yml` |
| **Qwen3.6 35B** - `Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf` | [unsloth/Qwen3.6-35B-A3B-GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF) | `coding/qwen35B.yml` |
| **Qwen3.5 27B** - `Qwen3.5-27B-IQ4_XS.gguf` | [unsloth/Qwen3.5-27B-GGUF](https://huggingface.co/unsloth/Qwen3.5-27B-GGUF) | `coding/qwen27B.IQ4.yml` |
| **Qwen3.5 27B** - `Qwen3.5-27B-Q3_K_M.gguf` | [Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF](https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF) | `coding/qwen27B.IQ3.yml` |
| **Qwen3 Coder Next** - `Qwen3-Coder-Next-UD-Q4_K_M.gguf` | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | `coding/qwen.codernext.yml` |
| **Qwen3.5 9B** - `Qwen3.5-9B-Q8_0.gguf` | [unsloth/Qwen3.5-9B-GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) | `lightweight/qwen9B.yml` |
| **Qwen3.5 4B** - `Qwen3.5-4B-Q4_K_M.gguf` | [unsloth/Qwen3.5-4B-GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) | `lightweight/qwen4B.yml` |
| **Gemma 4 26B** - `gemma-4-26B-A4B-it-UD-IQ4_NL.gguf` | [google/gemma-4-it](https://huggingface.co/google/gemma-4-it) | `chat/gemma4.yml` |

# Build llama.cpp for RTX 5080 and Cuda 13.1

On my system, the CUDA version was newer than the llama.cpp docker images had, so I had to build it myself. 

Clone https://github.com/ggml-org/llama.cpp, then:

```
docker build -t local/llama.cpp:server-cuda-20260402 \
--build-arg CUDA_VERSION=13.1.0 \
  --build-arg CUDA_DOCKER_ARCH=120 \
  --target server \
  -f .devops/cuda-new.Dockerfile .
```


# Running llama-server with various models 

In all cases, run the docker compose command, wait a bit, then browse to http://localhost:8080 



## Qwen3.6 35B, for chat

This is a MOE - mixture of experts. It doesn't load the whole model into GPU, just parts as needed. It does work quite fast, good for general purpose chat. It can be used with the MCP for some web search capabilities.

```
docker compose -f chat/qwen35B.yml -f extras/mcp.yml up 
```

I got about 65 tokens per second. 

To make use of the MCP servers, add these URLs in llama chat's MCP settings. Yes, it's `localhost`. 

* http://localhost:8096/servers/time/mcp
* http://localhost:8096/servers/fetch/mcp
* http://localhost:8096/servers/ddg-search/mcp

## Qwen3.6 35B, for coding


The same model but with slightly different parameters. To use it: 

```
docker compose -f coding/qwen35B.yml up
```



## Qwen3 Coder Next, for coding

```
docker compose -f coding/qwen.codernext.yml up 
```


## Qwen3.5 9B Q8_0

```
docker compose -f lightweight/qwen9B.yml up llama-server
```


## Qwen3.5 4B, lightweight CPU option

A small, fast model that runs on CPU without requiring GPU. Good for simple tasks or systems without CUDA.

```
docker compose -f lightweight/qwen4B.yml up
```

# Pi.dev

Pi.dev runs in the terminal, and I want to let it use the llama-server, but operate on any one project's files. I've deliberately chosen this way so that the pi.dev interaction is assistive, and only operating on a single repo at a time. It also has no access to git, so that the act of reviewing code changes is part of the workflow.

The way I do it is to add a function in my `~/.bashrc` that starts the pi.dev docker container from whichever project directory I'm in. It points at the pidev.json file included here, and passes the current project directory as the workspace. Note that the container starts with bash, so we use `docker exec` to launch pi inside it.

```
pidev() {
  export PIDEV_DIR="/home/mendhak/Projects/local-llm-workspace"
  export PROJECT_DIR="$(pwd)"
  docker compose -f "${PIDEV_DIR}/extras/pidev.yml" up -d pidev
  if [ $# -eq 0 ]; then
    docker exec -it pidev pi
  else
    docker exec -it pidev pi -p "$*"
  fi
}

# or, without compose, just a throwaway session:

pidev() {
docker run -it --rm --network container:llama-server -v "/home/mendhak/Projects/local-llm-workspace/configs/pidev.json:/root/.pi/agent/models.json" -v "${PWD}:/workspace" -w /workspace local/pidev pi
}
```

I can then just run `pidev` in any directory. It will start the container, connect to the llama server, and let me use pi.dev in that directory. You can also pass arguments to pi directly:

* `pidev` - starts pi interactively
* `pidev "your prompt"` - starts pi with your prompt passed via `-p`

Note: The container is pre-configured with the `pi-safeguard` and `pi-exa-mcp` extensions installed.


# Opencode

Opencode runs in the terminal, and I want to let it use the above llama-server, but operate on any one project's files. I've deliberately chosen this way so that the opencode interaction is assistive, and only operating on a single repo at a time. It also has no access to git, so that the act of reviewing code changes is part of the workflow. 

The way I do it is to add a function in my `~/.bashrc` that starts the opencode docker container from whichever project directory I'm in. It points at the opencode.json file included here, and passes the current project directory as the workspace. 

```
opencode() {
  export OPENCODE_DIR="/home/mendhak/Projects/local-llm-workspace"
  export PROJECT_DIR="$(pwd)"
  docker compose -f "${OPENCODE_DIR}/extras/opencode.yml" up -d opencode
  docker attach opencode
}

# or, without compose, just a throwaway session:

opencode() {
docker run -it --rm --network container:llama-server -v "/home/mendhak/Projects/llama-cpp-qwen-models/configs/opencode.json:/root/.config/opencode/opencode.json" -v "${PWD}:/workspace" -w /workspace ghcr.io/anomalyco/opencode --agent plan
}
```

I can then just run `opencode` in any directory. It will start the container, connect to the llama server, and let me use opencode in that directory.


# Notes on benchmarking with llama-bench

This is a good way of running multiple benchmarks in one go, it outputs the processing speed and token generation speed.

Build this in llama.cpp project directory:

```
docker build -t local/llama.cpp:full-20260418 \
--build-arg CUDA_VERSION=13.1.0 \
  --build-arg CUDA_DOCKER_ARCH=120 \
  --target full \
  -f .devops/cuda.Dockerfile .
```

Then run the benchmark. Examples: 

```
docker run --rm  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full-20260418 -m /models/Qwen3.5-9B-Q8_0.gguf -ngl 99 -b 4096,8192,16384 -ub 512,1024,2048,4096,8192 -t 8 -fa 1 -ctk q8_0,f16,bf16,q4_0 -ctv q8_0,f16,bf16,q4_0 -p 512 -n 128 --mmap 1,0 

docker run --rm  --gpus all -v /mnt/Extra/Models:/models --entrypoint ./llama-bench local/llama.cpp:full-20260418 -m /models/Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf --fit-target 512 --fit-ctx 65536,131072,262144
```


## TODO

Try guardrail plugins for pi. These are:

* https://github.com/dtmirizzi/pi-governance 
* https://github.com/aliou/pi-guardrails 
* https://github.com/mgabor3141/yapp  (pi-safeguard) 