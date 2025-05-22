# Core Collection Snapshot Tool

This tool provides an alternative to metaboss for taking snapshots of Metaplex Core collections, which are not currently supported by metaboss.

## Overview

Metaboss supports traditional Token Metadata collections via MCC (Metaplex Certified Collections), but Metaplex Core collections use a different standard and require different querying methods. This tool uses the DAS (Digital Asset Standard) API to query Core collections directly.

## Target Collection
- **Collection Address**: `6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq`
- **Type**: Metaplex Core Collection

## Prerequisites

1. **Python 3.7+** with `requests` library:
   ```bash
   pip install requests
   ```

2. **Optional: Helius API Key** for better rate limits:
   - Sign up at [Helius](https://helius.dev)
   - Get a free API key (100k requests/day)
   - Set environment variable: `HELIUS_API_KEY=your_api_key_here`

## Usage

### Step 1: Test RPC Connectivity
```bash
python test_rpc_endpoint.py
```

This will:
- Test multiple RPC endpoints for connectivity
- Verify the target collection exists and is accessible
- Save working configuration to `rpc_config.json`

Expected output:
```
🔑 Using Helius API key from environment
============================================================
Testing RPC: https://mainnet.helius-rpc.com...
Testing RPC health at: https://mainnet.helius-rpc.com/?api-key=...
✅ RPC Health Check: {'result': 'ok'}

Testing Core collection query for: 6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq
✅ Found 5000 total assets in collection
✅ Retrieved 5 assets in test query
✅ Sample asset ID: <asset_mint_address>
✅ Sample asset interface: V1_NFT

🎉 SUCCESS! RPC endpoint works for Core collection queries
📊 Collection has 5000 total assets
============================================================
✅ READY FOR FULL IMPLEMENTATION
📡 Working RPC: https://mainnet.helius-rpc.com
🗂️  Collection: 6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq
📦 Total Assets: 5000
💾 Configuration saved to rpc_config.json
```

### Step 2: Create Full Snapshot
```bash
python core_collection_snapshot.py
```

This will:
- Load the saved RPC configuration
- Fetch all assets from the Core collection (with pagination)
- Create two snapshot files:
  - **Mint addresses**: List of all asset mint addresses
  - **Holders data**: Current owners of each asset

Expected output:
```
🚀 Core Collection Snapshot Tool
==================================================
📋 Using saved configuration:
   Collection: 6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq
   RPC: https://mainnet.helius-rpc.com
   Expected assets: 5000

🔍 Fetching all assets from collection: 6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq
📄 Fetching page 1... ✅ Got 1000 assets (total: 1000)
📄 Fetching page 2... ✅ Got 1000 assets (total: 2000)
📄 Fetching page 3... ✅ Got 1000 assets (total: 3000)
📄 Fetching page 4... ✅ Got 1000 assets (total: 4000)
📄 Fetching page 5... ✅ Got 1000 assets (total: 5000)
🎉 Successfully fetched 5000 total assets

💾 Saving snapshots...
💾 Snapshot saved to: core_collection_mints_6AExhZD5_20241201_143022.json
📊 Total assets: 5000
💾 Holders snapshot saved to: core_collection_holders_6AExhZD5_20241201_143022.json
👥 Total holders: 5000

🎉 SUCCESS! Core collection snapshot completed
📄 Mint addresses: core_collection_mints_6AExhZD5_20241201_143022.json
👥 Holders data: core_collection_holders_6AExhZD5_20241201_143022.json

💡 These files are compatible with metaboss workflows
```

## Output Files

### Mint Addresses File
Contains list of all mint addresses in metaboss-compatible format:
```json
{
  "collection_address": "6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq",
  "collection_type": "metaplex_core",
  "snapshot_timestamp": "2024-12-01T14:30:22.123456Z",
  "total_assets": 5000,
  "mint_addresses": [
    "asset_mint_1...",
    "asset_mint_2...",
    "..."
  ],
  "method": "das_api_core_collection_query",
  "rpc_endpoint": "https://mainnet.helius-rpc.com"
}
```

### Holders File
Contains current ownership information:
```json
{
  "collection_address": "6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq",
  "collection_type": "metaplex_core",
  "snapshot_timestamp": "2024-12-01T14:30:22.123456Z",
  "total_holders": 5000,
  "holders": [
    {
      "mint_address": "asset_mint_1...",
      "owner_address": "owner_wallet_1...",
      "frozen": false
    }
  ],
  "method": "das_api_core_collection_query",
  "rpc_endpoint": "https://mainnet.helius-rpc.com"
}
```

## Rate Limiting

The tool includes built-in rate limiting:
- 0.1 second delay between pagination requests
- Uses persistent HTTP session for efficiency
- Graceful error handling for network issues

With Helius free tier (100k requests/day), you can snapshot collections with up to ~90k assets per day (assuming 1k assets per page).

## Troubleshooting

### "No configuration found" error
Run `test_rpc_endpoint.py` first to set up the RPC configuration.

### Rate limiting issues
- Get a Helius API key for higher limits
- Or use the tool during off-peak hours

### Collection not found
- Verify the collection address is correct
- Check that it's a Metaplex Core collection (not Token Metadata)

## Comparison with metaboss

| Feature | metaboss | This Tool |
|---------|----------|-----------|
| Token Metadata Collections | ✅ | ❌ |
| Metaplex Core Collections | ❌ | ✅ |
| Output Format | JSON | JSON (compatible) |
| Holder Information | ✅ | ✅ |
| Built-in Tool | ✅ | Custom Script |

This tool fills the gap for Core collections until metaboss adds native support. 