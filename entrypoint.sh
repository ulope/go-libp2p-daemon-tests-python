#!/usr/bin/env bash

/p2pd -autonat -b -connManager -dht -natPortMap -autoRelay -relayActive -relayDiscovery -relayHop &
echo p2pd starting...
sleep 15

python /main.py "$@"
