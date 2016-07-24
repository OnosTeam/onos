<?php

ini_set('date.timezone', 'UTC');
$time= date('Y:m:d:H:i:s', time() - date('Z')); 
$year=date('Y', time() - date('Z'));
$month=date('m', time() - date('Z'));
$day=date('d', time() - date('Z'));
$hour=date('H', time() - date('Z'));
$minute=date('i', time() - date('Z'));
$second=date('s', time() - date('Z'));

#$date=substr($time,0,10);
$date=substr($time,0,13);  #2015:08:19
echo $time4;
echo "<br>";

echo $year;
echo "<br>";
echo $month;
echo "<br>";
echo $day;
echo "<br>";
echo $hour;
echo "<br>";
echo $minute;
echo "<br>";
echo $second;
echo "<br>";
echo $date;


?>
