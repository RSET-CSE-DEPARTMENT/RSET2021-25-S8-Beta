<?php

include('connection.php');

$phone = $_POST['phone'];
$password = $_POST['password'];

$sql = "SELECT * FROM tbl_patient WHERE phone_number = '$phone' AND password = '$password' ";

if($res = mysqli_query($con, $sql))
{
	if(mysqli_num_rows($res) > 0)
	{
		$row = mysqli_fetch_assoc($res);
		echo json_encode($row);
	}
	else{
		echo "failed";
	}
}
else{
	echo "error";
}



?>