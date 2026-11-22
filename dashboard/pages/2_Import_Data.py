import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import subprocess
import sys


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

UPLOAD_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "uploaded"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Import Data",
    page_icon="📥",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📥 Import Bitcoin Transaction Data")

st.write(
    """
    Upload Bitcoin transaction/network metadata in CSV, JSON,
    or XML format. Multiple files can be uploaded and analyzed
    together.
    """
)


# =========================================================
# SUPPORTED FORMATS
# =========================================================

st.info(
    "Supported formats: CSV, JSON, XML"
)


# =========================================================
# FILE UPLOADER
# =========================================================

uploaded_files = st.file_uploader(
    "Choose transaction data files",
    type=["csv", "json", "xml"],
    accept_multiple_files=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def load_uploaded_file(file_path):
    """
    Read an uploaded file according to its extension.
    """

    extension = file_path.suffix.lower()

    if extension == ".csv":

        return pd.read_csv(file_path)

    if extension == ".json":

        return pd.read_json(file_path)

    if extension == ".xml":

        return pd.read_xml(file_path)

    raise ValueError(
        f"Unsupported file format: {extension}"
    )


def save_uploaded_files(files):

    saved_paths = []

    for uploaded_file in files:

        destination = (
            UPLOAD_DIR
            / uploaded_file.name
        )

        with open(
            destination,
            "wb"
        ) as output:

            output.write(
                uploaded_file.getbuffer()
            )

        saved_paths.append(
            destination
        )

    return saved_paths


def build_combined_dataset(paths):

    dataframes = []

    file_information = []

    for path in paths:

        try:

            dataframe = load_uploaded_file(
                path
            )

            dataframes.append(
                dataframe
            )

            file_information.append({
                "file": path.name,
                "format": path.suffix.lower(),
                "records": len(dataframe),
                "columns": len(dataframe.columns),
                "status": "SUCCESS"
            })

        except Exception as error:

            file_information.append({
                "file": path.name,
                "format": path.suffix.lower(),
                "records": 0,
                "columns": 0,
                "status": f"ERROR: {error}"
            })

    if not dataframes:

        raise ValueError(
            "No files could be loaded."
        )

    combined = pd.concat(
        dataframes,
        ignore_index=True
    )

    return combined, file_information


# =========================================================
# PROCESS UPLOAD
# =========================================================

if uploaded_files:

    st.subheader("Selected Files")

    file_names = [
        file.name
        for file in uploaded_files
    ]

    st.write(
        file_names
    )

    # -----------------------------------------------------
    # Save files
    # -----------------------------------------------------

    if st.button(
        "📂 Load & Preview Data",
        type="primary"
    ):

        try:

            paths = save_uploaded_files(
                uploaded_files
            )

            combined_df, information = (
                build_combined_dataset(paths)
            )

            # Store information for other pages
            st.session_state[
                "uploaded_paths"
            ] = [
                str(path)
                for path in paths
            ]

            st.session_state[
                "uploaded_dataframe"
            ] = combined_df

            st.session_state[
                "upload_information"
            ] = information

            st.success(
                "Data loaded successfully."
            )

        except Exception as error:

            st.error(
                f"Unable to load data: {error}"
            )


# =========================================================
# DISPLAY DATA INFORMATION
# =========================================================

if "uploaded_dataframe" in st.session_state:

    df = st.session_state[
        "uploaded_dataframe"
    ]

    st.divider()

    st.subheader(
        "Dataset Summary"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Records",
        f"{len(df):,}"
    )

    c2.metric(
        "Columns",
        len(df.columns)
    )

    c3.metric(
        "Files",
        len(
            st.session_state[
                "uploaded_paths"
            ]
        )
    )

    # -----------------------------------------------------
    # File information
    # -----------------------------------------------------

    st.subheader(
        "Input File Status"
    )

    information_df = pd.DataFrame(
        st.session_state[
            "upload_information"
        ]
    )

    st.dataframe(
        information_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Column names
    # -----------------------------------------------------

    st.subheader(
        "Detected Columns"
    )

    st.write(
        list(df.columns)
    )

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    st.subheader(
        "Data Preview"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# RUN ANALYSIS
# =========================================================

if "uploaded_paths" in st.session_state:

    st.divider()

    st.subheader(
        "Run Analysis"
    )

    st.write(
        """
        The selected input will be passed to the offline
        analysis pipeline.
        """
    )

    if st.button(
        "▶ Run Complete Analysis",
        type="primary"
    ):

        # ---------------------------------------------
        # Use the first uploaded file as pipeline input
        #
        # For mixed CSV/JSON/XML uploads, the next stage
        # will use a combined standardized CSV.
        # ---------------------------------------------

        uploaded_df = st.session_state[
            "uploaded_dataframe"
        ]

        combined_input = (
            UPLOAD_DIR
            / "dashboard_combined_input.csv"
        )

        uploaded_df.to_csv(
            combined_input,
            index=False
        )

        st.info(
            "Starting complete offline analysis pipeline..."
        )

        python_executable = sys.executable

        if python_executable is None:
            python_executable = "python"

        pipeline_path = BASE_DIR / "run_pipeline.py"

        command = [
            str(python_executable),
            str(pipeline_path),
            "--input",
            str(combined_input)
        ]

        progress_box = st.empty()

        try:

            with st.spinner(
                "Running ingestion, preprocessing, "
                "ML, graph analysis and risk scoring..."
            ):

                result = subprocess.run(
                    command,
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True
                )

            if result.returncode == 0:

                st.success(
                    "✅ Complete analysis finished successfully."
                )

                st.session_state[
                    "analysis_completed"
                ] = True

                progress_box.code(
                    result.stdout
                )

            else:

                st.error(
                    "❌ Analysis pipeline failed."
                )

                progress_box.code(
                    result.stdout
                    + "\n"
                    + result.stderr
                )

        except Exception as error:

            st.error(
                f"Could not start pipeline: {error}"
            )


# =========================================================
# STATUS
# =========================================================

if st.session_state.get(
    "analysis_completed",
    False
):

    st.success(
        "Analysis results are ready. "
        "Use the other pages to investigate the results."
    )