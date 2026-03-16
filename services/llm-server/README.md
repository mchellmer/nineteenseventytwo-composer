# llm-server

Local LLM hosting via [Ollama](https://ollama.ai) on Kubernetes, using the PC node's GPU.

## Purpose

Provides the LLM inference backend that the composer service calls for bossa
transformations. Runs Ollama in a container scheduled on the GPU-capable PC node.

## Architecture

- **Ollama** runs as a Kubernetes Deployment on the PC node (via nodeSelector)
- Models are stored on a PersistentVolume so they survive pod restarts
- Exposed as a ClusterIP Service (`llm-server:11434`) for internal access

## Setup

### 1. Label your PC node

```bash
kubectl label node <your-pc-node-name> gpu=true workload=llm
```

### 2. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
```

### 3. Pull a model

```bash
# Port-forward to access Ollama locally
kubectl port-forward svc/llm-server 11434:11434

# Pull the model
curl http://localhost:11434/api/pull -d '{"name": "llama3:8b"}'
```

### 4. Verify

```bash
curl http://localhost:11434/api/tags
```

## Recommended Models

| Model | Size | Use Case |
|---|---|---|
| `llama3:8b` | ~4.7GB | Good balance of quality and speed |
| `mistral:7b` | ~4.1GB | Fast, good at structured output |
| `codellama:13b` | ~7.4GB | Better at JSON generation |

For bossa arrangement, start with `llama3:8b` — it handles structured JSON
transformation well and fits comfortably in 16GB+ GPU memory.

## GPU Requirements

- NVIDIA GPU with CUDA support, or
- AMD GPU with ROCm support
- Minimum 8GB VRAM for 7B models, 16GB for 13B models
- Ollama auto-detects GPU and uses it if available

## Resource Limits

The K8s deployment requests:
- CPU: 2 cores
- Memory: 8Gi
- GPU: 1 (nvidia.com/gpu)

Adjust in `k8s/deployment.yaml` based on your hardware.
