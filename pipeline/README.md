# 🔄 Supply Chain Data Pipeline

This directory contains the Python & SQL ETL pipeline implementing a **Medallion Architecture (Bronze → Silver → Gold)** powered by **DuckDB** and exported to **Apache Parquet** for Power BI reporting.

```
📁 pipeline/
├── 📁 bronze/                      # Raw ingestion & staging layer
│   ├── bronze__inventory_movements__lite.py
│   ├── bronze__inventory_snapshots__lite.py
│   ├── bronze__location_master__lite.py
│   ├── bronze__product_master__lite.py
│   └── bronze__sales_transactions__lite.py
├── 📁 silver/                      # Cleaned, standardized, & validated layer
│   ├── silver__inventory_movements__lite.py
│   ├── silver__inventory_snapshots__lite.py
│   ├── silver__location_master__lite.py
│   ├── silver__product_master__lite.py
│   └── silver__sales_transactions__lite.py
├── 📁 gold/                        # Business star schema & dimensional model
│   ├── gold__adv_fact_inventory_exposure.py
│   ├── gold__dim_location__lite.py
│   ├── gold__dim_product__lite.py
│   ├── gold__fact_inventory_movements__lite.py
│   ├── gold__fact_inventory_snapshots__lite.py
│   ├── gold__fact_sales__lite.py
│   └── export_gold_to_parquet.py
├── db_config.py                   # Dynamic DuckDB database and export directory helper
└── run_pipeline.py                # Unified pipeline execution orchestrator
```

---

## 🏛️ Medallion Architecture Overview

```
┌─────────────────────────┐
│     Raw Source Data     │  (Excel / CSV / ERP exports)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      BRONZE LAYER       │  Raw integration tables in DuckDB.
│   (Raw Ingestion)       │  Captures source schema with minimal transformations.
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      SILVER LAYER       │  Cleaned & standardized data.
│  (Data Quality & Norm)  │  • Type enforcement & date parsing (TRY_CAST, STRPTIME)
│                         │  • String trimming & case normalization (UPPER/TRIM)
│                         │  • Five-check Data Quality Framework
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       GOLD LAYER        │  Analytics-ready Star Schema & Aggregate Marts.
│ (Dimensional & Metrics) │  • Conformed Dimensions (Location, Product)
│                         │  • Fact Tables (Sales, Movements, Snapshots)
│                         │  • Advanced Feature Marts (Weekly Inventory Exposure)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   APACHE PARQUET EXPORT │  Compressed columnar files (.parquet) loaded into Power BI.
└─────────────────────────┘
```

---

## 🛠️ Layer Details

### 🥉 1. Bronze Layer (`pipeline/bronze/`)
- Ingests raw flat files (Excel / CSV) and populates staging tables in DuckDB.
- Preserves raw column names and initial values without business alterations.

| Script | Target Table | Description |
|---|---|---|
| `bronze__location_master__lite.py` | `bronze__location_master__lite` | Location master data (stores, fulfillment centers, warehouses) |
| `bronze__product_master__lite.py` | `bronze__product_master__lite` | Product catalog with SKU, brand, and unit cost |
| `bronze__sales_transactions__lite.py` | `bronze__sales_transactions__lite` | Raw POS and eCommerce sales line items |
| `bronze__inventory_movements__lite.py` | `bronze__inventory_movements__lite` | Stock transfer and movement logs |
| `bronze__inventory_snapshots__lite.py` | `bronze__inventory_snapshots__lite` | Periodic inventory on-hand snapshot logs |

---

### 🥈 2. Silver Layer (`pipeline/silver/`)
- Applies standardization, whitespace trimming, uppercase casting for keys, and resilient date/timestamp conversion.
- Eliminates null keys and prepares uniform datasets.

| Script | Target Table | Transformations & Quality Rules |
|---|---|---|
| `silver__location_master__lite.py` | `silver__location_master__lite` | Standardized `location_id`, trimmed strings, categorized location types |
| `silver__product_master__lite.py` | `silver__product_master__lite` | Normalized `sku`, cast `unit_cost` to DOUBLE, trimmed product names |
| `silver__sales_transactions__lite.py` | `silver__sales_transactions__lite` | Multi-format date parsing (`%d/%m/%Y %H:%M:%S`), numeric type casting |
| `silver__inventory_movements__lite.py` | `silver__inventory_movements__lite` | Date casting, standard movement types, origin/destination validation |
| `silver__inventory_snapshots__lite.py` | `silver__inventory_snapshots__lite` | Snapshot date formatting, positive quantity validation |

---

### 🥇 3. Gold Layer (`pipeline/gold/`)
- Builds the business dimensional model (Kimball Star Schema).
- Generates conformed dimension and fact tables, as well as multi-signal aggregation views.

| Script | Target Model | Model Type | Granularity & Description |
|---|---|---|---|
| `gold__dim_location__lite.py` | `gold__dim_location__lite` | Conformed Dimension | 1 row per Location (`LocationID`, `LocationName`, `LocationType`, `Region`) |
| `gold__dim_product__lite.py` | `gold__dim_product__lite` | Conformed Dimension | 1 row per Product SKU (`ProductSKU`, `ProductName`, `Category`, `Brand`, `UnitCost`) |
| `gold__fact_sales__lite.py` | `gold__fact_sales__lite` | Transaction Fact | 1 row per Sales Item (`SalesTransactionID`, `SalesDate`, `ProductSKU`, `LocationID`, `Quantity`, `UnitPrice`) |
| `gold__fact_inventory_movements__lite.py` | `gold__fact_inventory_movements__lite` | Transaction Fact | 1 row per Stock Movement (`MovementID`, `MovementDate`, `MovementType`, `ProductSKU`, `FromLocationID`, `ToLocationID`, `Quantity`) |
| `gold__fact_inventory_snapshots__lite.py` | `gold__fact_inventory_snapshots__lite` | Periodic Snapshot Fact | 1 row per (`SnapshotDate`, `LocationID`, `ProductSKU`) recording `OnHandQuantity` |
| `gold__adv_fact_inventory_exposure.py` | `gold__fact_inventory_exposure__lite` | Weekly Aggregate Mart | Combines weekly demand (`WeeklySalesQty`), stock (`WeekEndOnHandQty`), and flow (`NetMovementQty`) |
| `export_gold_to_parquet.py` | `gold_exports/*.parquet` | Parquet Exports | Columnar files exported directly for high-speed Power BI import |

---

## ⚡ Execution

You can run the entire pipeline with a single command using `run_pipeline.py`:

```bash
# Run complete end-to-end pipeline
python pipeline/run_pipeline.py
```

Or run individual layers or scripts as needed:

```bash
# Run Bronze layer
python pipeline/bronze/bronze__sales_transactions__lite.py

# Run Silver layer
python pipeline/silver/silver__sales_transactions__lite.py

# Run Gold layer & Export
python pipeline/gold/gold__adv_fact_inventory_exposure.py
python pipeline/gold/export_gold_to_parquet.py
```
