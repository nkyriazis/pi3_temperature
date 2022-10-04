#! /bin/bash

prometheus-node-exporter &
while true
do
 prometheus-vcgencmd >/var/lib/prometheus/node-exporter/vcgencmd.prom
 sleep 1
done