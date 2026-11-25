# System Architecture

## 1. Architecture Overview

The **AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic** system follows a modular offline analytics architecture.

The architecture separates data ingestion, preprocessing, feature engineering, correlation, graph construction, machine learning, risk scoring and visualization.

The overall architecture is:

```text
                         ┌──────────────────────┐
                         │     Input Sources     │
                         │                      │
                         │ CSV / JSON / XML     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Ingestion       │
                         │    loader.py         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Validation & Cleaning│
                         │ validation.py        │
                         │ cleaner.py           │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Feature Engineering │
                         │ feature_engineering  │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │ GeoIP / ASN     │ │ Correlation     │ │ Entity Graph    │
        │ Enrichment      │ │ Analysis        │ │ Construction    │
        └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                 │                   │                   │
                 └───────────────────┼───────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │     ML Analysis      │
                          │                      │
                          │ Isolation Forest     │
                          │ Entity Detection     │
                          │ DBSCAN Clustering    │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │    Risk Scoring      │
                          │                      │
                          │ Transaction Risk     │
                          │ Wallet Risk          │
                          │ IP Risk              │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │   Model Evaluation   │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │ Streamlit Dashboard  │
                          │                      │
                          │ Overview             │
                          │ Data Quality         │
                          │ Correlation          │
                          │ Entity Graph         │
                          │ AI/ML Analysis       │
                          └──────────────────────┘
```

---

## 2. Architectural Layers

The system is organized into the following layers:

```text
┌──────────────────────────────────────────────┐
│              Presentation Layer              │
│          Streamlit Interactive UI            │
├──────────────────────────────────────────────┤
│             Investigation Layer              │
│   Correlation + Entity Graph + Risk Analysis │
├──────────────────────────────────────────────┤
│              Analytics Layer                 │
│ Isolation Forest + DBSCAN + Entity Analysis  │
├──────────────────────────────────────────────┤
│             Feature Layer                    │
│ Transaction + Wallet + IP + Temporal Features│
├──────────────────────────────────────────────┤
│           Enrichment Layer                   │
│             GeoIP / ASN                      │
├──────────────────────────────────────────────┤
│          Preprocessing Layer                 │
│       Validation + Cleaning                  │
├──────────────────────────────────────────────┤
│             Ingestion Layer                  │
│             CSV / JSON / XML                 │
├──────────────────────────────────────────────┤
│               Data Layer                     │
│       Raw + Processed Transaction Data       │
└──────────────────────────────────────────────┘
```

---

## 3. Data Layer

The data layer contains input and generated analytical data.

### Raw Data

```text
data/raw/
```

Contains supported source files:

```text
bitcoin_transactions.csv
bitcoin_transactions.json
bitcoin_transactions.xml
```

Uploaded files can also be placed under:

```text
data/raw/uploaded/
```

### Processed Data

```text
data/processed/
```

Contains outputs generated by different processing stages.

These files are intermediate analytical artifacts and can be regenerated from the raw input.

### GeoIP Data

```text
data/geoip/
```

Contains the local GeoIP/ASN database used for IP enrichment.

---

## 4. Ingestion Layer

File:

```text
ingestion/loader.py
```

The ingestion layer is responsible for reading supported input formats.

Supported formats:

```text
CSV
JSON
XML
```

The loader converts the input into a common tabular structure so that the downstream processing modules do not need separate logic for each file format.

### Flow

```text
CSV ──┐
JSON ─┼──→ Loader ──→ Common DataFrame
XML ──┘
```

---

## 5. Validation and Cleaning Layer

Files:

```text
preprocessing/validation.py
preprocessing/cleaner.py
```

### Validation

The validation module checks the integrity of incoming data.

Validation includes:

- Required columns
- Missing values
- Duplicate TXIDs
- IP address format
- Port ranges
- Timestamp format
- Numeric fields

### Cleaning

The cleaner:

