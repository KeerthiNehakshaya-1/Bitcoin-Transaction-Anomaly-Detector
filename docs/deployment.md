# Offline Linux Deployment

## 1. Overview

This document explains how to install, configure, run, and verify the **Bitcoin Transaction Anomaly Detector** on an offline Linux system.

The system is designed to process Bitcoin transaction and network metadata locally without requiring an internet connection during analysis.

The deployment includes:

- CSV, JSON, and XML data ingestion
- Data validation and cleaning
- Feature engineering
- IP, transaction, and wallet correlation
- Entity graph construction
- Geo-IP and ASN enrichment using a local database
- Machine learning anomaly detection
- Wallet clustering
- Risk scoring and explainable alerts
- Streamlit dashboard
- Offline test and validation utilities

---

# 2. System Requirements

## 2.1 Operating System

A Linux-based operating system is required.

Recommended:

- Ubuntu 22.04 or later
- Ubuntu 24.04
- Other modern Linux distributions with Python 3 support

## 2.2 Software Requirements

Install or provide the following:

- Python 3
- Git
- Python virtual environment support
- pip

Check the installed versions:

```bash
python3 --version
git --version
pip3 --version
```

Python 3.10 or newer is recommended.

---

# 3. Offline Deployment Package

For a completely offline deployment, transfer the complete project directory to the target Linux machine.

The deployment package should contain the project source code, configuration files, documentation, synthetic/raw input data required for demonstration, and any required local Geo-IP database.

Example project structure:

```text
bitcoin-monitor/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── geoip/
│
├── ingestion/
├── preprocessing/
├── features/
├── correlation/
├── graph/
├── geoip/
├── ml/
│
├── dashboard/
│   ├── app.py
│   └── pages/
│
├── tests/
│
├── models/
│
├── run_pipeline.py
├── config.py
├── requirements.txt
│
├── README.md
├── ARCHITECTURE.md
├── ML_METHODOLOGY.md
├── DATASET.md
└── DEPLOYMENT.md
```

---

# 4. Transfer the Project to Linux

If the Linux machine has access to the Git repository, clone the project:

```bash
git clone <repository-url>
cd bitcoin-monitor
```

For a completely isolated machine without internet access, copy the project directory using an approved offline transfer method.

Then enter the project directory:

```bash
cd bitcoin-monitor
```

Verify the files:

```bash
ls
```

---

# 5. Create a Python Virtual Environment

Create an isolated Python environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, the terminal should show something similar to:

```text
(.venv) user@linux:~/bitcoin-monitor$
```

Verify Python:

```bash
python --version
```

---

# 6. Install Python Dependencies

The project dependencies are listed in:

```text
requirements.txt
```

For a normal installation:

```bash
pip install -r requirements.txt
```

## Offline Installation

For a machine with no internet access, the required Python packages must be prepared beforehand.

On a machine with internet access, download the required packages into a local directory:

```bash
pip download -r requirements.txt -d offline_packages
```

Transfer the `offline_packages` directory to the offline Linux machine.

Then install without contacting the internet:

```bash
pip install --no-index --find-links=offline_packages -r requirements.txt
```

Verify the installation:

```bash
pip list
```

---

# 7. Prepare the Input Dataset

Place the input transaction dataset inside:

```text
data/raw/
```

The system supports:

```text
CSV
JSON
XML
```

Example:

```text
data/raw/bitcoin_transactions.csv
```

The pipeline is executed by specifying the input file:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

For JSON:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.json
```

For XML:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.xml
```

---

# 8. Geo-IP and ASN Database

The project can use a local Geo-IP database for IP enrichment.

Place the required database file in:

```text
data/geoip/
```

Example:

```text
data/geoip/dbip-country.mmdb
```

The database is accessed locally during processing.

Private or reserved IP addresses are not treated as public geographical locations. They are retained as:

```text
PRIVATE_OR_RESERVED
```

If the Geo-IP database is unavailable, the remaining transaction analysis can still be performed, but Geo-IP/ASN enrichment may be unavailable.

---

# 9. Run the Complete Processing Pipeline

Make sure the virtual environment is active:

```bash
source .venv/bin/activate
```

Run:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

The pipeline performs the major processing stages in sequence:

```text
1. Data ingestion
       ↓
2. Validation and cleaning
       ↓
3. Geo-IP / ASN enrichment
       ↓
4. Feature engineering
       ↓
5. IP-TXID-Wallet correlation
       ↓
6. Entity graph construction
       ↓
7. Anomaly detection
       ↓
8. Entity-level analysis
       ↓
9. Wallet clustering
       ↓
10. Risk scoring
       ↓
11. Model evaluation
```

A successful execution generates the required analysis outputs under the project's processing/output directories.

---

# 10. Run the Dashboard

After the pipeline completes successfully, start the Streamlit dashboard:

```bash
python -m streamlit run dashboard/app.py
```

The terminal will display the local dashboard address.

For example:

```text
Local URL: http://localhost:8501
```

Open the displayed address in a browser available on the Linux machine.

