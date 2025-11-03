#!/bin/bash
# Testing
source ./secrets.sh
echo "Spinning off a new container..."

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "$FUNC_KEY&app_name=lion-task-1234&task_type=optimize")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep HTTP_STATUS | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response body:"
echo "$BODY"
echo "HTTP Status: $HTTP_STATUS"

echo "Spinning off a new container... DEFAULT_HOST_KEY"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "$DEFAULT_HOST_KEY&app_name=lion-task-1234&task_type=optimize")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep HTTP_STATUS | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response body:"
echo "$BODY"
echo "HTTP Status: $HTTP_STATUS"s

echo "Spinning off a new container... MASTER_HOSTKEY"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "$MASTER_HOST_KEY&app_name=lion-task-1234&task_type=optimize")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep HTTP_STATUS | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response body:"
echo "$BODY"
echo "HTTP Status: $HTTP_STATUS"
