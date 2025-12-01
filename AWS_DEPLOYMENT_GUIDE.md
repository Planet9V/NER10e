# NER11 AWS Deployment Guide

This repository is designed to be **fully portable**. You can zip the `NER11_Gold_Standard` directory and deploy it to any machine with Docker and NVIDIA Drivers (e.g., AWS EC2 `g4dn.xlarge` or `p3.2xlarge`).

## 1. Preparation (Local)
Ensure you have the full "Gold Standard" directory structure:
```text
NER11_Gold_Standard/
├── custom_data/          # Source files & scripts
├── external_data/        # Standardized external datasets
├── final_training_set/   # The merged, cleaned .spacy files
├── env/                  # config.cfg
├── scripts/              # Python scripts
├── docker/               # Dockerfile & docker-compose.yml
└── models/               # Output directory
```

## 2. Transfer to AWS
1.  **Zip the directory**:
    ```bash
    tar -czvf ner11_package.tar.gz NER11_Gold_Standard/
    ```
2.  **SCP to AWS Instance**:
    ```bash
    scp -i your-key.pem ner11_package.tar.gz ubuntu@<aws-ip>:~/
    ```

## 3. Setup on AWS (Ubuntu Deep Learning AMI)
Connect to your instance and run:

```bash
# 1. Extract
tar -xzvf ner11_package.tar.gz
cd NER11_Gold_Standard

# 2. Build & Start Container
# This pulls the spaCy GPU image and mounts the current directory to /app/NER11_Gold_Standard
docker compose -f docker/docker-compose.yml up -d --build

# 3. Verify GPU Access
docker exec ner11_training_env nvidia-smi
```

## 4. Run Training
Execute the training command inside the container:
```bash
docker exec ner11_training_env python3 -m spacy train \
    /app/NER11_Gold_Standard/env/config.cfg \
    --output /app/NER11_Gold_Standard/models/ner11_v3 \
    --paths.train /app/NER11_Gold_Standard/final_training_set/train.spacy \
    --paths.dev /app/NER11_Gold_Standard/final_training_set/dev.spacy \
    --gpu-id 0
```

## 5. Monitor
Tail the logs or use the monitoring script:
```bash
docker exec ner11_training_env python3 /app/NER11_Gold_Standard/scripts/monitor_training.py
```
