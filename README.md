# Smart Job Shop Optimizer

A smart optimizer for job shop scheduling.

## Overview

This repository contains the code for the Smart Job Shop Optimizer, a backend system utilizing FastAPI, Google's OR-Tools (CP-SAT solver) to schedule jobs on machines based on operations, and SimPy for discrete-event factory simulation.

## Backend Setup Instructions

### Prerequisites
- Python 3.8+ (recommended)

### Installation & Running

1. **Activate the virtual environment**:
   ```bash
   # If you're on a bash terminal (e.g. Git Bash)
   source backend/venv/Scripts/activate
   # If you're using PowerShell
   .\backend\venv\Scripts\activate
   ```

2. **Install the dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Run the FastAPI server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

### Running Modules Independently

Ensure you are in the project root directory (`d:\Smart-job-shop-optimizer`) before running these scripts. The scripts are now configured to resolve their own imports automatically.

**CP-SAT Scheduler**:
```bash
python backend/app/scheduler/cp_sat_scheduler.py
```

**Factory Simulation (SimPy)**:
```bash
python backend/app/simulation/factory_simulation.py
```

**Gantt Chart Visualization (Matplotlib)**:
```bash
python backend/app/simulation/gantt_visualization.py
```

**Result Analysis (CLI Text Output)**:
```bash
python backend/app/simulation/result_analysis.py
```

**Result Visualization (Charts)**:
```bash
python backend/app/simulation/result_visualization.py
```

**Bottleneck Analysis**:
```bash
python backend/app/simulation/bottleneck_analysis.py
```

**Scenario Analysis (What-If Scenarios)**:
```bash
python backend/app/simulation/scenario_analysis.py
```
