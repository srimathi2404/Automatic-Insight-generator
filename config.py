import os
from dotenv import load_dotenv

load_dotenv()

TRINO_HOST = os.getenv("TRINO_HOST")
TRINO_PORT = int(os.getenv("TRINO_PORT", 8443))
TRINO_USER = os.getenv("TRINO_USER")
TRINO_PASSWORD = os.getenv("TRINO_PASSWORD")
TRINO_CERT = os.getenv("TRINO_CERT")