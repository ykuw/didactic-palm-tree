<?php

	$output = fopen("test.csv", "w"); // File name // Also location of the file

	$connection = new MongoClient(); // Connection settings
	$col = "test"; // Collection name
	$db = "test"; // Database name
	$collection = $connection->$db->$col; // Select all above

	$cursor = $collection->find(); // Executing MongoDB query to retrieve all data from a MongoDB collection

	foreach($cursor as $cur) // Fetching records
		fputcsv($output, $cur); // Logging records into CSV file format

	fclose($output); // Stop writing

?>