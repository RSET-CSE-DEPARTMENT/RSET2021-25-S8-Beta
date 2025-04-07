<?php

	include('connection.php');

	date_default_timezone_set("Asia/Kolkata");
	$startDate = date("Y-m-d");

	$uid = $_POST['uid']; 
 
	$sql = "SELECT * FROM medicine_reminder WHERE uid = '$uid'";

	if($res = mysqli_query($con, $sql))
	{
		if(mysqli_num_rows($res) > 0)
		{
			while($row = mysqli_fetch_assoc($res)){
				$data[] = $row;
			}

			echo json_encode($data);
		}
		else{
			echo "failed";
		}
	}
	else{
		echo "error";
	}
?>