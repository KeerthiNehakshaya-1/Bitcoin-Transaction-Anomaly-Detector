# Model configuration
# ML_ANOMALY_WEIGHT = 30%
# GRAPH_WEIGHT = 18%
# ACTIVITY_WEIGHT = 18%
# NETWORK_WEIGHT = 10%
# COUNTERPARTIES_WEIGHT = 9%
# CENTRALITY_WEIGHT = 5%
# CLUSTER_WEIGHT = 10%

# 0–39   LOW
# 40–59  MEDIUM
# 60–79  HIGH
# 80–100 CRITICAL

# =========================================================
# ML CONFIGURATION
# =========================================================

ISOLATION_FOREST_ESTIMATORS = 200
ISOLATION_FOREST_CONTAMINATION = 0.08
RANDOM_STATE = 42

DBSCAN_EPS = 1.2
DBSCAN_MIN_SAMPLES = 5


# =========================================================
# RISK THRESHOLDS
# =========================================================

RISK_CRITICAL_THRESHOLD = 80
RISK_HIGH_THRESHOLD = 60
RISK_MEDIUM_THRESHOLD = 40


# =========================================================
# WALLET RISK WEIGHTS
# =========================================================

WALLET_ML_WEIGHT = 0.30
WALLET_GRAPH_WEIGHT = 0.18
WALLET_ACTIVITY_WEIGHT = 0.18
WALLET_NETWORK_WEIGHT = 0.10
WALLET_COUNTERPARTY_WEIGHT = 0.09
WALLET_CENTRALITY_WEIGHT = 0.05
WALLET_CLUSTER_WEIGHT = 0.10


# =========================================================
# TRANSACTION RISK WEIGHTS
# =========================================================

TRANSACTION_ML_WEIGHT = 0.55
TRANSACTION_AMOUNT_WEIGHT = 0.20
TRANSACTION_FEE_WEIGHT = 0.10
TRANSACTION_TEMPORAL_WEIGHT = 0.15


# =========================================================
# IP RISK WEIGHTS
# =========================================================

IP_ML_WEIGHT = 0.35
IP_GRAPH_WEIGHT = 0.20
IP_ACTIVITY_WEIGHT = 0.20
IP_WALLET_WEIGHT = 0.15
IP_DESTINATION_WEIGHT = 0.10