- Removes empty records
- Handles duplicate transaction IDs
- Normalizes timestamps
- Normalizes IP addresses
- Normalizes transaction IDs
- Parses wallet and amount arrays
- Converts numeric fields
- Calculates transaction-level derived values

The cleaned dataset becomes the foundation for feature engineering.

---

## 6. GeoIP and ASN Enrichment Layer

File:

```text
geoip/enrichment.py
```

The enrichment module performs local lookup of IP information.

The resulting information can include:

```text
IP
Country
ASN
Destination Country
Destination ASN
```

Additional derived features include:

```text
cross_country_transaction
cross_asn_transaction
ip_unique_countries
ip_unique_asns
```

Private and reserved addresses are preserved as:

```text
PRIVATE_OR_RESERVED
```

This prevents private addresses from being incorrectly treated as publicly geolocated entities.

---

## 7. Feature Engineering Layer

File:

```text
features/feature_engineering.py
```

The feature layer converts cleaned transaction data into machine-learning and analytical features.

Feature categories include:

### Transaction Features

Examples include:

- Transaction amount
- Fee
- Input count
- Output count
- Transaction timing

### Wallet Features

Examples include:

- Transaction frequency
- Amount behavior
- Counterparty activity
- Wallet activity patterns

### IP Features

Examples include:

- Transaction count
- Unique wallets
- Unique transactions
- Geographic diversity
- ASN diversity

### Temporal Features

Examples include:

- Transaction intervals
- Activity bursts
- Time-based behavior

The synthetic scenario label is not used as an ML input feature.

---

## 8. Correlation Layer

File:

```text
correlation/correlate.py
```

The correlation layer identifies relationships between:

```text
IP
Transaction
Wallet
```

The primary relationship is:

```text
IP
 │
 ▼
Transaction
 │
 ▼
Wallet
```

The module generates relationship summaries for:

- IP entities
- Wallet entities
- Transaction relationships

These outputs are later used by the graph and risk-scoring components.

---

## 9. Graph Layer

File:

```text
graph/graph_builder.py
```

The graph layer represents transaction relationships using a NetworkX graph.

### Node Types

```text
IP
TRANSACTION
WALLET
```

### Edge Types

```text
OBSERVED
DESTINATION
INPUT
OUTPUT
```

Conceptually:

```text
              ┌───────────────┐
              │      IP       │
              └───────┬───────┘
                      │
                   OBSERVED
                      │
                      ▼
              ┌───────────────┐
              │  TRANSACTION  │
              └───────┬───────┘
                      │
                INPUT / OUTPUT
                      │
                      ▼
              ┌───────────────┐
              │    WALLET     │
              └───────────────┘
```

The graph module also calculates graph-level features such as centrality.

Graph data can be exported in GraphML format for additional analysis.

---

## 10. Machine Learning Layer

The machine-learning layer contains multiple analytical components.

```text
ml/
├── anomaly_detection.py
├── entity_detection.py
├── clustering.py
├── risk_scoring.py
├── evaluate_model.py
└── model_tuning.py
```

---

## 11. Transaction Anomaly Detection

File:

```text
ml/anomaly_detection.py
```

The system uses **Isolation Forest** for transaction-level anomaly detection.

Isolation Forest is suitable for identifying observations that differ from the majority of the dataset without requiring a fully supervised training dataset.

The model receives behavioral features generated by the feature-engineering stage.

The synthetic ground-truth scenario is excluded from the model's feature inputs.

Output:

```text
ml_anomaly_results.csv
```

---

## 12. Entity Detection

File:

```text
ml/entity_detection.py
```

The entity detection stage aggregates transaction-level anomaly information into entity-level information.

It can generate anomaly scores for:

```text
Wallets
IPs
```

These scores are later used by the risk-scoring layer.

---

## 13. Wallet Clustering

File:

```text
ml/clustering.py
```

The system uses **DBSCAN** to group wallets according to behavioral similarity.

DBSCAN identifies:

- Dense behavioral groups
- Isolated observations
- Noise points

A cluster value of:

```text
-1
```

represents DBSCAN noise.

