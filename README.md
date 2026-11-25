# AI-Powered Bitcoin Transaction Anomaly Detector

An offline cybersecurity analytics platform for monitoring, analyzing, and investigating Bitcoin transaction traffic using **data processing, graph analysis, anomaly detection, clustering, and explainable risk scoring**.

The system ingests Bitcoin transaction and network metadata from **CSV, JSON, and XML** files and transforms it into an interactive investigation environment for identifying unusual transaction, wallet, and IP behavior.

> **Important:** This project works with a synthetic dataset designed for research and demonstration. A high-risk score indicates unusual behavior detected by the system and does **not** by itself prove criminal activity.

---

## 1. Project Overview

Bitcoin transaction networks can contain large volumes of interconnected activity involving:

- IP addresses
- Transaction IDs
- Wallet addresses
- Transaction amounts
- Fees
- Network endpoints
- Geographic information
- Autonomous System Numbers (ASN)

Manually examining these relationships can be difficult when the dataset becomes large.

This project provides an offline analytics pipeline that combines:

**Data Ingestion → Validation → Cleaning → Feature Engineering → Geo-IP Enrichment → Correlation → Graph Analysis → AI/ML Analysis → Risk Scoring → Interactive Dashboard**

The goal is to help investigators and analysts quickly identify unusual patterns and explore relationships between entities.

---

## 2. Key Features

### 📥 Multi-Format Data Ingestion

Supports:

- CSV
- JSON
- XML

The ingestion module converts supported input formats into a consistent internal representation.

---

### 🧹 Data Validation and Cleaning

The preprocessing stage performs checks such as:

- Required column validation
- Missing-value detection
- Duplicate transaction detection
- IP address validation
- Port validation
- Timestamp validation
- Numeric field validation
- Transaction amount processing
- Wallet address normalization
- Transaction ID normalization

---

### 🌍 Offline Geo-IP / ASN Enrichment

The system can enrich network information using a local Geo-IP database.

It extracts information such as:

- Country
- ASN
- Destination country
- Destination ASN

Private and reserved addresses are handled separately as:

```text
PRIVATE_OR_RESERVED
```

The system is designed to operate offline rather than depending on live external APIs.

---

### 🔗 Transaction Correlation

The system connects:

```text
IP Address
     ↓
Transaction ID
     ↓
Wallet Address
```

This allows analysts to investigate relationships between network activity and blockchain entities.

The correlation module produces summaries for:

- IP relationships
- Wallet relationships
- IP → Transaction → Wallet relationships

---

### 🕸️ Entity Graph Analysis

The project creates a graph containing three major entity types:

```text
        IP
        │
        │ OBSERVED
        ▼
   TRANSACTION
      /     \
     /       \
 INPUT       OUTPUT
   ↓           ↓
WALLET      WALLET
```

The graph supports investigation of:

- IP addresses
- Transaction IDs
- Wallet addresses
- Direct relationships
- Multi-level connections
- Entity centrality
- Connected components

The dashboard allows analysts to:

- Select an investigation entity
- Control connection depth
- Control displayed graph nodes
- Explore a selected node
- Focus on a node's links
- Return to the original investigation entity

---

## 3. AI/ML Analysis

The project uses multiple analytical techniques rather than relying on a single model.

### Isolation Forest

Isolation Forest is used for transaction-level anomaly detection.

It analyzes behavioral features without using the synthetic scenario label as an ML feature.

The model produces an anomaly signal that is later incorporated into the risk analysis.

---

### DBSCAN Clustering

DBSCAN is used to identify groups of wallets with similar behavioral characteristics.

The clustering process helps identify:

- Behavioral groups
- Dense wallet activity patterns
- Outlier wallets

A DBSCAN noise label of:

```text
-1
```

does **not** automatically mean that an entity is malicious.

It simply means that the entity was not assigned to a dense cluster.

---

### Entity-Level Analysis

Transaction anomaly signals are aggregated to investigate:

- Wallet behavior
- IP behavior
- Repeated activity
- Network relationships

This helps move from individual transaction analysis toward entity-level investigation.

---

### Risk Scoring

The system combines multiple signals into prioritized risk scores.

For wallet analysis, the scoring framework incorporates factors including:

- ML signal
- Graph signal
- Activity signal
- Network signal
- Counterparty signal
- Centrality signal
- Cluster signal

The resulting score is normalized to a 0–100 scale.

Example:

```text
0–39   LOW
40–59  MEDIUM
60–79  HIGH
80–100 CRITICAL
```

The exact thresholds are configurable according to the project configuration.

---

