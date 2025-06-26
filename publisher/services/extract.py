# services/extract.py

import os
from sqlalchemy import create_engine, text
from typing import Dict, Optional

def extract_data(table_name: str) -> Optional[Dict]:
    """
    Extracts a random record from a specified table (customer or products).
    
    Returns:
        dict with keys depending on the table, or None if table_name is invalid.
    """
    if table_name not in ["customer", "products"]:
        print("Invalid table name.")
        return None

    # Query to select a random row (PostgreSQL style)
    query = f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 1;"
    # print(f"query: {query}")

    # Build connection string manually
    connection_str = (
        f"postgresql://{os.getenv('RETAIL_POSTGRES_USER')}:{os.getenv('RETAIL_POSTGRES_PASSWORD')}"
        f"@{os.getenv('RETAIL_POSTGRES_HOST')}:{os.getenv('RETAIL_POSTGRES_PORT')}/{os.getenv('RETAIL_POSTGRES_DB')}"
    )

    # print(f"PostgreSQL connection string: {connection_str}")

    # Create engine
    engine = create_engine(connection_str)

    with engine.connect() as conn:
        result = conn.execute(text(query)).mappings().fetchone()
        if not result:
            return None

        if table_name == "customer":
            return {"customer_id": result["customer_id"]}
        elif table_name == "products":
            return {
                "product_id": result["product_id"],
                "price": float(result["price"])
            }

    