The dashboard provides access to the project's analysis modules, including:

- Overview
- Data Import
- Data Quality
- Correlation
- Entity Graph
- AI/ML Analysis

---

# 11. Dashboard Workflow

A typical investigation workflow is:

```text
Import / Load Dataset
        ↓
Run Processing Pipeline
        ↓
Check Data Quality
        ↓
Correlation Analysis
        ↓
Entity Graph Investigation
        ↓
AI/ML Analysis
        ↓
Risk and Alert Review
```

The Entity Graph can be used to investigate relationships between:

```text
IP Address
      ↕
Transaction
      ↕
Wallet Address
```

The graph supports investigation from a selected entity and exploration of connected entities.

---

# 12. AI/ML Analysis

The AI/ML module performs offline analysis of transaction and entity behavior.

The project includes:

- Isolation Forest anomaly detection
- Wallet/entity anomaly analysis
- DBSCAN wallet clustering
- Risk scoring
- Explainable risk factors
- Model evaluation

The synthetic scenario labels are used for evaluation and validation of the model. They should not be treated as input features for anomaly detection.

A high-risk score represents an investigation-prioritization signal. It does not by itself establish that an IP address, wallet, transaction, or entity is associated with criminal activity.

---

# 13. Verify the Deployment

Before final use, verify that the pipeline completes successfully:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

Then verify that the dashboard starts:

```bash
python -m streamlit run dashboard/app.py
```

Also verify the Python environment:

```bash
python --version
```

and installed dependencies:

```bash
pip list
```

---

# 14. Run Tests

Run the project's tests using:

```bash
pytest
```

If the project contains a final audit script, run:

```bash
python tests/final_audit.py
```

The test suite is intended to verify important parts of the processing pipeline, including:

- Data validation
- Data cleaning
- Feature generation
- Risk scoring
- Pipeline outputs

---

# 15. Troubleshooting

## 15.1 Python command not found

Try:

```bash
python3 --version
```

If Python is installed as `python3`, create the environment using:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## 15.2 pip command not found

Use:

```bash
python3 -m pip --version
```

Then install dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

---

## 15.3 Virtual environment is not active

Run:

```bash
source .venv/bin/activate
```

Then verify:

```bash
which python
```

The returned path should point to the project's `.venv` directory.

---

## 15.4 Input argument error

If the following error appears:

```text
error: the following arguments are required: --input
```

provide the input dataset explicitly:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

---

## 15.5 Input file not found

Check the raw data directory:

```bash
ls data/raw/
```

Then provide the correct filename:

```bash
python run_pipeline.py --input data/raw/<filename>
```

---

## 15.6 Geo-IP database unavailable

Check:

```bash
ls data/geoip/
```

Make sure the required local Geo-IP database is present.

If it is not available, Geo-IP/ASN enrichment may not be available for the deployment.

---

## 15.7 Streamlit does not start

Verify Streamlit is installed:

```bash
python -m streamlit --version
```

Then run:

```bash
python -m streamlit run dashboard/app.py
```

---

# 16. Offline Security Considerations

The deployment is designed to operate locally.

For an offline deployment:

- Do not expose the dashboard to an untrusted network.
- Keep sensitive datasets on the approved offline system.
- Do not upload operational or sensitive transaction data to external services.
- Use synthetic data for demonstrations and testing.
- Keep local Geo-IP databases and datasets under controlled access.
- Do not treat automated risk scores as definitive attribution.

---

# 17. Updating the Deployment

When a new project version is available, update the source code using the approved transfer mechanism.

For a Git-based deployment with network access:

```bash
git pull
```

Then activate the environment:

```bash
source .venv/bin/activate
```

Update dependencies when required:

```bash
pip install -r requirements.txt
```

Run the pipeline again:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

Then start the dashboard:

```bash
python -m streamlit run dashboard/app.py
```

---

# 18. Deployment Checklist

Before presenting or deploying the system, verify:

```text
[ ] Linux system available
[ ] Python 3 installed
[ ] Git available
[ ] Project copied/cloned
[ ] Virtual environment created
[ ] Virtual environment activated
[ ] requirements.txt installed
[ ] Input dataset available
[ ] Geo-IP database available, if required
[ ] Pipeline completes successfully
[ ] Output files generated
[ ] Tests pass
[ ] Streamlit dashboard starts
[ ] Entity Graph works
[ ] AI/ML Analysis works
[ ] Risk scores and explanations are displayed
```

---

# 19. Quick Start

For a prepared Linux system, the essential commands are:

```bash
git clone <repository-url>
cd bitcoin-monitor

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python run_pipeline.py --input data/raw/bitcoin_transactions.csv

python -m streamlit run dashboard/app.py
```

For a completely offline machine, install the dependencies from the previously prepared local package directory:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --no-index --find-links=offline_packages -r requirements.txt

python run_pipeline.py --input data/raw/bitcoin_transactions.csv

python -m streamlit run dashboard/app.py
```

The system is then ready for offline Bitcoin transaction anomaly analysis and investigation.