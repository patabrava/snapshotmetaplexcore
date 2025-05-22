#!/usr/bin/env python3
"""
Test script for RPC endpoint connectivity and DAS API functionality
Part of Core Collection Snapshot implementation
"""

import requests
import json
import sys
import os

def test_rpc_health(rpc_url):
    """Test if RPC endpoint is accessible"""
    print(f"Testing RPC health at: {rpc_url}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getHealth"
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ RPC Health Check: {result}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ RPC Health Check Failed: {e}")
        return False

def test_core_collection_query(rpc_url, collection_address, limit=5):
    """Test Core collection asset query with small limit"""
    print(f"\nTesting Core collection query for: {collection_address}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAssetsByGroup",
        "params": {
            "groupKey": "collection",
            "groupValue": collection_address,
            "page": 1,
            "limit": limit
        }
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            print(f"❌ DAS API Error: {result['error']}")
            return False
            
        if "result" in result:
            assets = result["result"]["items"]
            total = result["result"]["total"]
            
            print(f"✅ Found {total} total assets in collection")
            print(f"✅ Retrieved {len(assets)} assets in test query")
            
            if assets:
                print(f"✅ Sample asset ID: {assets[0]['id']}")
                print(f"✅ Sample asset interface: {assets[0].get('interface', 'Unknown')}")
                
            return True, total
        else:
            print(f"❌ Unexpected response format: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Collection Query Failed: {e}")
        return False

def main():
    # Target collection address
    COLLECTION_ADDRESS = "6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq"
    
    # RPC URLs to test (public endpoints first, then with API key)
    rpc_urls = [
        "https://mainnet.helius-rpc.com",  # Public endpoint
        "https://api.mainnet-beta.solana.com"  # Solana Labs public RPC
    ]
    
    # Check for API key environment variable
    helius_api_key = os.getenv('HELIUS_API_KEY')
    if helius_api_key:
        rpc_urls.insert(0, f"https://mainnet.helius-rpc.com/?api-key={helius_api_key}")
        print(f"🔑 Using Helius API key from environment")
    else:
        print("ℹ️  No HELIUS_API_KEY found in environment, using public endpoints")
        print("ℹ️  Set HELIUS_API_KEY environment variable for better rate limits")
    
    successful_rpc = None
    
    for rpc_url in rpc_urls:
        print(f"\n{'='*60}")
        print(f"Testing RPC: {rpc_url.split('?')[0]}...")  # Hide API key in output
        
        # Test health first
        if test_rpc_health(rpc_url):
            # Test collection query
            result = test_core_collection_query(rpc_url, COLLECTION_ADDRESS)
            
            if result and result[0]:  # If query was successful
                successful_rpc = rpc_url
                total_assets = result[1]
                print(f"\n🎉 SUCCESS! RPC endpoint works for Core collection queries")
                print(f"📊 Collection has {total_assets} total assets")
                break
        
        print(f"⚠️  Failed to use this RPC endpoint")
    
    if successful_rpc:
        print(f"\n{'='*60}")
        print(f"✅ READY FOR FULL IMPLEMENTATION")
        print(f"📡 Working RPC: {successful_rpc.split('?')[0]}")
        print(f"🗂️  Collection: {COLLECTION_ADDRESS}")
        print(f"📦 Total Assets: {total_assets}")
        
        # Save successful configuration
        config = {
            "rpc_url": successful_rpc,
            "collection_address": COLLECTION_ADDRESS,
            "total_assets": total_assets
        }
        
        with open("rpc_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration saved to rpc_config.json")
        
    else:
        print(f"\n❌ FAILED: No working RPC endpoint found")
        print(f"💡 Try setting HELIUS_API_KEY environment variable")
        sys.exit(1)

if __name__ == "__main__":
    main() 