#!/usr/bin/env python3
"""
JSON to CSV Converter for Core Collection Holders
Converts the holders-only JSON snapshot to CSV format
"""

import json
import csv
import sys
from datetime import datetime

def convert_holders_json_to_csv(json_filename: str, csv_filename: str = None) -> bool:
    """Convert holders JSON file to CSV format"""
    
    try:
        # Read the JSON file
        print(f"📖 Reading JSON file: {json_filename}")
        with open(json_filename, 'r') as f:
            data = json.load(f)
        
        # Extract holders list
        holders = data.get('holders', [])
        collection_address = data.get('collection_address', 'Unknown')
        total_holders = data.get('total_unique_holders', len(holders))
        snapshot_time = data.get('snapshot_timestamp', 'Unknown')
        
        print(f"✅ Found {len(holders)} holders in JSON")
        print(f"📊 Collection: {collection_address}")
        print(f"⏰ Snapshot time: {snapshot_time}")
        
        # Generate CSV filename if not provided
        if csv_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            collection_short = collection_address[:8] if collection_address != 'Unknown' else 'collection'
            csv_filename = f"holders_{collection_short}_{timestamp}.csv"
        
        # Write to CSV file
        print(f"💾 Writing CSV file: {csv_filename}")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['holder_address'])
            
            # Write data rows
            for holder in holders:
                writer.writerow([holder])
        
        print(f"✅ Successfully converted {len(holders)} holders to CSV")
        print(f"📄 Output file: {csv_filename}")
        
        # Verify the CSV file
        with open(csv_filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            csv_count = len(rows) - 1  # Subtract header row
        
        print(f"🔍 Verification: CSV contains {csv_count} data rows (+ 1 header)")
        
        if csv_count == len(holders):
            print(f"✅ Verification passed: Row count matches")
        else:
            print(f"⚠️ Verification warning: Expected {len(holders)}, got {csv_count}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: JSON file '{json_filename}' not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    # Look for the most recent holders JSON file
    import glob
    
    print("🔍 CSV Converter for Core Collection Holders")
    print("=" * 50)
    
    # Find holders JSON files
    json_files = glob.glob("core_collection_holders_only_*.json")
    
    if not json_files:
        print("❌ No holders JSON files found")
        print("💡 Make sure you have run the snapshot tool first")
        sys.exit(1)
    
    # Use the most recent file
    json_filename = sorted(json_files)[-1]
    
    print(f"🎯 Converting latest file: {json_filename}")
    
    # Convert to CSV
    if convert_holders_json_to_csv(json_filename):
        print(f"\n🎉 SUCCESS! JSON converted to CSV")
        print(f"💡 You can now use the CSV file in Excel, Google Sheets, etc.")
    else:
        print(f"\n❌ FAILED! Conversion unsuccessful")
        sys.exit(1)

if __name__ == "__main__":
    main() 