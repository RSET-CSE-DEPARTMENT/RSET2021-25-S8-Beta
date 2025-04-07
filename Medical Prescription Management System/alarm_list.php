<?php

include('connection.php');

$id = $_POST['id']; 

$sql = "SELECT * FROM reminder_status WHERE reminder_id = '$id'";

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