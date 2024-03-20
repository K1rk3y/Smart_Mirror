import torch

# Check if GPU is available
if torch.cuda.is_available():
    # Get the GPU device ID
    device = torch.cuda.current_device()
    print("GPU Device ID:", device)
else:
    print("No GPU available.")
