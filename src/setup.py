from db.utils import create_all_tables
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("command",choices=["init-db"])

args = parser.parse_args()

if args.command == "init-db":
    create_all_tables()