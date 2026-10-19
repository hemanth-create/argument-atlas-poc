"""Offline smoke demo: python cli_demo.py 'differential diagnosis'"""
import sys
from core import load_records, search, source_link

query = " ".join(sys.argv[1:]) or "differential diagnosis"
records = load_records()
print(f"Argument Atlas POC | {len(records)} records | Search: {query!r}")
for result in search(records, query=query):
    print(f"\n{result['case_name']} — {result['expert']} | {result['outcome']}")
    print(f"  {result['court_reasoning']}")
    print(f"  {source_link(result)}")
