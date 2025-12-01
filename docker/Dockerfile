FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /app

# Install Python dependencies
# Using spacy[cuda11x] for GPU acceleration
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir \
    "spacy[cuda11x]" \
    spacy-transformers \
    torch \
    pandas \
    numpy \
    tqdm \
    cupy-cuda11x

# Download spaCy models
RUN python3 -m spacy download en_core_web_sm
RUN python3 -m spacy download en_core_web_trf

# Set the entrypoint
CMD ["/bin/bash"]
