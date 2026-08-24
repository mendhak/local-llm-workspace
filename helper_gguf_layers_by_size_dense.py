# /// script
# dependencies = [
#     "gguf",
# ]
# ///

"""
Use this script to figure out the heaviest blocks in a GGUF model. 
It can then be used in an override tensor argument to move the heaviest blocks to CPU memory, and that can help loading GGUF models for GPU poor people like me. 
Learned from: https://www.reddit.com/r/LocalLLM/comments/1vq5oyu/guide_for_running_dense_models_on_16_gb_vram_qwen/

uv run helper_gguf_layers_by_size.py '/mnt/Extra/Models/Qwen3.8-27B-UD-Q4_K_M.gguf'
"""

import sys

import gguf

model_path = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Error: No file passed", 1)
reader = gguf.GGUFReader(model_path)

block_scores = {}
mtp_block_indexes = []

for tensor in reader.tensors:
    name = tensor.name

    # Check if the tensor belongs to an MTP (Multi-Token Prediction) head
    if ".nextn." in name or "shared_head" in name:
        if name.startswith("blk."):
            block_index = int(name.split(".")[1])
            if block_index not in mtp_block_indexes:
                mtp_block_indexes.append(block_index)
        continue

    # Check for standard FFN layer weights
    if ".ffn_down.weight" in name or ".ffn_up.weight" in name or ".ffn_gate.weight" in name:
        block_index = int(name.split(".")[1])
        weight_size = tensor.n_bytes

        if block_index not in block_scores:
            block_scores[block_index] = 0

        block_scores[block_index] += weight_size

# Remove any detected MTP blocks from the score list, you don't want to remove those. 
for mtp_index in mtp_block_indexes:
    if mtp_index in block_scores:
        block_scores.pop(mtp_index)

sorted_blocks = sorted(block_scores.keys(), key=lambda k: block_scores[k], reverse=True)

print("Block Scores (heaviest first):")
for block_index in sorted_blocks:
    size_mb = block_scores[block_index] / (1024 * 1024)
    print(f"Block {block_index}: Size = {size_mb:.2f} MB")

regex_group = "|".join(map(str, sorted_blocks))
override_arg = f"--override-tensor 'blk\\.({regex_group})\\.ffn_.*=CPU'"

print("\n\n\nGenerated --override-tensor argument:")
print("\nKeep removing from the right until you reach out of memory, then go back one")
print(override_arg)
