# Seed Data Documentation (seed_data.json)

## Overview

The `seed_data.json` file contains initial data that is loaded into the SQLite database
when the MCP server starts for the first time. This separates configuration data from
code, following best practices for maintainability.

## Why Use a Seed File?

1. **Separation of Concerns** - Data is separate from code
2. **Easy to Modify** - Non-developers can edit customer/order data
3. **Version Control Friendly** - JSON diffs are easy to read
4. **Deployment Flexibility** - Different seed data for dev/staging/prod

## File Structure

```json
{
  "customers": [...],  // Array of customer records
  "orders": [...]      // Array of order records
}
```

## Customer Schema

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | **Primary Key** - Customer's email address |
| `name` | string | Customer's full name |
| `tier` | string | Service tier: "Standard" or "Premium" |
| `support_tickets` | integer | Count of support tickets (updated by system) |

### Example Customer
```json
{
  "email": "john.doe@email.com",
  "name": "John Doe",
  "tier": "Premium",
  "support_tickets": 2
}
```

## Order Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | **Primary Key** - Order ID (format: ORD-XXX) |
| `customer_email` | string | **Foreign Key** - Links to customer |
| `order_date` | string | ISO date format (YYYY-MM-DD) |
| `product` | string | Product name |
| `status` | string | "Processing", "Shipped", or "Delivered" |

### Example Order
```json
{
  "id": "ORD-001",
  "customer_email": "john.doe@email.com",
  "order_date": "2024-11-15",
  "product": "Wireless Headphones",
  "status": "Delivered"
}
```

## How It's Used

1. **MCP Server Startup** (`mcp_server.py`):
   - Checks if `customers.db` exists
   - If database is empty, reads `seed_data.json`
   - Inserts all customers and orders into SQLite tables

2. **Code Location** (in `mcp_server.py`):
   ```python
   def _seed_database(self, cursor):
       with open(SEED_DATA_PATH, 'r') as f:
           seed_data = json.load(f)
       # ... insert into database
   ```

## Adding New Customers/Orders

Simply edit `seed_data.json` and delete `customers.db` to re-seed:

```bash
rm customers.db
python gradio_app.py  # Database will be recreated with new seed data
```

## Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│     customers       │       │       orders        │
├─────────────────────┤       ├─────────────────────┤
│ email (PK)          │◄──────│ customer_email (FK) │
│ name                │       │ id (PK)             │
│ tier                │       │ order_date          │
│ support_tickets     │       │ product             │
└─────────────────────┘       │ status              │
                              └─────────────────────┘

┌─────────────────────┐
│      tickets        │
├─────────────────────┤
│ id (PK)             │
│ customer_email (FK) │───────► Created at runtime
│ issue_type          │         Not in seed data
│ description         │
│ priority            │
│ status              │
│ created_at          │
└─────────────────────┘
```

## Best Practices

1. **Keep emails lowercase** - The system normalizes emails to lowercase
2. **Use consistent date format** - YYYY-MM-DD for order dates
3. **Order IDs must be unique** - Use format ORD-XXX
4. **Customer email must exist** - Orders reference customers by email
