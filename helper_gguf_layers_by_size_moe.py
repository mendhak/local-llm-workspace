# /// script
# dependencies = [
#     "gguf",
# ]
# ///

import sys

import gguf

model_path = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Error: No file passed", 1)
reader = gguf.GGUFReader(model_path)

block_scores = {}
mtp_block_indexes = []

for tensor in reader.tensors:
    name = tensor.name

    # Check for MTP (Multi-Token Prediction) layers to exclude
    if ".nextn." in name or "shared_head" in name:
        if name.startswith("blk."):
            block_index = int(name.split(".")[1])
            if block_index not in mtp_block_indexes:
                mtp_block_indexes.append(block_index)
        continue

    # Target MoE expert weights (captures ffn_gate_exps, ffn_up_exps, ffn_down_exps, etc.)
    if "_exps" in name or ".ffn_exp" in name:
        block_index = int(name.split(".")[1])
        weight_size = tensor.n_bytes

        if block_index not in block_scores:
            block_scores[block_index] = 0

        block_scores[block_index] += weight_size

# Remove any detected MTP blocks from the list
for mtp_index in mtp_block_indexes:
    if mtp_index in block_scores:
        block_scores.pop(mtp_index)

# Sort blocks by total Expert MB size (heaviest first)
sorted_blocks = sorted(block_scores.keys(), key=lambda k: block_scores[k], reverse=True)

print("MoE Expert Block Sizes (heaviest first):")
for block_index in sorted_blocks:
    size_mb = block_scores[block_index] / (1024 * 1024)
    print(f"Block {block_index:2d}: Expert Size = {size_mb:.2f} MB")

regex_group = "|".join(map(str, sorted_blocks))

# Target expert tensors specifically for CPU offload
override_arg = f"--override-tensor 'blk\\.({regex_group})\\.ffn_.*_exps.*=CPU'"

print("\nGenerated --override-tensor argument for MoE:")
print(override_arg)