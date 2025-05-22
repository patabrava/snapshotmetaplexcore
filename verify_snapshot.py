#!/usr/bin/env python3
"""
Verification script for Core collection snapshot results
Analyzes the generated snapshot files for integrity and statistics
"""

import json
import sys
from collections import Counter
from datetime import datetime

def analyze_mints_file(filename):
    """Analyze the mints snapshot file"""
    print(f"📄 Analyzing mints file: {filename}")
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print(f"  ✅ Collection: {data['collection_address']}")
        print(f"  ✅ Type: {data['collection_type']}")
        print(f"  ✅ Timestamp: {data['snapshot_timestamp']}")
        print(f"  ✅ Reported total: {data['total_assets']}")
        print(f"  ✅ Actual mints: {len(data['mint_addresses'])}")
        print(f"  ✅ Method: {data['method']}")
        print(f"  ✅ RPC: {data['rpc_endpoint']}")
        
        # Check for duplicates
        unique_mints = set(data['mint_addresses'])
        if len(unique_mints) != len(data['mint_addresses']):
            print(f"  ⚠️  Found {len(data['mint_addresses']) - len(unique_mints)} duplicate mints!")
        else:
            print(f"  ✅ No duplicate mints found")
        
        # Sample mint addresses
        print(f"  📝 Sample mints:")
        for i, mint in enumerate(data['mint_addresses'][:3]):
            print(f"     {i+1}. {mint}")
        
        return data['mint_addresses']
        
    except Exception as e:
        print(f"  ❌ Error reading mints file: {e}")
        return []

def analyze_holders_file(filename):
    """Analyze the holders snapshot file"""
    print(f"\n👥 Analyzing holders file: {filename}")
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print(f"  ✅ Collection: {data['collection_address']}")
        print(f"  ✅ Type: {data['collection_type']}")
        print(f"  ✅ Timestamp: {data['snapshot_timestamp']}")
        print(f"  ✅ Reported holders: {data['total_holders']}")
        print(f"  ✅ Actual records: {len(data['holders'])}")
        
        # Analyze ownership distribution
        owners = [h['owner_address'] for h in data['holders']]
        owner_counts = Counter(owners)
        unique_owners = len(owner_counts)
        
        print(f"  ✅ Unique owners: {unique_owners}")
        print(f"  📊 Avg assets per owner: {len(data['holders'])/unique_owners:.2f}")
        
        # Top holders
        print(f"  👑 Top 5 holders:")
        for i, (owner, count) in enumerate(owner_counts.most_common(5)):
            print(f"     {i+1}. {owner[:12]}... ({count} assets)")
        
        # Check frozen status
        frozen_count = sum(1 for h in data['holders'] if h.get('frozen', False))
        print(f"  🧊 Frozen assets: {frozen_count}")
        
        # Extract mint addresses from holders
        holder_mints = [h['mint_address'] for h in data['holders']]
        
        return holder_mints, owners
        
    except Exception as e:
        print(f"  ❌ Error reading holders file: {e}")
        return [], []

def cross_verify(mints_from_mints_file, mints_from_holders_file):
    """Cross-verify data between both files"""
    print(f"\n🔍 Cross-verification:")
    
    mints_set = set(mints_from_mints_file)
    holders_mints_set = set(mints_from_holders_file)
    
    if mints_set == holders_mints_set:
        print(f"  ✅ Mint addresses match perfectly between both files")
    else:
        missing_in_holders = mints_set - holders_mints_set
        missing_in_mints = holders_mints_set - mints_set
        
        if missing_in_holders:
            print(f"  ⚠️  {len(missing_in_holders)} mints in mints file but not in holders")
        if missing_in_mints:
            print(f"  ⚠️  {len(missing_in_mints)} mints in holders file but not in mints")
    
    print(f"  📊 Mints file count: {len(mints_from_mints_file)}")
    print(f"  📊 Holders file count: {len(mints_from_holders_file)}")

def main():
    print("🔍 Core Collection Snapshot Verification")
    print("=" * 50)
    
    # Find the most recent snapshot files
    import glob
    
    mints_files = glob.glob("core_collection_mints_*.json")
    holders_files = glob.glob("core_collection_holders_*.json")
    
    if not mints_files:
        print("❌ No mints snapshot files found")
        sys.exit(1)
    
    if not holders_files:
        print("❌ No holders snapshot files found")
        sys.exit(1)
    
    # Use the most recent files
    mints_file = sorted(mints_files)[-1]
    holders_file = sorted(holders_files)[-1]
    
    print(f"🎯 Verifying latest snapshots:")
    print(f"   Mints: {mints_file}")
    print(f"   Holders: {holders_file}")
    
    # Analyze both files
    mints_from_mints_file = analyze_mints_file(mints_file)
    mints_from_holders_file, owners = analyze_holders_file(holders_file)
    
    # Cross-verify
    cross_verify(mints_from_mints_file, mints_from_holders_file)
    
    print(f"\n🎉 Verification completed!")
    print(f"📈 Summary:")
    print(f"   Total Assets: {len(mints_from_mints_file)}")
    print(f"   Unique Owners: {len(set(owners)) if owners else 0}")
    print(f"   Files Generated: 2 (mints + holders)")
    print(f"   Data Integrity: {'✅ PASSED' if set(mints_from_mints_file) == set(mints_from_holders_file) else '❌ ISSUES'}")

if __name__ == "__main__":
    main() 