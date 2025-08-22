#!/usr/bin/env python3

print("Testing imports...")

try:
    from models import Base
    print("✓ Base imported successfully")
except Exception as e:
    print(f"✗ Failed to import Base: {e}")

try:
    from services.database import init_db
    print("✓ init_db imported successfully")
except Exception as e:
    print(f"✗ Failed to import init_db: {e}")

try:
    from api.auth import router as auth_router
    print("✓ auth_router imported successfully")
except Exception as e:
    print(f"✗ Failed to import auth_router: {e}")

print("Import test completed!")