### Explainable Alerts

Instead of only displaying an anomaly score, the system generates explanations based on contributing signals.

For example:

```text
High activity
+
Strong graph connectivity
+
Unusual transaction behavior
=
Elevated risk score
```

This makes the results easier to interpret during an investigation.

---

## 4. Dashboard

The project includes an interactive Streamlit dashboard.

### Dashboard Sections

#### Overview

Provides a high-level view of the processed dataset and analytical results.

#### Import Data

Allows supported transaction datasets to be imported into the system.

Supported formats:

```text
CSV
JSON
XML
```

#### Data Quality

Displays information such as:

- Record count
- Missing values
- Duplicate records
- Invalid IP addresses
- Invalid ports
- Invalid timestamps
- Invalid numeric values

#### Correlation

Allows analysts to search and investigate:

- IP addresses
- Transaction IDs
- Wallet addresses

The search interface provides available entity suggestions from the dataset.

#### Entity Graph

Provides interactive relationship analysis between:

```text
IP
↕
TRANSACTION
↕
WALLET
```

#### AI/ML Analysis

Provides analytical views for:

- Transaction anomalies
- Wallet analysis
- IP analysis
- Wallet clustering
- Model evaluation

---

## 5. System Architecture

```text
                    ┌─────────────────────┐
                    │ CSV / JSON / XML    │
                    │ Transaction Data    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Ingestion      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Validation &        │
                    │ Cleaning            │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Feature Engineering │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌─────────────┐ ┌──────────────┐
        │ Geo-IP /   │ │ Correlation │ │ Graph        │
        │ ASN        │ │ Analysis    │ │ Construction │
        └─────┬──────┘ └──────┬──────┘ └──────┬───────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ AI / ML Analysis    │
                    │                     │
                    │ Isolation Forest    │
                    │ DBSCAN              │
                    │ Entity Analysis     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Risk Scoring &      │
                    │ Explainable Alerts  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └─────────────────────┘
```

---

## 6. Project Structure

```text
bitcoin-monitor/
│
├── data/
│   ├── raw/
│   │   ├── bitcoin_transactions.csv
│   │   ├── bitcoin_transactions.json
│   │   ├── bitcoin_transactions.xml
│   │   └── uploaded/
│   │
│   ├── processed/
│   └── geoip/
│
├── ingestion/
│   └── loader.py
│
├── preprocessing/
│   ├── validation.py
│   └── cleaner.py
│
├── features/
│   └── feature_engineering.py
│
├── correlation/
│   └── correlate.py
│
├── graph/
│   └── graph_builder.py
│
├── geoip/
│   └── enrichment.py
│
├── ml/
│   ├── anomaly_detection.py
│   ├── entity_detection.py
│   ├── clustering.py
│   ├── risk_scoring.py
│   ├── evaluate_model.py
│   └── model_tuning.py
│
├── dashboard/
│   ├── app.py
│   └── pages/
│       ├── 1_Overview.py
│       ├── 2_Import_Data.py
│       ├── 3_Data_Quality.py
│       ├── 4_Correlation.py
│       ├── 5_Entity_Graph.py
│       └── 6_AI_ML_Analysis.py
│
├── tests/
│   ├── test_validation.py
│   ├── test_cleaner.py
│   ├── test_features.py
│   ├── test_risk_scoring.py
│   ├── test_pipeline_outputs.py
│   └── final_audit.py
│
├── models/
│
├── run_pipeline.py
├── config.py
├── requirements.txt
├── .gitignore
│
├── README.md
├── ARCHITECTURE.md
├── ML_METHODOLOGY.md
├── DATASET.md
└── DEPLOYMENT.md
```

---

## 7. Requirements

The project requires:

- Python 3.x
- pip
- Git
- Streamlit
- pandas
- NumPy
- scikit-learn
- NetworkX
- matplotlib
- Plotly
- Geo-IP database support

All Python dependencies are listed in:

```text
requirements.txt
```

---

## 8. Installation

### Clone the repository

```bash
git clone https://github.com/KeerthiNehakshaya-1/Bitcoin-Transaction-Anomaly-Detector.git
```

Move into the project:

```bash
cd Bitcoin-Transaction-Anomaly-Detector
```

---

### Create a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 9. Running the Analytics Pipeline

The pipeline requires an input dataset.

For the included CSV dataset:

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

The pipeline processes the dataset through the complete analytics workflow.

---

## 10. Running the Dashboard

After processing the data, start Streamlit:

```bash
streamlit run dashboard/app.py
```

The dashboard can then be opened in a browser using the local Streamlit address displayed in the terminal.

