#!/usr/bin/env python3
"""
Supply Chain Analytics - End-to-End Pipeline Orchestrator
Executes the Medallion Architecture data transformations:
Bronze (Raw Integration) -> Silver (Cleaned & Validated) -> Gold (Dimensional Star Schema) -> Parquet Export
"""

import sys
import time
from pathlib import Path
import subprocess

SCRIPT_DIR = Path(__file__).resolve().parent

BRONZE_SCRIPTS = [
    "bronze/bronze__location_master__lite.py",
    "bronze/bronze__product_master__lite.py",
    "bronze/bronze__sales_transactions__lite.py",
    "bronze/bronze__inventory_movements__lite.py",
    "bronze/bronze__inventory_snapshots__lite.py",
]

SILVER_SCRIPTS = [
    "silver/silver__location_master__lite.py",
    "silver/silver__product_master__lite.py",
    "silver/silver__sales_transactions__lite.py",
    "silver/silver__inventory_movements__lite.py",
    "silver/silver__inventory_snapshots__lite.py",
]

GOLD_SCRIPTS = [
    "gold/gold__dim_location__lite.py",
    "gold/gold__dim_product__lite.py",
    "gold/gold__fact_sales__lite.py",
    "gold/gold__fact_inventory_movements__lite.py",
    "gold/gold__fact_inventory_snapshots__lite.py",
    "gold/gold__adv_fact_inventory_exposure.py",
    "gold/export_gold_to_parquet.py",
]


def run_script(rel_path: str) -> bool:
    full_path = SCRIPT_DIR / rel_path
    if not full_path.exists():
        print(f"  ❌ Script not found: {rel_path}")
        return False

    print(f"  ▶ Running {rel_path}...")
    start = time.time()
    result = subprocess.run([sys.executable, str(full_path)], capture_output=True, text=True)
    duration = time.time() - start

    if result.returncode == 0:
        print(f"  ✅ Completed {rel_path} ({duration:.2f}s)")
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                print(f"     {line}")
        return True
    else:
        print(f"  ❌ Error in {rel_path} (Exit {result.returncode}):")
        if result.stderr.strip():
            for line in result.stderr.strip().splitlines():
                print(f"     {line}")
        return False


def run_layer(name: str, scripts: list[str]) -> bool:
    print(f"\n==========================================")
    print(f" 🚀 Executing {name} Layer")
    print(f"==========================================")
    all_ok = True
    for s in scripts:
        ok = run_script(s)
        if not ok:
            all_ok = False
    return all_ok


def main() -> None:
    print("=" * 60)
    print("  📦 SUPPLY CHAIN ANALYTICS - DATA PIPELINE RUNNER")
    print("=" * 60)
    total_start = time.time()

    layers = [
        ("BRONZE (Raw Data Ingestion)", BRONZE_SCRIPTS),
        ("SILVER (Data Cleaning & Quality)", SILVER_SCRIPTS),
        ("GOLD (Star Schema & Parquet Export)", GOLD_SCRIPTS),
    ]

    for layer_name, script_list in layers:
        run_layer(layer_name, script_list)

    total_time = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"  ✨ Pipeline execution completed in {total_time:.2f} seconds.")
    print("=" * 60)


if __name__ == "__main__":
    main()
