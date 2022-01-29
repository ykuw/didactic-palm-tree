#!/bin/bash

filename="/home/scripts/db/cli.txt"

cat $filename | while read line || [ -n "$line" ]; do echo "SELECT c.DDI, c.CLI, c.datetime AS Timestamp, c.duration AS Duration FROM calls c JOIN queues q ON q.uid = c.qid AND q.grouping = AND q.type = 'outbound' WHERE c.datetime BETWEEN '2019-01-01' AND '2019-07-23' AND c.call_outcome NOT IN ('101', '102') AND c.CLI = ${line}" | mysql -h -u -p db | sed 's/\t/,/g' > output/${line}.csv; done

exit 0