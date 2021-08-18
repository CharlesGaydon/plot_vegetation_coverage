# This script install torch 1.8.0 as well as compatible
# versions of torchnet and torch-scatter.

import os

os.system(
    "pip install torch==1.8.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html"
)
os.system("pip install torchnet")

# Install torch_scatter
import torch


def format_pytorch_version(version):
    return version.split("+")[0]


def format_cuda_version(version):
    return "cu" + version.replace(".", "")


TORCH_version = torch.__version__
TORCH = format_pytorch_version(TORCH_version)
print(TORCH)

CUDA_version = torch.version.cuda
CUDA = format_cuda_version(CUDA_version)
print(CUDA)

os.system(
    f"pip install torch-scatter -f https://pytorch-geometric.com/whl/torch-{TORCH}+{CUDA}.html"
)
os.system(
    f"pip install torch-cluster -f https://pytorch-geometric.com/whl/torch-{TORCH}+{CUDA}.html"
)
os.system("pip install torch-geometric")
