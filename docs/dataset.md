# Dataset Documentation

## AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

---

## 1. Dataset Overview

This project uses a **synthetic Bitcoin transaction and network-traffic dataset** for developing and testing the offline monitoring and analysis system.

The dataset is designed to represent the type of transaction, network, wallet, and entity information that may be available during Bitcoin transaction analysis.

The dataset contains both:

- Normal transaction behavior
- Intentionally generated anomalous behavior

The anomalous records are included so that the system can be evaluated for its ability to identify unusual transaction patterns.

> **Important:** The dataset is synthetic. It does not contain real seized Bitcoin transaction data, live intercepted network traffic, or real private user information.

---

## 2. Dataset Purpose

The dataset is used to test the complete analytics pipeline:

```text
Raw Dataset
     ↓
Data Ingestion
     ↓
Validation
     ↓
Data Cleaning
     ↓
Geo-IP / ASN Enrichment
     ↓
Feature Engineering
     ↓
Correlation Analysis
     ↓
Entity Graph Construction
     ↓
AI / ML Anomaly Detection
     ↓
Wallet / IP Analysis
     ↓
Clustering
     ↓
Risk Scoring
     ↓
Explainable Alerts
```

The dataset therefore supports both individual transaction analysis and relationship-based investigation.

---

## 3. Dataset Size

The synthetic dataset contains approximately **10,020 transaction records**.

| Category | Records |
|---|---:|
| Normal transactions | 9,200 |
| Anomalous transactions | 800 |
| Total | 10,000+ |
| Special burst scenario | 20 anomalous transactions included within the anomalous set |

The dataset contains a large majority of normal transactions and a smaller set of intentionally unusual transactions.

This distribution provides a realistic class imbalance for testing anomaly detection techniques.

---

## 4. Dataset Formats

The same transaction dataset is provided in multiple formats so that the ingestion module can demonstrate support for different input sources.

Supported formats:

```text
CSV
JSON
XML
```

Example files:

```text
data/
└── raw/
    ├── bitcoin_transactions.csv
    ├── bitcoin_transactions.json
    └── bitcoin_transactions.xml
```

The ingestion module automatically identifies and loads the supported format.

---

# 5. Dataset Fields

The main dataset contains transaction, network, wallet, and contextual information.

| Field | Description |
|---|---|
| `timestamp` | Date and time at which the transaction/network event occurred |
| `src_ip` | Source IP address associated with the observed transaction traffic |
| `dst_ip` | Destination IP address associated with the observed transaction traffic |
| `src_port` | Source network port |
| `dst_port` | Destination network port |
| `txid` | Unique transaction identifier |
| `input_addresses` | Input Bitcoin wallet addresses associated with the transaction |
| `output_addresses` | Output Bitcoin wallet addresses associated with the transaction |
| `input_amounts` | Amounts associated with the input addresses |
| `output_amounts` | Amounts associated with the output addresses |
| `fee` | Transaction fee |
| `script_type` | Bitcoin transaction script type |
| `geo_country` | Country information associated with the source IP |
| `asn` | Autonomous System Number associated with the source IP |
| `synthetic_scenario` | Synthetic label describing the generated behavior, used only for evaluation |

---

# 6. Transaction Information

### 6.1 Timestamp

The `timestamp` field records when the transaction/network event occurred.

It is used to calculate temporal behavior such as:

- Transaction frequency
- Time gaps between transactions
- Rapid transaction bursts
- Activity over time
- Unusual periods of activity

Example:

```text
2026-01-15 10:35:21
```

---

### 6.2 Transaction ID

The `txid` uniquely identifies a transaction in the synthetic dataset.

Example:

```text
TX00007691
```

The transaction ID is used to connect transaction records with:

- Source IP addresses
- Destination IP addresses
- Input wallets
- Output wallets

---

# 7. Network Information

## 7.1 Source IP

`src_ip` represents the source IP address associated with the observed transaction traffic.

Example:

```text
10.0.1.25
```

