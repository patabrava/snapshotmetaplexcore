# Core Collection Snapshot Test Plan

## Phase 1: Problem Analysis & Solution Design

### Test Case 1: Verify Collection Type
**Objective**: Confirm that `6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq` is a Metaplex Core collection

**Expected Outcome**: 
- Collection exists on Solana mainnet
- Collection uses Metaplex Core standard (not Token Metadata)
- Can identify the collection's assets

**Test Script**: Manual verification using Solana explorer

### Test Case 2: Current metaboss Capability Assessment 
**Objective**: Determine if current metaboss supports Core collections

**Expected Outcome**:
- metaboss CLI supports MCC collections via `snapshot mints` with group-key `mcc`
- metaboss does NOT support Core collections yet
- Need alternative approach for Core collections

**Status**: ✅ CONFIRMED - metaboss does not support Core collections

### Test Case 3: Alternative Solution Approach
**Objective**: Design alternative approach for Core collection snapshots

**Solution Options**:
1. Use DAS API directly (like metaboss does internally)
2. Use Metaplex Core SDK to query collection assets
3. Use Helius or other RPC provider that supports Core

**Selected Approach**: Use DAS API with Core-specific queries

## Phase 2: RPC Provider Selection

### Test Case 4: RPC Provider Research
**Objective**: Find RPC provider that supports DAS API and Core collections

**Candidates from research**:
- Helius (recommended by metaboss docs)
- Alchemy
- QuickNode  
- InstantNodes

**Selected**: Helius (free tier: 100k requests/day)

## Phase 3: Implementation Plan

### Core Collection Asset Query Method
Since this is a Metaplex Core collection, we need to:
1. Use the DAS API `getAssetsByGroup` method with groupKey "collection"
2. Query the collection address directly
3. Parse the results to extract mint addresses

### Manual Test Script (Phase 1)
```bash
# Test RPC endpoint accessibility
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"getHealth"}' \
  https://mainnet.helius-rpc.com/?api-key=YOUR_API_KEY

# Test Core collection query  
curl -X POST -H "Content-Type: application/json" \
  --data '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getAssetsByGroup",
    "params": {
      "groupKey": "collection",
      "groupValue": "6AExhZD5ihDJNKexiMf9jByUf37EcHn9eNN4WL5PJTAq",
      "page": 1,
      "limit": 1000
    }
  }' \
  https://mainnet.helius-rpc.com/?api-key=YOUR_API_KEY
```

## Phase 4: Final Implementation

Once the manual tests pass, create a script that:
1. Queries all pages of assets from the Core collection
2. Extracts mint addresses 
3. Saves to JSON file in metaboss format
4. Validates the output

## Success Criteria
- ✅ Identify Core collection vs Token Metadata collection
- ⏳ Get valid RPC endpoint with DAS API support  
- ⏳ Successfully query Core collection assets
- ⏳ Extract mint addresses into proper JSON format
- ⏳ Create snapshot file compatible with metaboss output format

## Failure Modes & Mitigation
- **RPC Issues**: Have backup RPC providers ready
- **Collection Not Found**: Verify address on block explorer
- **Rate Limiting**: Implement delays between requests
- **Invalid Collection Type**: Document the finding and suggest alternatives 