<?php

$dbFile = realpath('./').'/.dbtest' ;

/*
IMPORTANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

TO PREVENT DATABASE DOWNLOAD FROM BROWSER put a .htaccess in the site  directory with :

<Files ~ "\.d">
    Order allow,deny
    Deny from all
</Files>

<FilesMatch "\.d">
Deny from all
</FilesMatch>




Then use always .d+name for database starting name files


*/

if(!file_exists($dbFile)){

  $sqliteError= "Error , the database $dbFile does not exist";
  $sqliteError.= '<strong>'.$php_errormsg.'</strong>' ;
  $php_errormsg="" ;
  
  //die($sqliteError) ;

}

//$db->escape($values)

$db = new SQLite3($dbFile);

$db->exec("CREATE TABLE web_objects (obj_name VARCHAR(40) PRIMARY KEY,obj_status TEXT,obj_style TEXT , obj_html TEXT ,obj_type VARCHAR(40),obj_permission VARCHAR(16),obj_group  VARCHAR(40),obj_priority INTEGER  )" );

$user_group=json_encode(array("web_interface","onos_mail_guest"));


$db->exec("INSERT INTO web_objects (obj_name,obj_status,obj_style,obj_html,obj_type,obj_permission,obj_group,obj_priority) VALUES ('obj1','0','background-color:green;','obj1=0','button','777','$user_group',0)");


$db->exec("CREATE TABLE zones (zone_name VARCHAR(40) PRIMARY KEY,zone_objects TEXT,zone_order INTEGER , zone_owner VARCHAR(40) ,zone_permissions VARCHAR(16) )");

$zone_objects=json_encode(array("obj1","obj2","obj3"));

$db->exec("INSERT INTO zones (zone_name,zone_objects,zone_order,zone_owner,zone_permissions) VALUES ('zone0','$zone_objects',0,'web_interface','777')");

$db->exec("CREATE TABLE sync_messages (cmd_id INTEGER PRIMARY KEY,cmd_messages TEXT)");

$cmd_json_list=json_encode(array("cmd1","cmd2","cmd3"));

$db->exec("INSERT INTO sync_messages (cmd_messages) VALUES ('$cmd_json_list')");

//$db->exec();

$db->exec( "CREATE TABLE changed_remote_status_dict(changed_remote_status_dict_id INTEGER PRIMARY KEY,remote_status_dict TEXT)");

$remote_status_json_dict=json_encode(array(obj0 => '0', obj1 => '1',obj2 => '255'));

$db->exec("INSERT INTO changed_remote_status_dict (remote_status_dict) VALUES ('$remote_status_json_dict')");



$query_string="select * from web_objects;";

$result = $db->query('SELECT * FROM web_objects ');

while ($row = $result->fetchArray())
{
$objname=$row['obj_name'];
$objstatus=$row['obj_status'];
$users=$row['obj_group'];
echo "<br>";
echo "objname:".$objname;
echo "<br>";
echo "status:".$objstatus;
echo "<br>";
echo "user_group:".$users;



}






$query_string="select * from zones;";

$result = $db->query($query_string);

while ($row = $result->fetchArray())
{
$objname=$row['zone_name'];
$objstatus=$row['zone_objects'];
echo "<br>";
echo "<br>";
echo "zone_name:".$objname;
echo "<br>";
echo "zone_objs:".$objstatus;

}





$query_string="select * from sync_messages;";

$result = $db->query($query_string);

while ($row = $result->fetchArray())
{
$cmd_id=$row['cmd_id'];
$cmd_messages=$row['cmd_messages'];
echo "<br>";
echo "<br>";
echo "cmd_id:".$cmd_id;
echo "<br>";
echo "cmd_messages:".$cmd_messages;

}




$query_string="select * from changed_remote_status_dict;";

$result = $db->query($query_string);

while ($row = $result->fetchArray())
{
$remote_status_change_list_id=$row['changed_remote_status_dict_id'];
$remote_status_list=$row['remote_status_dict'];
echo "<br>";
echo "<br>";
echo "remote_status_change_list_id:".$remote_status_change_list_id;
echo "<br>";
echo "remote_status_list:".$remote_status_list;

}




$db->exec("DELETE FROM sync_messages WHERE cmd_id>7;");





$db->close();


?>
