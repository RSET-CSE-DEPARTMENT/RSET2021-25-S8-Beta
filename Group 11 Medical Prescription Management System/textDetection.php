<?php

include('connection.php');

/*
$image = $_POST['image'];

$filename = "input.jpg";
$path = "ocr/media/$filename";
file_put_contents($path,base64_decode($image));
*/

$python = `python ocr/inferencemodel.py`;


$detectedFile = "ocr/prediction_result.txt";
$fh = fopen($detectedFile, 'r');
$predictedText = fread($fh, filesize($detectedFile));
fclose($fh);

echo $predictedText;


?>