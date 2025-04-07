<?php

include('connection.php');

$id = $_POST['id']; 

$sql = "UPDATE reminder_status SET status = 'completed' WHERE id = '$id'";

if($res = mysqli_query($con, $sql))
{
 	echo "success";  
}
else{
	echo "failed";
}



?>