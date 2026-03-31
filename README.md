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
docker build -t local/llama.cpp:server-cuda-20260330 \
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

* http://localhost:8096/servers/time/mcp
* http://localhost:8096/servers/fetch/mcp
* http://localhost:8096/servers/ddg-search/mcp

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

Opencode runs in the terminal, and I want to let it use the above llama-server, but operate on any one project's files. I've deliberately chosen this way so that the opencode interaction is assistive, and only operating on a single repo at a time. It also has no access to git, so that the act of reviewing code changes is part of the workflow. 

The way I do it is to add a function in my `~/.bashrc` that starts the opencode docker container from whichever project directory I'm in. It points at the opencode.json file included here, and passes the current project directory as the workspace. 

```
opencode() {
  export OPENCODE_DIR="/home/mendhak/Projects/local-llm-workspace"
  export PROJECT_DIR="$(pwd)"
  docker compose -f "${OPENCODE_DIR}/compose-extras.opencode.yml" up -d opencode
  docker attach opencode
}

# or, without compose, just a throwaway session:

opencode() {
docker run -it --rm --network container:llama-server -v "/home/mendhak/Projects/llama-cpp-qwen-models/opencode.json:/root/.config/opencode/opencode.json" -v "${PWD}:/workspace" -w /workspace ghcr.io/anomalyco/opencode --agent plan
}
```

I can then just run `opencode` in any directory. It will start the container, connect to the llama server, and let me use opencode in that directory.

# Pi.dev

Pi.dev runs in the terminal, and I want to let it use the llama-server, but operate on any one project's files. I've deliberately chosen this way so that the pi.dev interaction is assistive, and only operating on a single repo at a time. It also has no access to git, so that the act of reviewing code changes is part of the workflow.

The way I do it is to add a function in my `~/.bashrc` that starts the pi.dev docker container from whichever project directory I'm in. It points at the pidev.json file included here, and passes the current project directory as the workspace. Note that the container starts with bash, so we use `docker exec` to launch pi inside it.

```
pidev() {
  export PIDEV_DIR="/home/mendhak/Projects/local-llm-workspace"
  export PROJECT_DIR="$(pwd)"
  docker compose -f "${PIDEV_DIR}/compose-extras.pidev.yml" up -d pidev
  if [ $# -eq 0 ]; then
    docker exec -it pidev pi
  else
    docker exec -it pidev pi -p "$*"
  fi
}

# or, without compose, just a throwaway session:

pidev() {
docker run -it --rm --network container:llama-server -v "/home/mendhak/Projects/local-llm-workspace/pidev.json:/root/.pi/agent/models.json" -v "${PWD}:/workspace" -w /workspace local/pidev pi
}
```

I can then just run `pidev` in any directory. It will start the container, connect to the llama server, and let me use pi.dev in that directory. You can also pass arguments to pi directly:

* `pidev` - starts pi interactively
* `pidev "your prompt"` - starts pi with your prompt passed via `-p`

Note: The container is pre-configured with the `pi-safeguard` and `pi-exa-mcp` extensions installed.

