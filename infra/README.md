# Infrastructure

Ansible playbooks and Kubernetes manifests for deploying the composer stack.

## Structure

```
infra/
  ansible/
    playbooks/
      setup-gpu-node.yaml    # Configure PC node for GPU workloads
      deploy-services.yaml   # Deploy all services to K8s
    inventory/
      hosts.yaml             # Cluster inventory
  k8s/
    namespace.yaml           # Kubernetes namespace
    composer/                # Composer service K8s manifests
```

## Node Layout

| Node | Role | Workloads |
|---|---|---|
| PC | GPU node | llm-server, training jobs |
| RPi (CI/CD) | Worker | GitHub Actions runner |
| RPi (others) | General | Other apps (avoid composer workloads) |

## Deployment Flow

1. GitHub Actions (on CI/CD Pi) builds container images
2. Tags images with version from `version.txt`
3. Pushes images to registry
4. Runs Ansible playbook to deploy to K8s cluster
