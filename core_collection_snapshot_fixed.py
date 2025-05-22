#!/usr/bin/env python3
"""
Core Collection Snapshot Tool - Fixed Version
Alternative to metaboss for Metaplex Core collections
Addresses pagination issues and provides holders-only output

Debugging improvements:
- Enhanced pagination logic
- Comprehensive instrumentation
- Holders-only output format
- Data verification checks
"""

import requests
import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from collections import Counter

class CoreCollectionSnapshotFixed:
    def __init__(self, rpc_url: str, collection_address: str):
        self.rpc_url = rpc_url
        self.collection_address = collection_address
        self.session = requests.Session()
        self.assets = []
        self.debug_info = {
            "total_pages_fetched": 0,
            "total_requests": 0,
            "api_total_reported": None,
            "pagination_history": []
        }
        
    def query_assets_page(self, page: int, limit: int = 1000) -> Tuple[List[Dict], Dict]:
        """Query a single page of assets with detailed debugging info"""
        print(f"🔍 DEBUG: Querying page {page} with limit {limit}")
        
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
            self.debug_info["total_requests"] += 1
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"❌ DAS API Error: {result['error']}")
                return [], {"error": result["error"]}
                
            if "result" not in result:
                print(f"❌ Unexpected response format")
                return [], {"error": "No result field"}
            
            items = result["result"].get("items", [])
            total = result["result"].get("total", 0)
            
            # Store API total from first successful request
            if self.debug_info["api_total_reported"] is None:
                self.debug_info["api_total_reported"] = total
                print(f"📊 DEBUG: API reports total collection size: {total}")
            
            # Enhanced pagination logic - continue until we get empty results
            has_more = len(items) > 0
            
            page_info = {
                "page": page,
                "items_received": len(items),
                "api_total": total,
                "has_more": has_more
            }
            
            self.debug_info["pagination_history"].append(page_info)
            
            print(f"📄 DEBUG: Page {page} returned {len(items)} items (API total: {total})")
            
            return items, page_info
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return [], {"error": str(e)}
    
    def fetch_all_assets(self, delay_seconds: float = 0.1) -> bool:
        """Fetch ALL assets with improved pagination logic"""
        print(f"🔍 Fetching ALL assets from collection: {self.collection_address}")
        print(f"🎯 Expected: ~4274 assets, ~1500+ unique holders")
        
        page = 1
        total_fetched = 0
        consecutive_empty_pages = 0
        max_empty_pages = 3  # Stop after 3 consecutive empty pages
        
        while True:
            print(f"📄 Fetching page {page}...", end=" ")
            
            items, page_info = self.query_assets_page(page)
            
            if "error" in page_info:
                if page == 1:
                    print("❌ Failed to fetch any assets")
                    return False
                else:
                    print("❌ Error during pagination, stopping")
                    break
                    
            if items:
                self.assets.extend(items)
                total_fetched += len(items)
                consecutive_empty_pages = 0
                print(f"✅ Got {len(items)} assets (total: {total_fetched})")
            else:
                consecutive_empty_pages += 1
                print(f"⚠️ Empty page ({consecutive_empty_pages}/{max_empty_pages})")
                
                if consecutive_empty_pages >= max_empty_pages:
                    print(f"🛑 Stopping after {max_empty_pages} consecutive empty pages")
                    break
                    
            self.debug_info["total_pages_fetched"] = page
            page += 1
            
            # Rate limiting delay
            if delay_seconds > 0:
                time.sleep(delay_seconds)
                
            # Safety check - prevent infinite loops
            if page > 100:  # Reasonable upper bound
                print(f"⚠️ Safety stop: Reached page {page}, stopping to prevent infinite loop")
                break
        
        print(f"🎉 Pagination completed! Fetched {total_fetched} total assets")
        print(f"📊 DEBUG: Fetched {page-1} pages, made {self.debug_info['total_requests']} requests")
        
        # Verify against expected counts
        expected_assets = 4274
        if total_fetched < expected_assets * 0.95:  # Allow 5% tolerance
            print(f"⚠️ WARNING: Fetched {total_fetched} assets, expected ~{expected_assets}")
            print(f"💡 This might indicate incomplete data collection")
        
        return total_fetched > 0
    
    def extract_unique_holders(self) -> List[str]:
        """Extract unique holder addresses only"""
        holders_set = set()
        
        for asset in self.assets:
            ownership = asset.get("ownership", {})
            owner = ownership.get("owner")
            
            if owner:
                holders_set.add(owner)
        
        unique_holders = list(holders_set)
        print(f"📊 DEBUG: Found {len(unique_holders)} unique holders from {len(self.assets)} assets")
        
        return unique_holders
    
    def analyze_holder_distribution(self) -> Dict:
        """Analyze holder distribution for debugging"""
        holder_counts = Counter()
        
        for asset in self.assets:
            ownership = asset.get("ownership", {})
            owner = ownership.get("owner")
            
            if owner:
                holder_counts[owner] += 1
        
        unique_holders = len(holder_counts)
        total_assets = sum(holder_counts.values())
        avg_assets_per_holder = total_assets / unique_holders if unique_holders > 0 else 0
        
        analysis = {
            "unique_holders": unique_holders,
            "total_assets_with_owners": total_assets,
            "avg_assets_per_holder": round(avg_assets_per_holder, 2),
            "top_5_holders": holder_counts.most_common(5),
            "single_asset_holders": sum(1 for count in holder_counts.values() if count == 1),
            "multi_asset_holders": sum(1 for count in holder_counts.values() if count > 1)
        }
        
        return analysis
    
    def create_holders_only_snapshot(self) -> Dict:
        """Create snapshot with only unique holder addresses"""
        unique_holders = self.extract_unique_holders()
        analysis = self.analyze_holder_distribution()
        
        snapshot_data = {
            "collection_address": self.collection_address,
            "collection_type": "metaplex_core",
            "snapshot_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_unique_holders": len(unique_holders),
            "total_assets_processed": len(self.assets),
            "holders": sorted(unique_holders),  # Sort for consistency
            "holder_analysis": analysis,
            "debug_info": self.debug_info,
            "method": "das_api_core_collection_query_fixed",
            "rpc_endpoint": self.rpc_url.split('?')[0]
        }
        
        return snapshot_data
    
    def save_holders_snapshot(self, output_file: str) -> bool:
        """Save holders-only snapshot"""
        try:
            snapshot_data = self.create_holders_only_snapshot()
            
            with open(output_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            print(f"💾 Holders snapshot saved to: {output_file}")
            print(f"👥 Unique holders: {snapshot_data['total_unique_holders']}")
            print(f"📦 Total assets: {snapshot_data['total_assets_processed']}")
            
            # Verification against expected numbers
            expected_holders = 1500
            actual_holders = snapshot_data['total_unique_holders']
            expected_assets = 4274
            actual_assets = snapshot_data['total_assets_processed']
            
            print(f"\n📊 VERIFICATION:")
            print(f"   Holders: {actual_holders} (expected ~{expected_holders}) - {'✅ GOOD' if actual_holders >= expected_holders * 0.9 else '⚠️ LOW'}")
            print(f"   Assets:  {actual_assets} (expected ~{expected_assets}) - {'✅ GOOD' if actual_assets >= expected_assets * 0.95 else '⚠️ LOW'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save snapshot: {e}")
            return False
    
    def print_debug_summary(self):
        """Print comprehensive debug information"""
        print(f"\n🔍 DEBUG SUMMARY:")
        print(f"   Total pages fetched: {self.debug_info['total_pages_fetched']}")
        print(f"   Total API requests: {self.debug_info['total_requests']}")
        print(f"   API reported total: {self.debug_info['api_total_reported']}")
        print(f"   Actual assets collected: {len(self.assets)}")
        
        if self.debug_info["pagination_history"]:
            print(f"   Pagination pattern:")
            for i, page_info in enumerate(self.debug_info["pagination_history"][-5:]):  # Last 5 pages
                print(f"     Page {page_info['page']}: {page_info['items_received']} items")

def load_config() -> Optional[Dict]:
    """Load configuration from rpc_config.json if it exists"""
    try:
        with open("rpc_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    print("🚀 Core Collection Snapshot Tool - FIXED VERSION")
    print("=" * 60)
    print("🔧 Improvements: Enhanced pagination, holders-only output, debug instrumentation")
    
    # Try to load existing config
    config = load_config()
    
    if config:
        print(f"📋 Using saved configuration:")
        print(f"   Collection: {config['collection_address']}")
        print(f"   RPC: {config['rpc_url'].split('?')[0]}")
        
        rpc_url = config["rpc_url"]
        collection_address = config["collection_address"]
    else:
        print("❌ No configuration found. Please run test_rpc_endpoint.py first")
        sys.exit(1)
    
    # Create snapshot tool instance
    snapshot_tool = CoreCollectionSnapshotFixed(rpc_url, collection_address)
    
    # Fetch all assets with improved logic
    if not snapshot_tool.fetch_all_assets():
        print("❌ Failed to fetch assets")
        sys.exit(1)
    
    # Print debug information
    snapshot_tool.print_debug_summary()
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    collection_short = collection_address[:8]
    
    holders_file = f"core_collection_holders_only_{collection_short}_{timestamp}.json"
    
    # Save holders-only snapshot
    print(f"\n💾 Saving holders-only snapshot...")
    
    if snapshot_tool.save_holders_snapshot(holders_file):
        print(f"\n🎉 SUCCESS! Holders-only snapshot completed")
        print(f"👥 Output file: {holders_file}")
        print(f"\n💡 This file contains only unique holder addresses as requested")
    else:
        print(f"\n❌ Snapshot failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 