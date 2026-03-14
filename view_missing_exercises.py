#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone script to view missing exercise requests.
Run this script to see which exercises users are requesting.

Usage:
    python view_missing_exercises.py

Note: If the database is locked (Streamlit app running), close the app first.
"""

from chat_pt.database import get_missing_exercise_requests, init_db
import sys

def main():
    try:
        # Initialize database
        init_db()
    except Exception as e:
        if "locked" in str(e).lower():
            print("\n[!] Database is locked. Please close the Streamlit app and try again.\n")
            return
        raise

    # Get all missing exercise requests
    requests = get_missing_exercise_requests(min_requests=1, limit=100)

    if not requests:
        print("\n[OK] No missing exercise requests yet!\n")
        return

    print("\n" + "="*70)
    print("[STATS] MISSING EXERCISE REQUESTS")
    print("="*70)
    print(f"\nTotal unique exercises requested: {len(requests)}\n")

    # Display high priority (5+ requests)
    high_priority = [r for r in requests if r['request_count'] >= 5]
    if high_priority:
        print("[HIGH] HIGH PRIORITY (5+ requests):")
        print("-" * 70)
        for req in high_priority:
            print(f"  * {req['exercise_name']:<40} {req['request_count']:>3} requests")
        print()

    # Display medium priority (3-4 requests)
    medium_priority = [r for r in requests if 3 <= r['request_count'] < 5]
    if medium_priority:
        print("[MED] MEDIUM PRIORITY (3-4 requests):")
        print("-" * 70)
        for req in medium_priority:
            print(f"  * {req['exercise_name']:<40} {req['request_count']:>3} requests")
        print()

    # Display low priority (1-2 requests)
    low_priority = [r for r in requests if r['request_count'] < 3]
    if low_priority:
        print("[LOW] LOW PRIORITY (1-2 requests):")
        print("-" * 70)
        for req in low_priority[:20]:  # Show first 20
            print(f"  * {req['exercise_name']:<40} {req['request_count']:>3} requests")
        if len(low_priority) > 20:
            print(f"  ... and {len(low_priority) - 20} more")
        print()

    print("="*70)
    print("\n[NEXT] Next Steps:")
    print("   1. Prioritize exercises with 5+ requests")
    print("   2. Research form tutorials on YouTube")
    print("   3. Add to chat_pt/exercise_data.py")
    print("   4. Update AI trainer knowledge if needed\n")

    # Option to export to CSV
    export = input("Export to CSV? (y/n): ").lower().strip()
    if export == 'y':
        filename = "missing_exercises.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Exercise Name,Request Count,Last Requested\n")
            for req in requests:
                f.write(f"{req['exercise_name']},{req['request_count']},{req['last_requested']}\n")
        print(f"[OK] Exported to {filename}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)
