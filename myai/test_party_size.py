#!/usr/bin/env python3
"""Test party size parsing"""

from src.myai.date_parser import parse_party_size

test_queries = [
    "dinner for 5 at 8pm tuesday",
    "dinner for 5",
    "for 5 people",
    "5 people",
    "party of 5",
    "table for 5",
    "dinner for five people",
    "dinner near union square for 6"
]

print("Testing Party Size Parsing\n")
for query in test_queries:
    size = parse_party_size(query)
    print(f"Query: '{query}' -> Party size: {size}")