The system uses IP information to identify:

- IP activity
- Number of transactions from an IP
- Number of wallets associated with an IP
- Network relationships
- Geographic relationships
- ASN relationships

---

## 7.2 Destination IP

`dst_ip` represents the destination IP address associated with the transaction traffic.

It can be used to study communication relationships between network entities.

---

## 7.3 Network Ports

The following fields describe the network ports:

```text
src_port
dst_port
```

They provide additional network-level information that can be used during validation and behavioral analysis.

The system validates that port values are within valid network port ranges.

---

# 8. Wallet Information

The dataset contains wallet information through input and output address fields.

### Input Addresses

```text
input_addresses
```

represent wallet addresses associated with the transaction inputs.

### Output Addresses

```text
output_addresses
```

represent wallet addresses receiving transaction outputs.

The wallet information is used to build relationships such as:

```text
IP → Transaction → Wallet
```

and:

```text
Wallet → Transaction → Wallet
```

This information is important for entity-level investigation.

---

# 9. Transaction Amount Information

The dataset contains:

```text
input_amounts
output_amounts
fee
```

These values are used to derive behavioral features.

Examples include:

- Total input amount
- Total output amount
- Transaction amount
- Transaction fee
- Number of inputs
- Number of outputs

These features help the anomaly detection system identify unusual transaction behavior.

---

# 10. Script Type

The `script_type` field describes the transaction script category used by the synthetic transaction.

It provides additional transaction-level context and can be used during feature engineering and analysis.

---

# 11. Geo-IP and ASN Information

The dataset contains geographic and network information such as:

```text
geo_country
asn
```

The system can also perform additional **offline Geo-IP / ASN enrichment** using a local database.

The enrichment process can produce information such as:

```text
geo_country_lookup
asn_lookup
dst_geo_country_lookup
dst_asn_lookup
```

Additional derived signals include:

```text
cross_country_transaction
cross_asn_transaction
ip_unique_countries
ip_unique_asns
```

This allows the system to identify unusual geographic or network-level relationships.

---

# 12. Synthetic Anomaly Scenarios

The dataset contains intentionally generated anomalous behavior.

These scenarios are designed to represent unusual transaction activity rather than real-world criminal activity.

Examples of synthetic behavior include:

- Unusually high transaction activity
- Rapid transaction bursts
- High wallet activity
- Unusual IP-to-wallet relationships
- Unusual transaction frequency
- High fan-out behavior

One specific synthetic burst scenario uses:

```text
Source IP:
172.16.50.1

Wallet:
WALLET_A_0001
```

The scenario contains approximately **20 rapid transactions** involving multiple output wallets.

This creates a high fan-out pattern that can be detected through behavioral and graph-based analysis.

---

# 13. Synthetic Scenario Labels

The field:

```text
synthetic_scenario
```

identifies the intentionally generated scenario associated with a record.

For example, it can distinguish normal synthetic behavior from generated anomalous scenarios.

### Important ML Rule

`synthetic_scenario` is **not used as an input feature for anomaly detection**.

It is used only for:

```text
Model evaluation
Performance measurement
Validation of detected anomalies
```

This prevents the machine-learning model from simply learning the answer from the synthetic label.

The evaluation module can compare detected anomalies against the known synthetic scenarios to calculate metrics such as:

- Precision
- Recall
- F1-score

---

# 14. Data Quality and Validation

Before analysis, the dataset passes through validation and cleaning.

The validation process checks:

- Required columns
- Missing values
- Duplicate transaction IDs
- IP address validity
- Port validity
- Timestamp validity
- Numeric transaction values
- Transaction amounts
- Transaction fees

Invalid or incomplete records are handled during preprocessing.

---

# 15. Data Cleaning

The cleaning stage performs operations such as:

### Duplicate Removal

Duplicate transaction IDs are identified and removed where necessary.

### Missing Values

Missing numeric values are handled during preprocessing.

### Data Type Conversion

Fields such as:

```text
timestamp
fee
input_amounts
output_amounts
```

