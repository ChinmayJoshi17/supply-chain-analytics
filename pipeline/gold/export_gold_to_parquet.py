from pathlib import Path
import sys
import duckdb

# Ensure pipeline directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db_config import get_db_path, get_export_dir


def main() -> None:
    db_path = get_db_path()
    export_dir = get_export_dir()

    gold_tables = [
        "gold__dim_location__lite",
        "gold__dim_product__lite",
        "gold__fact_sales__lite",
        "gold__fact_inventory_movements__lite",
        "gold__fact_inventory_snapshots__lite",
        "gold__fact_inventory_exposure__lite",
    ]

    print(f"Connecting to DuckDB database at: {db_path}")
    con = duckdb.connect(str(db_path))

    for table in gold_tables:
        out_path = export_dir / f"{table}.parquet"
        try:
            con.execute(f"COPY {table} TO '{out_path}' (FORMAT PARQUET)")
            print(f"✅ Exported {table} -> {out_path.name}")
        except Exception as e:
            print(f"⚠️ Failed to export {table}: {e}")

    con.close()
    print(f"\n✨ All gold tables exported to: {export_dir}")


if __name__ == "__main__":
    main()
