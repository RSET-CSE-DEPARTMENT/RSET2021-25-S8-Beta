<?php

	include('connection.php');

	$uid = $_POST['uid'];
	$image = $_POST['image'];
	$title = $_POST['title'];
	$hospitalName = $_POST['hospitalName'];
	$doctorName = $_POST['doctorName'];
	$department = $_POST['department'];
	$date = $_POST['date'];
	$result = $_POST['result'];

	$filename = "presc"."$date"."_$date.jpg";
	$path = "uploads/$filename";
	file_put_contents($path,base64_decode($image));


	$sql = "INSERT INTO tbl_prescription(uid, title, hospital_name, doctor_name, department, date, image, result) VALUES
								   ('$uid', '$title', '$hospitalName','$doctorName','$department','$date','$filename', '$result')";

	// echo $sql;

	if(mysqli_query($con,$sql))
	{
		echo "Success";
	}
	else{
		echo "Failed";
	}

?>