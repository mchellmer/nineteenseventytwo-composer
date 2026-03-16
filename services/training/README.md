# training

Fine-tuning pipeline for bossa arrangement models.

## Purpose

Train a local LLM to be better at bossa jazz arrangement by fine-tuning on
your example arrangements. Uses LoRA (Low-Rank Adaptation) to keep costs
and compute requirements minimal.

## How It Works

### 1. Dataset Preparation

Provide pairs of:
- **Input**: Piano MusicXML (original score)
- **Output**: Arranged MusicXML (your manual bossa arrangement)

The pipeline converts these into training examples using the intermediate
representation from `musicxml-tools`:

```
data/
  pairs/
    song1/
      input.musicxml     # original piano score
      output.musicxml    # your bossa arrangement
    song2/
      input.musicxml
      output.musicxml
  bossa_references/
    favourite1.musicxml  # reference bossa songs for style
    favourite2.musicxml
```

### 2. Training

Uses [Unsloth](https://github.com/unslothai/unsloth) or
[PEFT](https://github.com/huggingface/peft) for efficient LoRA fine-tuning:

- Base model: Llama 3 8B (or Mistral 7B)
- Method: QLoRA (4-bit quantized LoRA)
- VRAM needed: ~6GB for 7B model with QLoRA
- Training time: A few hours on a consumer GPU

### 3. Export

Export the fine-tuned model to GGUF format for Ollama:

```bash
python -m training.export --output model.gguf
# Then load into Ollama:
# ollama create bossa-arranger -f Modelfile
```

## Quick Start

```bash
cd services/training
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Prepare dataset from your MusicXML pairs
python -m training.prepare_dataset --data-dir data/pairs --output data/training.jsonl

# Fine-tune
python -m training.train --dataset data/training.jsonl --output models/bossa-lora

# Evaluate
python -m training.evaluate --model models/bossa-lora --test-dir data/pairs
```

## Dataset Size

Even 5-10 high-quality arrangement pairs can meaningfully improve the model's
bossa transformation quality. More is better, but start small and iterate.

You can also use the bossa reference songs to generate synthetic training data
by having the base model attempt arrangements and then rating/correcting them.
