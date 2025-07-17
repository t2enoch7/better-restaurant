# You can run this file in two ways:
# 1. As a module (recommended):
#    python -m src.seed.seed_data
# 2. Directly as a script:
#    python src/seed/seed_data.py
# The sys.path logic below supports both.

import sys
import os
from decimal import Decimal

# Add both project root and src to sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

import load_env
load_env.load_env()

import uuid
from services.guest_service import GuestService
from services.table_service import TableService
from services.menu_service import MenuService

def seed():
    # Seed guests
    for i in range(5):
        GuestService.create_guest({
            "guest_id": str(uuid.uuid4()),
            "name": f"Guest {i}",
            "email": f"guest{i}@mail.com",
            "phone": f"555-000{i}"
        })
    # Seed tables
    for i in range(10):
        TableService.create_table({
            "table_id": str(uuid.uuid4()),
            "capacity": 2 + i % 4,
            "location": f"Section {chr(65 + i % 3)}"
        })
    # Seed menu
    for i in range(8):
        MenuService.create_menu({
            "menu_id": str(uuid.uuid4()),
            "name": f"Dish {i}",
            "description": f"Tasty dish {i}",
            "price": Decimal(str(10 + i * 2))
        })

if __name__ == "__main__":
    seed()
