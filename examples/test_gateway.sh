#!/bin/bash
# MCP Gateway — smoke tests
# Make sure the gateway is running before executing this script.

GATEWAY="http://localhost:8000"
API_KEY="${MCP_API_KEY:-your-secret-key-here}"

echo "=== MCP Gateway Smoke Tests ==="
echo ""

echo "1. Health check (no auth needed)"
curl -s "$GATEWAY/health" | python3 -m json.tool
echo ""

echo "2. Status (no auth needed)"
curl -s "$GATEWAY/status" | python3 -m json.tool
echo ""

echo "3. List servers (auth required)"
curl -s -H "X-API-Key: $API_KEY" "$GATEWAY/v1/servers" | python3 -m json.tool
echo ""

echo "4. Call echo tool"
curl -s -X POST "$GATEWAY/v1/call" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"server": "echo-server", "tool": "echo", "arguments": {"message": "Hello MCP Gateway!"}}' \
  | python3 -m json.tool
echo ""

echo "5. Reject invalid API key (should return 401)"
curl -s -H "X-API-Key: wrong-key" "$GATEWAY/v1/servers" | python3 -m json.tool
echo ""

echo "6. Reject unknown server (should return 404)"
curl -s -X POST "$GATEWAY/v1/call" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"server": "not-in-registry", "tool": "anything", "arguments": {}}' \
  | python3 -m json.tool
echo ""

echo "=== Done ==="
