# AQPG Environment Setup Guide for New Developers

This guide provides step-by-step instructions for setting up the **Automated Question Paper Generation (AQPG)** environment on a fresh Windows 10/11 machine.

---

## Prerequisites
Ensure the following tools are installed on your Windows system before starting:
- **Git for Windows**: [git-scm.com](https://git-scm.com/)
- **Python 3.10.x or 3.13.x (64-bit)**: Add Python to PATH during installation.
- **Node.js (v18.0+ or v24.0+)**: [nodejs.org](https://nodejs.org/)
- **PowerShell / Terminal**: Built-in Windows Terminal or PowerShell 7+.
- *(Optional)* **MySQL Server 8.0+**: If using MySQL instead of SQLite.

---

## Step 1: Obtain Project Files
Copy or clone the repository to your chosen project folder (referred to as `<PROJECT_ROOT>`):

```powershell
# Open PowerShell and navigate to your workspace folder
cd C:\Users\<YourUsername>\Projects
git clone <repository_url> AQPG
cd AQPG
```

---

## Step 2: Set Up Python Virtual Environment

```powershell
# Navigate to backend directory
cd backend

# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip to latest
python -m pip install --upgrade pip
```

> [!TIP]
> If PowerShell blocks script execution, open PowerShell as Administrator and run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## Step 3: Install Backend Dependencies

With `.venv` active in `backend/`:

```powershell
# Install all required Python packages
pip install -r requirements.txt
```

If you have an NVIDIA GPU and CUDA installed, install PyTorch with CUDA support:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## Step 4: Install Frontend Dependencies

Open a new PowerShell terminal and run:

```powershell
cd frontend
npm install
```

---

## Step 5: Configure Environment Variables

1. **Backend Environment File**:
   Copy `.env.example` in `backend/` to `backend/.env`:
   ```powershell
   cd backend
   Copy-Item .env.example .env
   ```
   Edit `backend/.env` with Notepad or VS Code if you wish to adjust database settings or add a Gemini API key.

2. **Frontend Environment File**:
   Ensure `frontend/.env` exists and contains:
   ```ini
   VITE_API_BASE_URL=http://127.0.0.1:8011/api/v1
   ```

---

## Step 6: Verify Backend API Server

In your backend terminal (with `.venv` activated):

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8011
```

- Open your browser to `http://127.0.0.1:8011/health`
- Expected response: `{"status":"ok","environment":"development"}`
- Press `Ctrl+C` to stop the dev server.

---

## Step 7: Verify Frontend Development Server

In your frontend terminal:

```powershell
cd frontend
npm run dev
```

- Open `http://localhost:5173` in your browser.
- Verify the AQPG dashboard loads cleanly.

---

## Step 8: Verify Dataset and Model Files

From the `<PROJECT_ROOT>` directory:

```powershell
# Check V16 dataset files existence
Test-Path datasets/v16/qg_train_dataset_v16.jsonl
Test-Path datasets/v16/qg_validation_dataset_v16.jsonl

# Check pre-trained checkpoint directory
Test-Path backend/ml/models/checkpoints/flan_t5_v16_small
```

---

## Step 9: Continue Phase 20 Execution (Model Training / Evaluation)

### Scenario A: Training needs to be run on the new machine
If the physical model weights (`model.safetensors`) do **NOT** exist yet in `backend/ml/models/checkpoints/flan_t5_v16_small/`, start training:

```powershell
# Set PYTHONPATH to project root in PowerShell
$env:PYTHONPATH="."

# Launch V16 FLAN-T5-Small training (7,602 steps)
python backend/ml/training/train_flan_t5_v16.py
```

### Scenario B: Model weights were transferred from cloud/disk
If `model.safetensors` is physically present in `backend/ml/models/checkpoints/flan_t5_v16_small/`:

1. **Run Weight Verification (Step 8)**:
   ```powershell
   python -c "import torch; m = torch.load('backend/ml/models/checkpoints/flan_t5_v16_small/model.safetensors'); print('Checkpoint Loaded Successfully')"
   ```
2. **Run Post-Training Evaluation (Step 9)**:
   ```powershell
   $env:PYTHONPATH="."
   python backend/ml/evaluation/evaluate_flan_t5_v16.py
   ```

---

## Step 10: Run full Stack

To run both backend and frontend together:
1. Terminal 1: `cd backend; python -m uvicorn app.main:app --reload --port 8011`
2. Terminal 2: `cd frontend; npm run dev`
3. Access UI at `http://localhost:5173`
