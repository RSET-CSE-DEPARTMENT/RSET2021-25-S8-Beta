<?php

	include('connection.php');

	$name = $_POST['name'];
	$image = $_POST['image'];
	$age = $_POST['age'];
	$dob = $_POST['dob'];
	$phone = $_POST['phone'];
	$password = $_POST['password'];
	$emergency = $_POST['emergency'];


	$filename = "userimage"."$date"."_$name.jpg";
	$path = "uploads/$filename";
	file_put_contents($path,base64_decode($image));


	$sql = "INSERT INTO tbl_patient(patient_name, image, age, dob, phone_number, password, emergency_contact) VALUES 
								   ('$name','$filename','$age','$dob','$phone','$password','$emergency')";

	if(mysqli_query($con,$sql))
	{
		echo "Success";
	}
	else{
		echo "Failed";
	}

?>