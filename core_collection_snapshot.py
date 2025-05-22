#!/usr/bin/env python3
"""
Core Collection Snapshot Tool
Alternative to metaboss for Metaplex Core collections

This script queries all assets from a Metaplex Core collection using DAS API
and creates a snapshot file compatible with metaboss format.
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class CoreCollectionSnapshot:
    def __init__(self, rpc_url: str, collection_address: str):
        self.rpc_url = rpc_url
        self.collection_address = collection_address
        self.session = requests.Session()
        self.assets = []
        
    def query_assets_page(self, page: int, limit: int = 1000) -> Tuple[List[Dict], bool]:
        """Query a single page of assets from the collection"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAssetsByGroup",
            "params": {
                "groupKey": "collection",
                "groupValue": self.collection_address,
                "page": page,
                "limit": limit
            }
        }
        
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"❌ DAS API Error: {result['error']}")
                return [], False
                
            if "result" not in result:
                print(f"❌ Unexpected response format")
                return [], False
            
            items = result["result"].get("items", [])
            total = result["result"].get("total", 0)
            
            # Check if we have more pages
            has_more = len(items) == limit and (page * limit) < total
            
            return items, has_more
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return [], False
    
    def fetch_all_assets(self, delay_seconds: float = 0.1) -> bool:
        """Fetch all assets from the collection with pagination"""
        print(f"🔍 Fetching all assets from collection: {self.collection_address}")
        
        page = 1
        total_fetched = 0
        
        while True:
            print(f"📄 Fetching page {page}...", end=" ")
            
            items, has_more = self.query_assets_page(page)
            
            if not items and page == 1:
                print("❌ Failed to fetch any assets")
                return False
                
            if items:
                self.assets.extend(items)
                total_fetched += len(items)
                print(f"✅ Got {len(items)} assets (total: {total_fetched})")
            else:
                print("✅ No more assets")
                
            if not has_more:
                break
                
            page += 1
            
            # Rate limiting delay
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        
        print(f"🎉 Successfully fetched {total_fetched} total assets")
        return True
    
    def extract_mint_addresses(self) -> List[str]:
        """Extract mint addresses from assets"""
        mint_addresses = []
        
        for asset in self.assets:
            # For Core assets, the 'id' field is typically the mint address
            mint_id = asset.get("id")
            if mint_id:
                mint_addresses.append(mint_id)
        
        return mint_addresses
    
    def format_metaboss_compatible(self) -> Dict:
        """Format the snapshot data to be compatible with metaboss output"""
        mint_addresses = self.extract_mint_addresses()
        
        # Create metaboss-style output
        snapshot_data = {
            "collection_address": self.collection_address,
            "collection_type": "metaplex_core",
            "snapshot_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_assets": len(mint_addresses),
            "mint_addresses": mint_addresses,
            "method": "das_api_core_collection_query",
            "rpc_endpoint": self.rpc_url.split('?')[0]  # Hide API key
        }
        
        return snapshot_data
    
    def save_snapshot(self, output_file: str) -> bool:
        """Save the snapshot to a JSON file"""
        try:
            snapshot_data = self.format_metaboss_compatible()
            
            with open(output_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            print(f"💾 Snapshot saved to: {output_file}")
            print(f"📊 Total assets: {snapshot_data['total_assets']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save snapshot: {e}")
            return False
    
    def create_holders_list(self) -> List[Dict]:
        """Create a list of current holders from the assets"""
        holders = []
        
        for asset in self.assets:
            ownership = asset.get("ownership", {})
            owner = ownership.get("owner")
            
            if owner:
                holder_info = {
                    "mint_address": asset.get("id"),
                    "owner_address": owner,
                    "frozen": ownership.get("frozen", False)
                }
                holders.append(holder_info)
        
        return holders
    
    def save_holders_snapshot(self, output_file: str) -> bool:
        """Save holders snapshot (similar to metaboss snapshot holders)"""
        try:
            holders = self.create_holders_list()
            
            holders_data = {
                "collection_address": self.collection_address,
                "collection_type": "metaplex_core", 
                "snapshot_timestamp": datetime.utcnow().isoformat() + "Z",
                "total_holders": len(holders),
                "holders": holders,
                "method": "das_api_core_collection_query",
                "rpc_endpoint": self.rpc_url.split('?')[0]
            }
            
            with open(output_file, 'w') as f:
                json.dump(holders_data, f, indent=2)
            
            print(f"💾 Holders snapshot saved to: {output_file}")
            print(f"👥 Total holders: {len(holders)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save holders snapshot: {e}")
            return False

def load_config() -> Optional[Dict]:
    """Load configuration from rpc_config.json if it exists"""
    try:
        with open("rpc_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    print("🚀 Core Collection Snapshot Tool")
    print("=" * 50)
    
    # Try to load existing config
    config = load_config()
    
    if config:
        print(f"📋 Using saved configuration:")
        print(f"   Collection: {config['collection_address']}")
        print(f"   RPC: {config['rpc_url'].split('?')[0]}")
        print(f"   Expected assets: {config.get('total_assets', 'Unknown')}")
        
        rpc_url = config["rpc_url"]
        collection_address = config["collection_address"]
    else:
        print("❌ No configuration found. Please run test_rpc_endpoint.py first")
        sys.exit(1)
    
    # Create snapshot tool instance
    snapshot_tool = CoreCollectionSnapshot(rpc_url, collection_address)
    
    # Fetch all assets
    if not snapshot_tool.fetch_all_assets():
        print("❌ Failed to fetch assets")
        sys.exit(1)
    
    # Generate output filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    collection_short = collection_address[:8]
    
    mints_file = f"core_collection_mints_{collection_short}_{timestamp}.json"
    holders_file = f"core_collection_holders_{collection_short}_{timestamp}.json"
    
    # Save both snapshots
    print(f"\n💾 Saving snapshots...")
    
    success_mints = snapshot_tool.save_snapshot(mints_file)
    success_holders = snapshot_tool.save_holders_snapshot(holders_file)
    
    if success_mints and success_holders:
        print(f"\n🎉 SUCCESS! Core collection snapshot completed")
        print(f"📄 Mint addresses: {mints_file}")
        print(f"👥 Holders data: {holders_file}")
        print(f"\n💡 These files are compatible with metaboss workflows")
    else:
        print(f"\n❌ Snapshot failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 