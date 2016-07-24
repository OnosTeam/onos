<?php

session_start();
$user=$_SESSION["username"];
$dbFile=$_SESSION["dbFile"];


#echo "session OK";
#echo "<br>";

#echo $dbFile;
#echo "<br>";

if (isset($_REQUEST['z'])) {
  $zone_name=$_REQUEST['z'];
}
else{
  echo "error no zone name passed in the get method";
  die;
}

if (isset($_REQUEST['obj'])) {
  $obj_name=$_REQUEST['obj'];
}
else{
  echo "error no obj name passed in the get method";
  die;
}


if (isset($_REQUEST['st'])) {
  $obj_status_to_set=$_REQUEST['st'];
}
else{
  echo "error no obj name passed in the get method";
  die;
}



#modify the database with the new style (grey for waiting) and write to  changed_remote_status_dict  and  sync_messages  tables
#then redirect back to the web object list page

$obj_pending_style="background-color:grey";
$obj_pending_html=$obj_name."=pending";

$db = new SQLite3($dbFile);

$db->exec("UPDATE web_objects SET obj_style ='$obj_pending_style',obj_html='$obj_pending_html'  WHERE obj_name ='$obj_name' ");

#$db->exec("CREATE TABLE if not exists sync_messages (cmd_id INTEGER PRIMARY KEY,cmd_message TEXT)");

$cmd_array=array();

#$cmd_array["cmd"]="online_obj_changed";
#$cmd_array["arguments"]=$obj_name;
#$json_cmd_array=json_encode($cmd_array);

$db->exec("INSERT INTO sync_messages (cmd_message) VALUES ('#_@".$user."#_@obj_ch#_@".$obj_name."#_@".$obj_status_to_set."#_@')");
#use split  #_@ on python side to get a list ...

#$db->exec( "CREATE TABLE if not exists changed_remote_status_dict(changed_remote_status_dict_id INTEGER PRIMARY KEY,remote_status_dict TEXT)");



$result = $db->query("select * from changed_remote_status_dict ;");

$row = $result->fetchArray();

$remote_status=json_decode($row['remote_status_dict'],true);

$remote_status["$obj_name "]=$obj_status_to_set;

$remote_status_json_dict=json_encode($remote_status);

$db->exec("INSERT INTO changed_remote_status_dict (remote_status_dict) VALUES ('$remote_status_json_dict')");

$db->close();








header("location: list_zone_object.php?z=".$zone_name);

?>


</body>
</html>
