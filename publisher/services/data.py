import random
from datetime import datetime, timezone
from typing import Dict, Any
import uuid

def generate_purchase_event(customer: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a simulated purchase event using input customer and product data.

    This function creates a mock event dictionary containing:
    - UUID-based event ID
    - customer_id and product_id from the input
    - random quantity between 1 and 5
    - unit and total price
    - current UTC timestamp as ISO 8601 string (`created_at`)

    Args:
        customer (Dict[str, Any]): Dictionary containing customer details, must include 'customer_id'.
        product (Dict[str, Any]): Dictionary containing product details, must include 'product_id' and 'price'.

    Returns:
        Dict[str, Any]: A dictionary representing a single purchase event with structured fields.
    """

    # Simulasi nilai acak dari data existing
    customer_id = customer['customer_id']
    product_id = product['product_id']
    quantity = random.randint(1, 5)    
    unit_price = product['price']
    total_price = round(quantity * unit_price, 2)
    created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    return {
        "event_id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": total_price,
        "created_at": created_at
    }