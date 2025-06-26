"""
Defines BigQuery table schemas for raw and transformed purchase stream data.

These schemas are used by the Apache Beam pipeline to write structured data into
BigQuery tables. The raw schema captures original fields from the streaming source,
while the transformed schema includes an additional `status` field.

Attributes:
    purchase_stream_raw_schema (dict): BigQuery schema for raw purchase data.
    purchase_stream_transformed_schema (dict): BigQuery schema for transformed purchase data.
"""

from typing import Dict, Any

# Schema for the raw incoming purchase stream data
purchase_stream_raw_schema: Dict[str, Any] = {
    "fields": [
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "quantity", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "unit_price", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "total_price", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"}
    ]
}

# Schema for the transformed purchase data (adds a 'status' field)
purchase_stream_transformed_schema: Dict[str, Any] = {
    "fields": [
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "quantity", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "unit_price", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "total_price", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "status", "type": "STRING", "mode": "REQUIRED"}
    ]
}
