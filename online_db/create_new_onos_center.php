<html>
<body>


<?php
ini_set('display_errors', 'On');
error_reporting(E_ALL | E_STRICT);
$db_folder=realpath('./').'/users_db/';


function test_input($data) {
  $data=rtrim($data);
  $data = trim($data);
  $data = stripslashes($data);
  $data = htmlspecialchars($data);
  return $data;
}


$key = "the post key is void";
$pass = "the post data is void";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
  echo "post data <br>";

  if (empty($_POST["onos_key"])) {
    $key = "the post key is void";
  } 
  else {
    $key = test_input($_POST["onos_key"]);
  }


  if (empty($_POST["pass"])) {
    $pass = "the post data is void";
  } 
  else {
    $pass = test_input($_POST["pass"]);
  }



  if (empty($_POST["hw_fw_version"])) {
    $hw_fw_version = "the post hw_fw_version is void";
  } 
  else {
    $hw_fw_version = test_input($_POST["onos_key"]);
    echo "ok";
  }


}
echo "key".$key."<br>";


if (!file_exists($db_folder)) {
mkdir($db_folder);
}

$user_db_file=$db_folder.".db_users_account";
if (!file_exists($user_db_file)) {

  $db = new SQLite3($user_db_file);
  $db->exec("CREATE TABLE onos_user (onos_username VARCHAR(40) PRIMARY KEY,user_password VARCHAR(40),onos_db TEXT )" );
  $db->close();

  echo "the db file:".$user_db_file."didn't exist , I created it <br>";
}



$user_folder_prefix=".dir";

$user_folder=$db_folder.$user_folder_prefix.$key."/";



if (!file_exists($user_folder)) {
mkdir($user_folder);
}




$dbFile = $user_folder.'.db_onos_'.$key ;

#echo $dbFile;
#echo "<br>";
#echo "key:".$key."end<br>";
#echo "pass:".$pass."end<br>";



if(file_exists($dbFile)){


  echo "#_error the db $dbFile already exist " ;
  
  //die($sqliteError) ;

}
else{

$db = new SQLite3($dbFile);

$db->exec("CREATE TABLE if not exists onos_sys (onos_key TEXT PRIMARY KEY,onos_password VARCHAR(40),hw_fw_version TEXT,last_sync_time VARCHAR(16))" );

$db->exec("INSERT INTO onos_sys (onos_key,onos_password,hw_fw_version,last_sync_time ) VALUES ('$key','$pass','$hw_fw_version','00:00:00')");

$db->exec("CREATE TABLE if not exists zones (zone_name VARCHAR(40) PRIMARY KEY,zone_objects TEXT,zone_order INTEGER , zone_owner VARCHAR(40) ,zone_permissions VARCHAR(16) )");

$db->exec("CREATE TABLE if not exists web_objects (obj_name VARCHAR(40) PRIMARY KEY,obj_status TEXT,obj_style TEXT , obj_html TEXT ,obj_type VARCHAR(40),obj_permission VARCHAR(16),obj_group  VARCHAR(40),obj_priority INTEGER  )" );


$db->exec( "CREATE TABLE if not exists changed_remote_status_dict(changed_remote_status_dict_id INTEGER PRIMARY KEY,remote_status_dict TEXT)");


$db->exec("CREATE TABLE if not exists sync_messages (cmd_id INTEGER PRIMARY KEY,cmd_message TEXT)");

$db->close();

echo '<a href="new_onos_user_form.html">create_new_onos_user </a>';


}








?>



</body>
</html>
