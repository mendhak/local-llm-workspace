This project provides a local, self-contained environment for running LLMs with chat or coding capabilities. It uses llama-server and pi.dev in a docker container, and provides a preset configuration file to load the various models. 


Some aspects of the project are specific to my hardware, but the general approach should be transferable to other systems.  

# Motivation

I want to run LLMs locally for privacy, cost, and dependency reasons. While it won't achieve the same performance as cloud hosted models, it can be good enough for simple tasks like chat and coding. 

I also want to be able to run local models safely without compromising the security of my host system. This is achieved by running llama and pi.dev in isolated docker containers, and sharing only necessary files and ports.

The models chosen are aimed at running on my 16 GB VRAM system.

# Model download

These are various models I downloaded and tried and found useful.

* Qwen 35B 
* Qwen Coder Next
* Qwen 27B
* Gemma 4 26B



Each model download link is in the [configs/models.ini](configs/models.ini) file.

## How it works

STart the server with `docker compose up`, then open the web interface at http://localhost:9931 or use pi.dev to connect to it. 

The `docker-compose.yml` uses the latest official docker image, and runs llama-server in router mode - it just listens but doesn't load any model on startup.

The model to use can be selected from the web interface model selector or pi.dev's model selector.

The models are loaded from [configs/models.ini](configs/models.ini), each section has  arguments used to load that model optimally.


# Pi.dev

Pi.dev is an agent harness that runs in the terminal. I want to let it use the llama-server, and operate on any arbitrary directory. It runs in a docker container instead of the host system. 

I've deliberately chosen this way so that the pi.dev interaction is assistive, and only operating on a single repo at a time. It also has no access to git, so that the act of reviewing code changes is part of the workflow.

The way I do it is to add a function in my `~/.bashrc` that starts the pi.dev docker container from whichever project directory I'm in. It passes the current project directory as the workspace. Note that the container starts with bash, so we use `docker exec` to launch pi inside it.

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
docker run -it --rm --network host -v "${PWD}:/workspace" -w /workspace local/pidev pi
}
```

I can then just run `pidev` in any directory. It will start the container, connect to the llama server, and let me use pi.dev in that directory. You can also pass arguments to pi directly:

* `pidev` - starts pi interactively
* `pidev "your prompt"` - starts pi with your prompt passed via `-p`

The image is built with these extensions:

* pi-llama-cpp - for connecting to llama-server and automatically picking models
* pi-safeguard - prompts the user before executing some commands
* pi-exa-mcp - allows web search
* juicesharp/rpiv-ask-user-question - interactively ask user questions

## Updating pi.dev

When it's necessary to rebuild pi.dev, use

```
docker compose -f extras/pidev.yml build --no-cache
```

It's also a good idea to clear its data directory

```
docker compose -f extras/pidev.yml down && docker volume rm extras_pidev-data
```

# MCP

To make use of MCP servers in the llama.cpp web interface, start the server together with the MCP proxy:

```
docker compose -f docker-compose.yml -f extras/mcp.yml up
```

Then add these URLs in llama chat's MCP settings. Yes, it's `localhost`.

* http://localhost:8096/servers/time/mcp
* http://localhost:8096/servers/fetch/mcp
* http://localhost:8096/servers/ddg-search/mcp

# Helper scripts: finding which layers to offload to CPU

If you're GPU poor like me, you can offload the heaviest blocks of a model to CPU RAM with an `override-tensor` argument in `models.ini`. The two helper scripts figure out which blocks are heaviest for you:

```
uv run helper_gguf_layers_by_size_dense.py /mnt/Extra/Models/some-dense-model.gguf
uv run helper_gguf_layers_by_size_moe.py /mnt/Extra/Models/some-moe-model.gguf
```

They print the block sizes (heaviest first, MTP blocks excluded) and a ready-to-paste `override-tensor = blk.(...).ffn_.*=CPU` line. Keep removing blocks from the right until you hit out of memory, then go back one.