are converted into suitable data types.

### Address Parsing

Input and output wallet arrays are parsed so that individual wallet addresses can be analyzed.

### Text Normalization

Fields such as:

```text
IP addresses
transaction IDs
script types
country codes
ASN values
```

are normalized into consistent formats.

---

# 16. Feature Engineering

The cleaned dataset is converted into numerical and behavioral features for analysis.

Important feature groups include:

### Transaction Features

- Transaction amount
- Fee
- Number of inputs
- Number of outputs
- Input/output totals

### Wallet Features

- Transaction count
- Activity frequency
- Number of counterparties
- Input/output behavior
- Transaction volume

### IP Features

- Number of transactions
- Number of wallets
- Number of unique countries
- Number of unique ASNs
- Network activity

### Temporal Features

- Transaction frequency
- Time gaps
- Rapid activity
- Burst behavior

### Graph Features

- Node degree
- Centrality
- Entity connections
- Relationship counts

### Geo-IP / ASN Features

- Geographic relationships
- Cross-country activity
- Cross-ASN activity
- Unique countries per IP
- Unique ASNs per IP

---

# 17. Entity Relationships

The dataset allows the system to construct an entity relationship graph.

The main entities are:

```text
IP
Transaction
Wallet
```

The basic relationship is:

```text
        TRANSACTION
       /           \
      /             \
   IP                WALLET
```

A larger investigation may look like:

```text
IP
 │
 ├── TX001 ─── Wallet A
 │
 ├── TX002 ─── Wallet B
 │
 └── TX003 ─── Wallet C
```

This relationship structure is used by the graph analysis module.

---

# 18. Graph Construction

The graph module uses the transaction data to create a directed entity graph.

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

The resulting graph is stored in GraphML format and can be analyzed using graph-based features.

---

# 19. AI / ML Usage

The dataset supports several analytical components.

### Isolation Forest

Isolation Forest is used for transaction-level anomaly detection.

It analyzes behavioral features without using:

```text
synthetic_scenario
```

as an input feature.

The output contains an anomaly signal that is later used in risk scoring.

---

### Entity Analysis

Transaction anomaly information is aggregated to identify potentially unusual:

- Wallets
- IP addresses

This allows the system to move from individual transaction analysis to entity-level investigation.

---

### DBSCAN Clustering

DBSCAN is used to group wallets based on behavioral characteristics.

The clustering process helps identify:

- Similar wallet behavior
- Dense behavioral groups
- Unusual or isolated wallet behavior

A DBSCAN noise label of:

```text
-1
```

does **not automatically mean that a wallet is malicious**.

It only means that the wallet was not assigned to a dense cluster by DBSCAN.

---

# 20. Risk Scoring

The system combines multiple signals to generate risk scores.

Signals can include:

- Machine-learning anomaly signal
- Graph signal
- Activity signal
- Network signal
- Counterparty signal
- Centrality signal
- Cluster signal

The resulting score is used to prioritize entities and transactions for investigation.

A high risk score means:

> The entity exhibits more characteristics associated with the unusual patterns defined by this analytical system.

It does **not** prove criminal activity.

---

# 21. Explainability

The system produces explanations alongside risk scores.

The explanation can identify contributing signals such as:

```text
High transaction activity
Unusual network behavior
High graph connectivity
Unusual counterparty relationships
Anomaly detection signal
Cluster behavior
```

This allows an investigator to understand why an entity received a particular priority.

---

# 22. Offline Processing

The complete system is designed to operate offline.

The project does not require live Bitcoin network access for the provided demonstration dataset.

The processing flow is:

```text
Local Dataset
     ↓
Local Processing
     ↓
Local Geo-IP / ASN Database
     ↓
Local ML Analysis
     ↓
Local Graph Analysis
     ↓
Local Dashboard
```

This makes the prototype suitable for environments where external network access is unavailable or restricted.

---

# 23. Privacy and Data Safety

The dataset is synthetic and does not represent real individuals or real seized transaction records.

