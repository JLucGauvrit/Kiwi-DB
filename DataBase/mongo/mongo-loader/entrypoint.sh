#!/bin/sh
set -e

MONGO_URI=${MONGO_URI:-mongodb://root:example@mongo:27017}
MONGO_DB=${MONGO_DB:-safety_db}
MONGO_COLLECTION=${MONGO_COLLECTION:-procedures}

echo "Waiting for MongoDB to be available at ${MONGO_URI}..."
python3 - <<'PY'
import os, time
from pymongo import MongoClient

uri = os.environ.get('MONGO_URI', 'mongodb://root:example@mongo:27017')
for i in range(60):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print('\nMongo is available')
        break
    except Exception:
        print('.', end='', flush=True)
        time.sleep(1)
else:
    raise SystemExit('Timed out waiting for MongoDB')
PY

echo "Running loader script..."
python3 /app/scripts/load_mongo_from_dataset.py --uri "${MONGO_URI}" --db "${MONGO_DB}" --collection "${MONGO_COLLECTION}" --drop

echo "Loader finished. Exiting."
