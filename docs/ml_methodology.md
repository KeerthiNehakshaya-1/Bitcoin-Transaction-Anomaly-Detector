# Machine Learning Methodology

## 1. Feature Engineering

The system derives behavioral features from transaction,
network and graph data.

Examples:

- Transaction amount
- Fee
- Input count
- Output count
- Transaction frequency
- Wallet transaction count
- Wallet-to-IP diversity
- Wallet counterparties
- IP transaction count
- IP-to-wallet diversity
- Temporal transaction gaps
- Graph degree
- Graph centrality
- Geo-IP/ASN behavior

---

## 2. Isolation Forest

Isolation Forest is used for unsupervised anomaly detection.

Input:
Behavioral transaction features.

Output:

- ML prediction
- Decision score
- Normalized anomaly score

Prediction values:

- 1 = normal
- -1 = anomaly

The normalized anomaly score is mapped to a 0-100 range
for downstream prioritization.

---

## 3. DBSCAN

DBSCAN is used to identify behavioral clusters among wallets.

Input:

Wallet behavioral and graph features.

Output:

- Cluster ID
- Cluster type
- Noise entities

Cluster ID -1 represents DBSCAN noise.

Noise is not automatically interpreted as malicious activity.

---

## 4. Risk Scoring

Risk is derived by combining multiple signals:

- ML anomaly
- Graph structure
- Transaction activity
- Network behavior
- Counterparty behavior
- Centrality
- Behavioral clustering

The final score is normalized to a 0-100 prioritization scale.

---

## 5. Explainability

Every alert includes evidence explaining which signals
contributed to its priority.

Examples:

- High ML anomaly score
- High transaction activity
- Many connected IP addresses
- High graph connectivity
- High behavioral cluster signal

---

## 6. Evaluation

The synthetic dataset contains controlled scenarios for
offline evaluation.

The synthetic scenario label is NOT used as an ML feature.

It is used only to calculate:

- Precision
- Recall
- F1-score
- Confusion matrix
- Scenario detection rate