<?php

	include('connection.php');

	date_default_timezone_set("Asia/Kolkata");
	$startDate = date("Y-m-d");

	$uid = $_POST['uid'];
	$medicineName = $_POST['medicineName'];
	$hour = $_POST['hour'];
	$minute = $_POST['minute'];
	$numOfDays = $_POST['numOfDays']; 
	$alarmIds = $_POST['alarmIds']; 
	$alarms = explode("::", $alarmIds);


	$time = $hour.":".$minute;
	$sql = "INSERT INTO medicine_reminder(uid, medicine_name, reminder_time, num_of_days) 
								  VALUES ('$uid','$medicineName','$time','$numOfDays')";

	if($con->query($sql) === TRUE)
	{
		$reminder_id = $con->insert_id;
		$c = 0;
		foreach (range(1, (int)$numOfDays) as $i) {
			$nextDate = date("Y-m-d", strtotime("+$i day", strtotime($startDate)));
    		$day = "Day $i";
    		$a = $alarms[$c];
    		$c++;
    		$sql = "INSERT INTO reminder_status(reminder_id, day, alarm_id, dates, status) 
    									VALUES ('$reminder_id','$day','$a','$nextDate','pending')";

    		$con->query($sql);
		}

		echo "Success";
	}
	else{
		echo "Failed";
	}

?>