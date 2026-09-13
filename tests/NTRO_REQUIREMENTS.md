# NTRO Problem Statement Requirements Audit

## Organization

National Technical Research Organisation (NTRO)

## Category

Software

## Theme

Blockchain & Cybersecurity

---

## Requirement 1: Bulk Metadata Ingestion

Status: COMPLETE

Supported formats:
- CSV
- JSON
- XML

Implementation:
- ingestion/loader.py

---

## Requirement 2: Required Bitcoin Metadata

Status: COMPLETE

Supported fields include:
- timestamp
- src_ip
- dst_ip
- src_port
- dst_port
- txid
- input_addresses
- output_addresses
- input_amounts
- output_amounts
- fee
- script_type
- geo_country
- ASN

---

## Requirement 3: Network / Blockchain Correlation

Status: COMPLETE

Correlation:
IP ↔ TXID ↔ Wallet

Implementation:
correlation/correlate.py

Output:
ip_txid_wallet_correlation.csv

---

## Requirement 4: Entity / Transaction Graph

Status: COMPLETE

Nodes:
- IP
- Transaction
- Wallet

Relationships:
- OBSERVED
- DESTINATION
- INPUT
- OUTPUT

Implementation:
graph/graph_builder.py

---

## Requirement 5: AI/ML Anomaly Detection

Status: COMPLETE

Model:
Isolation Forest

Implementation:
ml/anomaly_detection.py

---

## Requirement 6: Entity Clustering

Status: COMPLETE

Model:
DBSCAN

Implementation:
ml/clustering.py

---

## Requirement 7: Explainable Alerts

Status: COMPLETE

Alert evidence includes:
- ML anomaly
- transaction activity
- network relationships
- graph connectivity
- behavioral clustering

Implementation:
ml/risk_scoring.py

---

## Requirement 8: Confidence Score

Status: COMPLETE

Each prioritized alert includes a confidence indicator.

Output:
prioritized_alerts.csv

---

## Requirement 9: Prioritized Alerts

Status: COMPLETE

Risk levels:
- LOW
- MEDIUM
- HIGH
- CRITICAL

Output:
prioritized_alerts.csv

---

## Requirement 10: Geo-IP / ASN

Status: COMPLETE

Local offline Geo-IP / ASN lookup implemented.

Implementation:
geoip/enrichment.py

---

## Requirement 11: Dashboard

Status: COMPLETE

Dashboard provides:
- system overview
- risk distribution
- prioritized alerts
- entity investigation
- related transactions
- link analysis
- clustering information
- model metrics

Implementation:
dashboard/app.py

---

## Requirement 12: Offline Linux Operation

Status: COMPLETE / VERIFIED DURING DEPLOYMENT TESTING

The system is designed to operate locally without live transaction APIs.

---

## Requirement 13: Working Prototype

Status: COMPLETE

Master execution script:
run_pipeline.py

---

## Requirement 14: Technical Documentation

Status: IN PROGRESS

Required documents:
- system architecture
- data flow
- ML methodology
- dataset description
- installation instructions
- limitations
- future scope