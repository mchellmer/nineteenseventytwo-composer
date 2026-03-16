# nineteenseventytwo-composer

AI-powered music arrangement tool that takes piano scores in MusicXML and outputs
re-arranged scores in bossa jazz style.

## What It Does

Takes a piano score (MusicXML) and produces a full arrangement:

- **Alto Sax** — top treble line extracted and rephrased for bossa feel
- **Piano Harmony** — middle voices with bossa voicings
- **Piano Bass** — bottom line transformed to bossa bass patterns
- **Drums** — generated bossa drum track that fits the bass line

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    composer (API)                        │
│  FastAPI service orchestrating the arrangement pipeline  │
│                                                         │
│  1. Parse input MusicXML          (musicxml-tools)      │
│  2. Split voices                  (musicxml-tools)      │
│  3. Transform bass → bossa        (LLM-assisted)        │
│  4. Adjust harmony voicings       (LLM-assisted)        │
│  5. Phrase sax melody             (LLM-assisted)        │
│  6. Generate bossa drums          (rule-based + LLM)    │
│  7. Reassemble output MusicXML    (musicxml-tools)      │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
     ┌───────▼───────┐         ┌───────▼───────┐
     │ musicxml-tools│         │   llm-server  │
     │ Python lib    │         │   Ollama on   │
     │ music21-based │         │   K8s (GPU)   │
     └───────────────┘         └───────────────┘
```

## Monorepo Structure

```
services/
  musicxml-tools/    Core MusicXML parsing, voice splitting, reassembly
  composer/          Arrangement orchestration API
  llm-server/        Local LLM deployment (Ollama on K8s)
  training/          Fine-tuning pipeline for bossa style models
infra/
  ansible/           Node configuration playbooks
  k8s/               Kubernetes manifests
.github/
  workflows/         CI/CD pipelines (build, tag, deploy)
examples/
  input/             Sample piano MusicXML scores
  output/            Example arranged outputs
```

Each service follows the convention:
- `version.txt` — current version (used by CI/CD for image tagging)
- `CHANGELOG.md` — version history
- `README.md` — service-specific docs
- `Dockerfile` — container build

## Infrastructure

- **LLM hosting**: Ollama on Kubernetes, running on PC node with GPU
- **CI/CD**: GitHub Actions on Raspberry Pi worker → build image → tag from version.txt → deploy via Ansible
- **Cluster**: K8s with PC node (GPU workloads) + Raspberry Pi nodes (lightweight services only)

## Getting Started

See individual service READMEs for setup instructions. Start with:

1. `services/musicxml-tools/` — the foundation for all MusicXML processing
2. `services/llm-server/` — get a local LLM running
3. `services/composer/` — the main arrangement service
4. `services/training/` — fine-tune on your bossa examples

## Tech Stack

- **Python 3.12+** with [music21](https://web.mit.edu/music21/) for MusicXML processing
- **FastAPI** for the composer service API
- **Ollama** for local LLM inference
- **Kubernetes** for orchestration
- **Ansible** for deployment
- **GitHub Actions** for CI/CD