---

## 11. Typical Workflow

```text
1. Select/import transaction dataset
              ↓
2. Validate input
              ↓
3. Clean and normalize data
              ↓
4. Enrich IP information
              ↓
5. Generate behavioral features
              ↓
6. Build IP/Transaction/Wallet correlations
              ↓
7. Build entity graph
              ↓
8. Run anomaly detection
              ↓
9. Perform wallet clustering
              ↓
10. Calculate entity risk scores
              ↓
11. Generate explanations and alerts
              ↓
12. Investigate entities through dashboard
```

---

## 12. Dataset

The project uses a **synthetic Bitcoin transaction dataset** for development, testing, and demonstration.

The dataset contains transaction and network-style metadata including fields such as:

```text
timestamp
src_ip
dst_ip
src_port
dst_port
txid
input_addresses
output_addresses
input_amounts
output_amounts
fee
script_type
geo_country
asn
```

The synthetic data contains both normal and anomalous scenarios to support model evaluation.

The synthetic scenario indicator is used for **evaluation only** and is not supplied to the anomaly detection model as an input feature.

More information is available in:

```text
DATASET.md
```

---

## 13. Model Evaluation

The project includes an evaluation module that compares detected anomalies against the synthetic evaluation labels.

The evaluation includes metrics such as:

- Precision
- Recall
- F1-score

These metrics are used to understand how effectively the anomaly detection configuration identifies the synthetic anomalous scenarios.

The evaluation labels are not used as direct model features.

---

## 14. Offline Design

The system is designed for offline analysis.

The core workflow does not require:

- Live blockchain APIs
- External transaction APIs
- Cloud ML services
- Online IP lookup services
- Continuous internet connectivity

Geo-IP enrichment can use a locally stored database.

This makes the project suitable for controlled environments where transaction data needs to remain within the analysis system.

---

## 15. Security and Privacy Considerations

This project is intended as an analytical and investigative support system.

It should not be interpreted as an automated system for determining criminal activity.

A high anomaly or risk score means that the observed behavior contains patterns considered unusual by the configured analytical methods.

Analysts should consider:

- Data quality
- Model limitations
- False positives
- False negatives
- Context surrounding the activity
- Additional investigative evidence

before making conclusions.

---

## 16. Limitations

Current limitations include:

- The dataset is synthetic.
- The model is not trained on real seized or live-intercept Bitcoin traffic.
- Risk confidence is a heuristic indicator rather than a calibrated probability.
- Anomaly detection can produce false positives and false negatives.
- Private/reserved IP addresses do not provide real-world geographic attribution.
- Offline Geo-IP results depend on the local database.
- The system does not prove malicious or criminal behavior.
- Real-time streaming analysis is outside the current offline workflow.

---

## 17. Future Enhancements

Potential future improvements include:

- Real-time transaction stream processing
- Live sensor/network ingestion
- Additional anomaly detection algorithms
- Graph neural network analysis
- Advanced wallet behavior profiling
- Temporal graph analysis
- Automated high-risk alerts
- More sophisticated model calibration
- Analyst feedback integration
- Larger and more diverse datasets
- Integration with mission or investigation monitoring systems
- Advanced link-analysis visualization

---

## 18. Testing

The project includes automated tests covering major processing components.

Tests include:

```text
Data validation
Data cleaning
Feature engineering
Risk scoring
Pipeline output verification
Final project audit
```

Run the test suite with:

```bash
pytest
```

---

## 19. Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Anomaly Detection | Isolation Forest |
| Clustering | DBSCAN |
| Graph Analysis | NetworkX |
| Visualization | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Data Formats | CSV, JSON, XML |
| Geo-IP | Local MMDB database |
| Version Control | Git / GitHub |

---

## 20. Project Objective

The primary objective is to build an offline analytical platform capable of transforming large volumes of Bitcoin transaction and network metadata into an understandable investigation workflow.

The system combines:

```text
Data Analytics
      +
Machine Learning
      +
Graph Analysis
      +
Risk Scoring
      +
Explainable Investigation
```

This provides analysts with a structured way to move from raw transaction data to entity-level investigation and prioritized anomaly analysis.

---

## 21. Author

**Keerthi Nehakshaya**

Project:

**AI-Powered Bitcoin Transaction Anomaly Detector**

Domain:

**Blockchain & Cybersecurity**

---

## 22. Disclaimer

This project is developed for educational, research, cybersecurity analytics, and demonstration purposes.

The generated anomaly and risk scores are analytical indicators only. They should not be treated as definitive evidence of criminal activity or malicious intent.