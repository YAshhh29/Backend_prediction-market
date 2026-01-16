"""
Test script to run one fetch cycle without scheduling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import fetch_and_store_markets

print("Testing single data fetch cycle...\n")
result = fetch_and_store_markets()

if result:
    print("\n✓ Test completed successfully!")
else:
    print("\n✗ Test failed - check logs for details")
