<?php

include('connection.php');

$uid = $_POST['uid'];
// $uid = "1";

$sql = "SELECT * FROM tbl_prescription WHERE uid = '$uid'";

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