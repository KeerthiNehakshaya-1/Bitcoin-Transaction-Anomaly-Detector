# AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

## 1. Problem
## 2. Objectives
## 3. Architecture
## 4. Dataset
## 5. Ingestion
## 6. Preprocessing
## 7. Geo-IP / ASN
## 8. Feature Engineering
## 9. Correlation
## 10. Graph Analysis
## 11. Isolation Forest
## 12. DBSCAN
## 13. Risk Scoring
## 14. Explainability
## 15. Dashboard
## 16. Evaluation
## 17. Installation
## 18. Running the Pipeline
## 19. Running the Dashboard
## 20. Offline Linux Deployment
## 21. Limitations
## 22. Future Scope


# AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

## Organization

National Technical Research Organisation (NTRO)

## Category

Software

## Theme

Blockchain & Cybersecurity

---

## 1. Problem Statement

Bitcoin's pseudonymous peer-to-peer architecture can be exploited
to move and layer illicit funds. This project provides an offline
AI-powered analytics platform for analyzing synthetic Bitcoin
transaction and network metadata.

The system correlates network-layer information such as IP addresses,
ports and timestamps with blockchain-layer information such as
transaction IDs, wallet addresses, amounts and fees.

Machine-learning techniques are then used to identify anomalous
behavior, cluster entities and prioritize investigative leads.

---

## 2. Objectives

- Ingest bulk CSV, JSON and XML metadata.
- Validate and clean incoming data.
- Correlate IP addresses, TXIDs and wallets.
- Build an entity/transaction graph.
- Perform AI/ML anomaly detection.
- Cluster wallet behavior.
- Generate explainable risk scores.
- Produce prioritized investigative alerts.
- Provide an offline investigation dashboard.
- Integrate offline Geo-IP and ASN enrichment.

---

## 3. System Architecture

See:

docs/architecture.md

---

## 4. Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- NetworkX
- Streamlit
- Plotly
- MaxMind DB / DB-IP Geo-IP data
- Pytest

---

## 5. Machine Learning

### Isolation Forest

Used for unsupervised anomaly detection.

### DBSCAN

Used for behavioral clustering of wallet entities.

---

## 6. Data Pipeline

CSV / JSON / XML
        ↓
Ingestion
        ↓
Validation
        ↓
Cleaning
        ↓
Geo-IP / ASN Enrichment
        ↓
Feature Engineering
        ↓
IP-TXID-Wallet Correlation
        ↓
Graph Construction
        ↓
ML Analysis
        ↓
Risk Scoring
        ↓
Explainable Alerts
        ↓
Dashboard

---

## 7. Running the Project

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate