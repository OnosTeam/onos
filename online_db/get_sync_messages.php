<?php

function test_input($data) {
  $data = trim($data);
  $data=rtrim($data);
  $data = stripslashes($data);
  $data = htmlspecialchars($data);
  return $data;
}
if ($_SERVER["REQUEST_METHOD"] == "POST") {

  if (empty($_POST["onos_password"])) {
    $form_pass = "the post pass is void";
  } 
  else {
    $form_pass = test_input($_POST["onos_password"]);
    echo "ok1";
  }



  if (empty($_POST["onos_key"])) {
    $key = "the post key is void";
  } 
  else {
    $key = test_input($_POST["onos_key"]);
    echo "ok";
  }



  if (empty($_POST["hw_fw_version"])) {
    $hw_fw_version = "the post hw_fw_version is void";
  } 
  else {
    $hw_fw_version = test_input($_POST["hw_fw_version"]);
    echo "ok";
  }




}
else{
echo "no post data received";
die;
}



$db_folder=realpath('./').'/users_db/';
$user_folder_prefix=".dir";  #for example .dirRouterGL0000
$user_folder=$db_folder.$user_folder_prefix.$key."/";
$dbFile = $user_folder.'.db_onos_'.$key ;





if(file_exists($dbFile)){
  $db = new SQLite3($dbFile);
  $result = $db->query("select * from onos_sys where onos_key='$key' ;");
  $row = $result->fetchArray();
  $real_password=test_input($row['onos_password']);
  $db->close();
  echo "real_password:".$real_password;
  if (strcmp($form_pass,$real_password) == 0) {  #if the password is ok
    echo "onos_password_ok";

  }
  else{
    echo "#_error_wrong_onos_password ";

    die;
  }
}
else{

  echo "#_error the db $dbFile does not exist " ;

}


ini_set('date.timezone', 'UTC');
$time = date('Y:m:d:H:i:s', time() - date('Z')); 
echo "time sync".$time;

$db = new SQLite3($dbFile);

#$db->exec("insert or replace INTO onos_sys (onos_key,hw_fw_version,last_sync_time ) VALUES ('$key','$hw_fw_version','$time')");


$db->exec("UPDATE onos_sys SET last_sync_time ='$time',hw_fw_version='$hw_fw_version'  WHERE onos_key ='$key' ");



$result = $db->query("select * from sync_messages ");  
$cmd_list=array();
while ($row = $result->fetchArray()){
  $cmd=test_input($row['cmd_message']);
  array_push($cmd_list,$cmd);
  #echo "#_cmd_".$cmd."_cmd_#";
}

$json_cmd_list=json_encode($cmd_list);

echo "#_cmd_".$json_cmd_list."_cmd_#";

#$result = $db->query("select cmd_message from sync_messages WHERE cmd_id IN (SELECT cmd_id FROM sync_messages ORDER BY cmd_id ASC LIMIT 1)");   #get first row (older row)

#$row = $result->fetchArray();

#$cmd_message=test_input($row['cmd_message']);
#echo "first_cmd_message:".$cmd_message."cmd_end";

$db->exec("DELETE FROM sync_messages");#clear the table 
#$db->exec( "DELETE FROM sync_messages WHERE cmd_id IN (SELECT cmd_id FROM sync_messages ORDER BY cmd_id ASC LIMIT 1)");  #delete the row just downloaded


$db->close();






?>
