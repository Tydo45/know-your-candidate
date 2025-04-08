#!/bin/bash

PORT=8001

TUNNEL_PID=$(lsof -ti :$PORT)

if [ -n "$TUNNEL_PID" ]; then
  echo "Closing SSH tunnel on port $PORT (PID: $TUNNEL_PID)"
  kill $TUNNEL_PID
  echo "Tunnel closed."
else
  echo "No tunnel found on port $PORT."
fi

