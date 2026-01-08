#!/usr/bin/env python3
"""
Load the `MongoDB/safety_procedure_dataset` dataset and insert documents into MongoDB.

Usage examples:
  python3 scripts/load_mongo_from_dataset.py --uri mongodb://localhost:27017 --db safety_db --collection procedures --drop

"""
import argparse
import os
from datasets import load_dataset
from pymongo import MongoClient


def main():
    parser = argparse.ArgumentParser(description="Load safety_procedure_dataset into MongoDB")
    parser.add_argument('--uri', default=os.environ.get('MONGO_URI', 'mongodb://localhost:27017'),
                        help='MongoDB connection URI')
    parser.add_argument('--db', default='safety_db', help='Database name')
    parser.add_argument('--collection', default='procedures', help='Collection name')
    parser.add_argument('--drop', action='store_true', help='Drop collection before inserting')
    args = parser.parse_args()

    print(f"Loading dataset 'MongoDB/safety_procedure_dataset'...")
    ds = load_dataset("MongoDB/safety_procedure_dataset")

    client = MongoClient(args.uri)
    db = client[args.db]
    col = db[args.collection]

    if args.drop:
        print(f"Dropping collection {args.db}.{args.collection} (if exists)")
        col.drop()

    inserted = 0
    for split_name, split_dataset in ds.items():
        print(f"Inserting split: {split_name} with {len(split_dataset)} items")
        for item in split_dataset:
            doc = dict(item)
            doc['_split'] = split_name
            # Insert document
            col.insert_one(doc)
            inserted += 1

    print(f"Done. Inserted {inserted} documents into {args.db}.{args.collection}")


if __name__ == '__main__':
    main()
