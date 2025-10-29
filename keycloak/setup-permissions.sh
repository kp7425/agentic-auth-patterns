#!/bin/bash
set -e

echo "Waiting for Keycloak to be ready..."
sleep 15

echo "Configuring token exchange permissions..."

# Get admin access token
ADMIN_TOKEN=$(curl -s -X POST "http://keycloak:8080/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r '.access_token')

echo "Got admin token"

# Get internal-api client's internal ID
CLIENT_UUID=$(curl -s -X GET "http://keycloak:8080/admin/realms/agentic-demo/clients?clientId=internal-api" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

echo "internal-api client UUID: $CLIENT_UUID"

# Enable authorization services for internal-api client
curl -s -X PUT "http://keycloak:8080/admin/realms/agentic-demo/clients/$CLIENT_UUID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "internal-api",
    "enabled": true,
    "bearerOnly": false,
    "publicClient": false,
    "serviceAccountsEnabled": false,
    "authorizationServicesEnabled": true
  }'

echo "Enabled authorization services"

# Get orchestrator client UUID
ORCHESTRATOR_UUID=$(curl -s -X GET "http://keycloak:8080/admin/realms/agentic-demo/clients?clientId=orchestrator" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

echo "orchestrator client UUID: $ORCHESTRATOR_UUID"

# Create token-exchange scope
curl -s -X POST "http://keycloak:8080/admin/realms/agentic-demo/clients/$CLIENT_UUID/authz/resource-server/scope" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "token-exchange"
  }'

echo "Created token-exchange scope"

# Create client policy for orchestrator
POLICY_ID=$(curl -s -X POST "http://keycloak:8080/admin/realms/agentic-demo/clients/$CLIENT_UUID/authz/resource-server/policy/client" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "orchestrator-policy",
    "clients": ["'$ORCHESTRATOR_UUID'"]
  }' | jq -r '.id')

echo "Created orchestrator policy: $POLICY_ID"

# Create token-exchange permission
curl -s -X POST "http://keycloak:8080/admin/realms/agentic-demo/clients/$CLIENT_UUID/authz/resource-server/permission/scope" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "token-exchange-permission",
    "scopes": ["token-exchange"],
    "policies": ["'$POLICY_ID'"]
  }'

echo "Created token-exchange permission"
echo "Token exchange configuration complete!"