The example IP addresses and wallet identifiers are generated for testing.

Private or reserved IP addresses may appear in the synthetic dataset.

These addresses are treated as:

```text
PRIVATE_OR_RESERVED
```

during Geo-IP processing rather than being interpreted as public geographic locations.

---

# 24. Dataset Limitations

The dataset is intended for prototype development and evaluation.

It does not represent the full complexity of real Bitcoin transaction traffic.

Important limitations include:

1. The dataset is synthetic.

2. The anomalous scenarios are intentionally generated.

3. Real-world Bitcoin transaction behavior can be considerably more complex.

4. Synthetic IP-to-wallet relationships may not represent actual network behavior.

5. Geo-IP and ASN information may be limited by the available local database.

6. The dataset does not contain live network traffic.

7. The dataset does not contain real seized or intercepted investigative data.

8. Model performance on this dataset does not guarantee the same performance on real-world data.

---

# 25. Recommended Dataset Directory

The project uses the following structure:

```text
data/
│
├── raw/
│   ├── bitcoin_transactions.csv
│   ├── bitcoin_transactions.json
│   ├── bitcoin_transactions.xml
│   └── uploaded/
│
├── processed/
│
└── geoip/
```

### `raw/`

Contains original input datasets.

### `uploaded/`

Contains datasets imported through the dashboard.

### `processed/`

Contains cleaned, enriched, correlated, and other generated outputs.

### `geoip/`

Contains the local Geo-IP / ASN database used for offline enrichment.

---

# 26. Running the Dataset Through the Pipeline

The main CSV dataset can be processed using:

```bash
python run_pipeline.py --input data/raw/bitcoin_transactions.csv
```

The pipeline performs:

```text
1. Ingestion
2. Validation
3. Cleaning
4. Geo-IP / ASN enrichment
5. Feature engineering
6. Correlation analysis
7. Graph construction
8. Isolation Forest anomaly detection
9. Entity analysis
10. DBSCAN clustering
11. Risk scoring
12. Model evaluation
```

---

# 27. Expected Outputs

After successful processing, the system generates analytical outputs such as:

```text
Cleaned transaction data
Geo-IP enriched data
Feature-engineered data
IP-TXID-wallet correlations
IP relationship summaries
Wallet relationship summaries
Graph files
Graph entity features
Graph centrality information
Transaction anomaly results
Wallet anomaly scores
IP anomaly scores
Wallet clusters
Cluster statistics
Risk scores
Prioritized alerts
Model evaluation results
```

These outputs are consumed by the Streamlit dashboard.

---

# 28. Dataset Summary

| Property | Value |
|---|---|
| Dataset type | Synthetic |
| Primary domain | Bitcoin transaction and network analysis |
| Approximate records | 10,020 |
| Normal records | 9,200 |
| Anomalous records | 800 |
| Special burst records | 20 |
| Input formats | CSV, JSON, XML |
| Main entities | IP, Transaction, Wallet |
| Geo-IP processing | Offline |
| ASN processing | Offline |
| Anomaly detection | Isolation Forest |
| Clustering | DBSCAN |
| Graph analysis | NetworkX |
| Risk analysis | Multi-signal scoring |
| Evaluation labels | `synthetic_scenario` |
| Real seized data | No |
| Live intercepted data | No |

---

## 29. Conclusion

The dataset provides a controlled environment for developing and demonstrating an offline Bitcoin transaction monitoring and analysis system.

It combines:

```text
Transaction Data
      +
Network Data
      +
Wallet Data
      +
Temporal Data
      +
Geo-IP / ASN Data
      +
Entity Relationships
      +
Synthetic Anomalies
```

This allows the project to demonstrate the complete process from raw transaction ingestion to AI/ML anomaly detection, graph-based investigation, clustering, risk scoring, and explainable alert prioritization.

The dataset is intended to demonstrate the **technical capability of the prototype**, not to establish that any real-world person, wallet, IP address, or transaction is associated with criminal activity.