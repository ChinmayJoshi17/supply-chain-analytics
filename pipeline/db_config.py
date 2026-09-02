from pathlib import Path
import os


def get_db_path() -> Path:
    """
    Resolves the DuckDB database path dynamically.
    Checks environment variable DUCKDB_PATH first, then common relative locations.
    """
    if "DUCKDB_PATH" in os.environ:
        return Path(os.environ["DUCKDB_PATH"]).resolve()

    repo_root = Path(__file__).resolve().parent.parent
    candidates = [
        repo_root / "data" / "supply_chain_analytics.duckdb",
        repo_root / "supply_chain_analytics.duckdb",
        repo_root.parent / "Project case study" / "supply_chain_analytics.duckdb",
        repo_root.parent.parent.parent / "Project case study" / "supply_chain_analytics.duckdb",
    ]

    for p in candidates:
        if p.exists():
            return p.resolve()

    # Default fallback inside repository root
    return (repo_root / "supply_chain_analytics.duckdb").resolve()


def get_export_dir() -> Path:
    """
    Resolves the output directory for Parquet gold table exports.
    """
    if "EXPORT_DIR" in os.environ:
        export_dir = Path(os.environ["EXPORT_DIR"]).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent
        export_dir = repo_root / "gold_exports"

    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir
