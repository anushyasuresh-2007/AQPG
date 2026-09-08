# AQPG PHASE 20 STEP 7 — BEGINNER'S GUIDE FOR GOOGLE COLAB GPU LAUNCH

Follow this simple, step-by-step guide to run **Phase 20 Step 7 (Controlled V16 FLAN-T5-Small Training)** on Google Colab GPU without writing or modifying any code.

---

## Direct Method to Open Notebook in Google Colab

### Method A: Upload File Directly (Recommended)
1. Open your browser and go to: **[colab.research.google.com](https://colab.research.google.com)**
2. In the popup window, click the **Upload** tab.
3. Click **Browse** and select [`docs/phase20_step7_colab_gpu.ipynb`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/docs/phase20_step7_colab_gpu.ipynb) from your local project folder.

### Method B: Via Google Drive
1. Upload your entire `AQPG` project folder to your main **Google Drive** folder so it sits at `MyDrive/AQPG`.
2. Double click [`docs/phase20_step7_colab_gpu.ipynb`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/docs/phase20_step7_colab_gpu.ipynb) inside Google Drive and select **Open with Google Colaboratory**.

---

## Step-by-Step Execution Guide

1. Open the notebook [`phase20_step7_colab_gpu.ipynb`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/docs/phase20_step7_colab_gpu.ipynb) in Google Colab.
2. Select GPU (`Runtime -> Change runtime type -> T4 GPU`).
3. Run **CELL 1** (Mount Google Drive).
4. Run **CELLS 2–9** sequentially in order.
5. Confirm **CELL 9** finds `checkpoint-1500` (`Global step: 1500`, `Epoch: 1`, `Resume: YES`).
6. Run **CELL 10** (Final pre-training summary).
7. Run **CELL 10A** (Checkpoint-1500 resume state validation).
8. Confirm **CELL 10A** prints: `CHECKPOINT-1500 RESUME STATE VALIDATION: PASS`.
9. Run **CELL 10B** (Actual `run_step7_training` source check).
10. Confirm **CELL 10B** prints: `RUN_STEP7_TRAINING SOURCE CHECK: PASS`.
11. Only then run **CELL 11** ONCE to resume training from step 1500.
12. **Do NOT use Run All.**
13. **Do NOT run Cell 11 twice.**
14. After Step 7 completes, **STOP**. No training or evaluation steps beyond Step 7 should be executed.

---

## IMPORTANT RULES (DO NOT DO)

> [!CAUTION]  
> * **DO NOT** run CELL 11 twice.
> * **DO NOT** run on CPU (CELL 3 will stop you automatically).
> * **DO NOT** close your browser tab during active training.
> * **DO NOT** start a local training script on your computer simultaneously.
> * **DO NOT** execute Steps 8–14 in Colab or locally until explicitly authorized.
