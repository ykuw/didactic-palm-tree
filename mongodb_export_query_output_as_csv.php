<?php

	$output = fopen("test.csv", "w"); // File name // Also location for CSV file format // File will automatically be generated

	$headers = ["test", "test2", "test3"]; // Headers
	fputcsv($output, $headers); // Inserting headers into CSV file format

	$username = ''; // Database username
	$password = ''; // Database passsword
	$connection = new MongoClient("mongodb://$username:$password@localhost/test", array("socketTimeoutMS" => "900000")); // Connection settings
	// socketTimeoutMS is to increase execution time limit for slow running queries
	
	$start = new MongoDate(strtotime("2019-04-01")); // Start date
	$end = new MongoDate(strtotime("2019-04-06")); // End date

	$cursor = $connection->test->test->find(array("test" => 123, "test2" => 1234, "test3" => 12345, "datetime" => array('$gt' => $start, '$lte' => $end))); // Execute MongoDB query

	// Above MongoDB query command would translate in SQL as:
	// SELECT *
	// FROM test.test
	// WHERE test = 123
	//	AND test2 = 1234
	//	AND test3 = 12345
	//	AND datetime BETWEEN $start AND $end

	$counter = 0; // Store count for fetched records

	$start = microtime(true); // Start count for script execution time

	foreach($cursor as $cur) { // Fetch records
		$cur['datetime'] = date("Y-m-d H:i:s", $cur['datetime']->sec); // Date in a readable format
		fputcsv($output, $cur); // Logging all data into CSV file format
		$counter++; // Count fetched records
	}

	fclose($output); // Stop writing

	$time_elapsed_secs = microtime(true) - $start; // Script execution time

	echo "\n" . $counter . " records fetched in " . $time_elapsed_secs . " seconds\n"; // Output Result

?>