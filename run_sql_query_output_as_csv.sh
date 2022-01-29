#!/bin/bash

echo "SELECT LEFT(c.datetime, 7), c.result, COUNT(*) FROM calls c JOIN outgoing o ON o.uid = c.out_id JOIN sip_gateways sg ON sg.host = o.host WHERE sg.carrier = 'colt' AND c.datetime > '2020-01-01' GROUP BY LEFT(c.datetime, 7), c.result" | mysql -h -u -p db | sed 's/\t/,/g' > output/result.csv

exit 0