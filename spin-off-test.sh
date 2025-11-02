#!/bin/bash
source ./secrets.sh
echo "Spinning off a new container..."

echo $FUNC_KEY

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "https://lion-func-bqhycbhdfna4fder.westeurope-01.azurewebsites.net/api/createApp?app_name=lion-task-1234&task_type=optimize&code=$FUNC_KEY")

# Extract HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep HTTP_STATUS | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response body:"
echo "$BODY"
echo "HTTP Status: $HTTP_STATUS"
