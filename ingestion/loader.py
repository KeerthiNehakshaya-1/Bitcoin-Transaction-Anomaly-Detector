try:
    import pandas as pd  # type: ignore
except ImportError:  # pragma: no cover - handled at runtime when pandas is unavailable
    pd = None

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from preprocessing.validation import validate_dataframe

# Find the project folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"


def _require_pandas():
    """Ensure pandas is installed before using data-loading helpers."""
    if pd is None:
        raise ModuleNotFoundError(
            "pandas is required to load datasets. Install it with: pip install pandas"
        )


def load_csv(file_path):
    """Load transaction data from CSV."""
    _require_pandas()
    return pd.read_csv(file_path)


def load_json(file_path):
    """Load transaction data from JSON."""
    _require_pandas()
    return pd.read_json(file_path)


def load_xml(file_path):
    """Load transaction data from XML."""
    _require_pandas()
    return pd.read_xml(file_path)


def load_dataset(file_path):
    """Load a dataset according to its file format."""

    extension = Path(file_path).suffix.lower()

    if extension == ".csv":
        return load_csv(file_path)

    elif extension == ".json":
        return load_json(file_path)

    elif extension == ".xml":
        return load_xml(file_path)

    else:
        raise ValueError(f"Unsupported file format: {extension}")


if __name__ == "__main__":

    files = [
        DATA_DIR / "bitcoin_transactions.csv",
        DATA_DIR / "bitcoin_transactions.json",
        DATA_DIR / "bitcoin_transactions.xml"
    ]

    for file in files:

        print("\n" + "=" * 60)
        print(f"Loading: {file.name}")
        print("=" * 60)

        try:
            df = load_dataset(file)
        
            print(f"Records loaded: {len(df)}")
            print(f"Columns: {len(df.columns)}")
            validate_dataframe(df)
            print("\nFirst 3 records:")
            print(df.head(3))

        except Exception as error:
            print(f"ERROR: {error}")