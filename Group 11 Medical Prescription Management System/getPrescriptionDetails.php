<?php

include('connection.php');

$id = $_POST['id'];
// $id = '1';

$sql = "SELECT * FROM tbl_prescription WHERE id = '$id'";

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