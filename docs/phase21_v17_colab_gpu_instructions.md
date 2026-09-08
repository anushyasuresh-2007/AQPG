# AQPG V17 Remediation — Google Colab GPU Training Instructions

> **Operational Strategy**: Clean, reproducible V17 fine-tuning run on NVIDIA GPU (T4 / V100 / A100) using verified V17 datasets.

---

## 1. Directory Setup on Google Drive

Create an `AQPG` folder in your Google Drive root (`MyDrive/AQPG`) and upload the following files:

```
MyDrive/AQPG/
├── phase21_step3_v17_train_dataset.jsonl       (29.4 MB / 40,000 records)
├── phase21_step3_v17_validation_dataset.jsonl  (7.35 MB / 10,000 records)
├── phase21_v17_colab/
│   ├── phase21_v17_gpu_training.ipynb
│   ├── train_flan_t5_v17_gpu.py
│   ├── phase21_v17_gpu_training_config.json
│   └── phase21_v17_dataset_manifest.json
```

---

## 2. Google Colab Execution Workflow

1. Open **Google Colab** and select **File -> Open Notebook**.
2. Upload [`phase21_v17_gpu_training.ipynb`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_v17_colab/phase21_v17_gpu_training.ipynb).
3. Set Runtime Hardware Accelerator: **Runtime -> Change runtime type -> T4 GPU**.
4. Run **Cell 1** to mount Google Drive.
5. Run **Cell 2 & 3** to initialize environment and dataset path variables.
6. Run **Cell 4 (MANDATORY PRE-FLIGHT AUDIT CELL)**:
   - Verifies CUDA availability and GPU device name.
   - Computes SHA-256 hashes of train and validation datasets.
   - Verifies 40,000 train / 10,000 validation record counts.
   - Checks that FastAPI integration remains **BLOCKED**.
7. Run **Cell 5** to initiate clean V17 GPU training run.

---

## 3. Preserved Hyperparameters & GPU Settings

- **Base Model**: `google/flan-t5-small` (80M parameters)
- **Precision**: `fp16 = True` (NVIDIA CUDA mixed precision)
- **Batch Size**: `16` per device, `gradient_accumulation_steps = 2` (Effective Batch Size = `32`)
- **Epochs**: `3` Epochs (~3,750 optimization steps)
- **Learning Rate**: `1e-4` with Cosine Decay Scheduler & 5% Warmup
- **Weight Decay**: `0.01`, **Label Smoothing**: `0.05`, **Gradient Clipping**: `1.0`
- **Evaluation & Checkpoints**: Every 250 steps, `save_total_limit = 3`, Early Stopping `patience = 3`

---

## 4. Post-Training Checkpoint Output

Upon completion, the best model checkpoint will be saved to:
`MyDrive/AQPG/backend/ml/models/checkpoints/flan_t5_v17_gpu/best_model/`

Download or preserve these files for Phase 21A Step 6 Post-Training Quality Gate Evaluation.