It does not automatically represent malicious activity.

Outputs include:

```text
wallet_clusters.csv
cluster_statistics.csv
```

---

## 14. Risk Scoring Layer

File:

```text
ml/risk_scoring.py
```

Risk scoring combines multiple signals.

For wallet entities, the current weighting model is:

```text
ML Signal          30%
Graph Signal       18%
Activity Signal    18%
Network Signal     10%
Counterparty       9%
Centrality          5%
Cluster Signal     10%
```

Therefore:

```text
Wallet Risk
    =
    ML Signal
    + Graph Signal
    + Activity Signal
    + Network Signal
    + Counterparty Signal
    + Centrality Signal
    + Cluster Signal
```

The resulting score is normalized to a 0-100 scale.

The system also generates explanations describing which signals contributed to the risk score.

The confidence indicator is heuristic and should not be interpreted as a calibrated probability.

---

## 15. Model Evaluation

File:

```text
ml/evaluate_model.py
```

The evaluation module uses the synthetic scenario labels to measure model performance.

Metrics include:

```text
Precision
Recall
F1-score
```

The important architectural principle is:

```text
Synthetic Ground Truth
        │
        │
        └──────→ Evaluation
```

rather than:

```text
Synthetic Ground Truth
        │
        └──────→ ML Features
```

This prevents the known synthetic label from being directly used to predict itself.

---

## 16. Model Tuning

File:

```text
ml/model_tuning.py
```

The tuning module evaluates different Isolation Forest contamination settings.

Example values include:

```text
0.03
0.05
0.08
0.10
0.12
```

The objective is to understand how the anomaly threshold affects detection performance.

---

## 17. Dashboard Architecture

The dashboard is implemented using Streamlit.

Main entry point:

```text
dashboard/app.py
```

Pages:

```text
dashboard/pages/
├── 1_Overview.py
├── 2_Import_Data.py
├── 3_Data_Quality.py
├── 4_Correlation.py
├── 5_Entity_Graph.py
└── 6_AI_ML_Analysis.py
```

### Overview

Provides a high-level view of the processed dataset and analytical results.

### Import Data

Allows supported transaction files to be uploaded and processed through the pipeline.

### Data Quality

Displays:

- Record counts
- Missing values
- Duplicate records
- Invalid fields
- Validation results

### Correlation

Allows investigators to search and inspect:

```text
IP addresses
Transaction IDs
Wallet addresses
```

and examine their relationships.

### Entity Graph

Provides interactive relationship analysis.

An investigation begins by selecting a root entity.

The investigator can then control:

```text
Connection Depth
Maximum Graph Nodes
```

Two investigation actions are available when selecting a node:

```text
Explore This Node
```

This changes the current investigation center.

```text
Focus on This Node's Links
```

This keeps the original investigation context while examining the selected node's direct relationships.

### AI/ML Analysis

Provides views for:

- Transaction anomalies
- Wallet analysis
- IP analysis
- Wallet clustering
- Model evaluation

---

## 18. Investigation State Model

The Entity Graph maintains two important concepts:

### Investigation Root

The original entity selected by the investigator.

```text
root_entity
root_type
```

### Current Center

The entity currently being explored.

```text
current_entity
current_type
```

This allows the system to distinguish between:

```text
Original Investigation
```

and:

```text
Current Exploration
```

Example:

```text
Root:
WALLET_A_0001

        │
        ├── Transaction 1
        ├── Transaction 2
        └── IP 172.16.50.1

Current Center:
Transaction 2
```

The investigator can return to the original investigation context without losing the root entity.

---

## 19. End-to-End Data Flow

The complete data flow is:

