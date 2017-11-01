<?php
ini_set('display_errors', 'On');
error_reporting(E_ALL | E_STRICT);
//http://myonos.com/onos/updates/mail_update.php?sn=RouterOP0000&fw=5.23&msg=check
#echo 'sn:' . htmlspecialchars($_GET["sn"]) ;
#echo '<br>';
#echo 'fw:' . htmlspecialchars($_GET["fw"]) ;
#echo '<br>';
#echo 'msg:' . htmlspecialchars($_GET["msg"]);

$sn=$_POST['sn'];
$msg=$_POST['msg'];
$fw=$_POST['fw'];
$hw=$_POST['hw'];
$password=$_POST['pw'];
$send_mail=$_POST['s_mail'];

$from="myonos@onos.com";
$subject="onos_update_msg";
$date = date_create();
$timestamp=date_timestamp_get($date);
echo($timestamp);
$headers = "From:onoscenter:" .$sn;
$message="onoscenter:".$sn." ,hw:".$hw.", ".$msg.", at:".date("Y/m/d")."time:".date("h:i:sa").", timestamp:".$timestamp.",  local_fw".$fw;



if($password=="abcdefghi4321") {//if the password received is correct


  $file = 'updated_onos_centers.txt';
  $csv_row=$sn.','.$hw.','.$fw.','.$timestamp.','.date("Y/m/d").','.date("h:i:sa").','.$msg.PHP_EOL;   // PHP_EOL appens a new line
  // and the LOCK_EX flag to prevent anyone else writing to the file at the same time
  file_put_contents($file, $csv_row, FILE_APPEND | LOCK_EX);

  if($send_mail=="1") {  //if i need to send the mail
    mail("onos.info@gmail.com", $subject, $message, $headers);

  }

}




?>
