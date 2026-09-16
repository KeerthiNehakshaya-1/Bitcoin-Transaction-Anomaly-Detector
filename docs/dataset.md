# Dataset Documentation

## Dataset Type

Synthetic Bitcoin transaction/network metadata.

## Purpose

The dataset is used to develop and evaluate the offline
Bitcoin transaction monitoring prototype.

## Main Fields

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
- asn

## Derived Features

The system additionally creates behavioral features including:

- transaction amount
- input count
- output count
- wallet transaction frequency
- unique IP count
- unique counterparties
- graph degree
- graph centrality
- temporal transaction gaps
- Geo-IP/ASN features

## Synthetic Scenarios

The dataset contains controlled normal and anomalous patterns
for testing.

The scenario label is reserved for model evaluation and is
not provided to the unsupervised models during training.

## Privacy / Data Source

No real seized, intercepted or live Bitcoin transaction data
is used.