```text
                     RAW DATA
                        │
              CSV / JSON / XML
                        │
                        ▼
                  INGESTION
                        │
                        ▼
              VALIDATION + CLEANING
                        │
                        ▼
               FEATURE ENGINEERING
                        │
             ┌──────────┼──────────┐
             │          │          │
             ▼          ▼          ▼
          GEOIP      CORRELATION  GRAPH
             │          │          │
             └──────────┼──────────┘
                        │
                        ▼
                 MACHINE LEARNING
                 ┌──────┴──────┐
                 │             │
                 ▼             ▼
           ISOLATION FOREST   DBSCAN
                 │             │
                 └──────┬──────┘
                        │
                        ▼
                  ENTITY ANALYSIS
                        │
                        ▼
                   RISK SCORING
                        │
                        ▼
                  MODEL EVALUATION
                        │
                        ▼
                STREAMLIT DASHBOARD
                        │
                        ▼
                  INVESTIGATION
```

---

## 20. Pipeline Execution Order

The main pipeline is controlled by:

```text
run_pipeline.py
```

The execution sequence is:

```text
1. Ingestion
       ↓
2. Validation / Cleaning
       ↓
3. GeoIP / ASN Enrichment
       ↓
4. Feature Engineering
       ↓
5. Correlation
       ↓
6. Graph Construction
       ↓
7. Isolation Forest
       ↓
8. Entity Detection
       ↓
9. DBSCAN Clustering
       ↓
10. Risk Scoring
       ↓
11. Model Evaluation
       ↓
12. Output Validation
```

The pipeline accepts an input file using:

```powershell
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

---

## 21. Output Architecture

The processing stages generate intermediate and final analytical outputs.

Conceptually:

```text
Raw Input
   │
   ├── Cleaned Transactions
   │
   ├── Enriched Transactions
   │
   ├── Engineered Features
   │
   ├── Correlation Results
   │
   ├── Graph Features
   │
   ├── Anomaly Results
   │
   ├── Entity Scores
   │
   ├── Wallet Clusters
   │
   ├── Risk Scores
   │
   └── Evaluation Results
```

These outputs are consumed by the dashboard.

---

## 22. Security and Privacy Design

The prototype is designed for controlled offline analysis.

Important principles include:

- No requirement for live blockchain APIs.
- Local processing of transaction metadata.
- Local GeoIP enrichment.
- Synthetic data for development and evaluation.
- No assumption that an anomaly represents criminal behavior.
- Risk scores are used for prioritization.
- Private/reserved IP addresses are explicitly identified.
- Generated processing files can be excluded from source control.

---

## 23. Scalability Considerations

The current architecture is modular so that individual components can be replaced or extended.

Potential scaling paths include:

```text
Pandas
   ↓
Distributed Data Processing
   ↓
Large-Scale Graph Processing
   ↓
Streaming Analytics
```

Possible future components include:

- Apache Spark
- Kafka
- Distributed graph databases
- Real-time stream processing
- Advanced graph analytics
- GPU-based machine learning

These technologies are not required by the current prototype.

---

## 24. Future Architecture

A future real-time version could follow:

```text
Bitcoin Network / Data Feed
             │
             ▼
       Stream Ingestion
             │
             ▼
       Real-Time Processing
             │
      ┌──────┼───────┐
      ▼      ▼       ▼
    GeoIP   Graph     ML
      │      │       │
      └──────┼───────┘
             ▼
       Risk Engine
             │
             ▼
       Alert Manager
             │
             ▼
     Investigator Dashboard
```

This would extend the current offline prototype into a continuous monitoring architecture.

---

## 25. Architectural Summary

The system follows a modular pipeline architecture:

```text
INPUT
  ↓
INGEST
  ↓
VALIDATE
  ↓
CLEAN
  ↓
ENRICH
  ↓
FEATURE ENGINEERING
  ↓
CORRELATE
  ↓
BUILD GRAPH
  ↓
ANOMALY DETECTION
  ↓
CLUSTERING
  ↓
RISK SCORING
  ↓
EVALUATION
  ↓
DASHBOARD
```

The architecture separates **data processing**, **machine learning**, **relationship analysis**, and **presentation**, making the system easier to test, maintain and extend.

The final platform combines transaction-level anomaly detection with entity-level relationship analysis so that investigators can move from an individual transaction or entity to its surrounding network context.