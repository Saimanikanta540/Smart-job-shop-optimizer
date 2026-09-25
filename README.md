# Smart Job Shop Optimizer

A smart optimizer for job shop scheduling.

## Overview

This repository contains the code for the Smart Job Shop Optimizer, a backend system utilizing FastAPI and Google's OR-Tools (CP-SAT solver) to schedule jobs on machines based on operations.

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

### Running the Scheduler independently
If you want to run the data loader or the CP-SAT scheduler directly:
```bash
# Ensure you are in the project root so it can find data/sample/
./backend/venv/Scripts/python backend/app/scheduler/cp_sat_scheduler.py
```
