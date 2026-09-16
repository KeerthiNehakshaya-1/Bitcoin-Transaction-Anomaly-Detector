# System Architecture

## High-Level Architecture

The system consists of the following layers:

1. Data Ingestion
2. Validation and Cleaning
3. Geo-IP / ASN Enrichment
4. Feature Engineering
5. Network-Blockchain Correlation
6. Graph Analysis
7. AI/ML Analysis
8. Risk Scoring
9. Explainability
10. Dashboard

# System Architecture

                    ┌──────────────────────┐
                    │   CSV / JSON / XML   │
                    │   Transaction Data   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    DATA INGESTION    │
                    │       loader.py      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ VALIDATION & CLEANING│
                    │ validation.py        │
                    │ cleaner.py           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ GEO-IP / ASN LOOKUP  │
                    │   Local MMDB DB      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ FEATURE ENGINEERING  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ IP-TXID-WALLET       │
                    │ CORRELATION          │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐
      │  ENTITY GRAPH    │          │  ML FEATURE SET  │
      │    NetworkX      │          │                  │
      └────────┬─────────┘          └────────┬─────────┘
               │                             │
               └──────────────┬──────────────┘
                              ▼
                   ┌─────────────────────┐
                   │      AI / ML        │
                   │                     │
                   │ Isolation Forest    │
                   │ DBSCAN              │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │    RISK ENGINE      │
                   │                     │
                   │ Risk Score          │
                   │ Risk Level          │
                   │ Confidence Indicator│
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ EXPLAINABLE ALERTS  │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │     DASHBOARD       │
                   │      Streamlit      │
                   └─────────────────────┘