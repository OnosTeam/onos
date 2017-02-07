<html>
<body>


<?php
ini_set('display_errors', 'On');
$db_folder=realpath('./').'/users_db/';


function test_input($data) {
  $data=rtrim($data);
  $data = trim($data);
  $data = stripslashes($data);
  $data = htmlspecialchars($data);
  return $data;
}


$username = "the post data is void";
$key = "the post key is void";
$pass = "the post data is void";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
  echo "post data <br>";


  if (empty($_POST["username"])) {
    $username = "the post data is void";
  } 
  else {
    $username = test_input($_POST["username"]);
  }


  if (empty($_POST["onos_key"])) {
    $key = "the post key is void";
  } 
  else {
    $key = test_input($_POST["onos_key"]);
  }


  if (empty($_POST["user_pass"])) {
    $user_pass = "the post data is void";
  } 
  else {
    $user_pass = test_input($_POST["user_pass"]);
  }


  if (empty($_POST["onos_password"])) {
    $onos_password = "the post data is void";
  } 
  else {
    $onos_password = test_input($_POST["onos_password"]);
  }


}
echo "username".$username."<br>";



$db_folder=realpath('./').'/users_db/';
$user_folder_prefix=".dir";
$user_folder=$db_folder.$user_folder_prefix.$key."/";
$dbFile = $user_folder.'.db_onos_'.$key ;


$db_account = $db_folder.'.db_users_account' ;
echo $dbFile;
#echo "<br>";
#echo "username:".$username."end<br>";
#echo "user_pass:".$user_pass."end<br>";
#echo "key:".$key."end<br>";
#echo "onos_pass:".$onos_password."end<br>";


if(file_exists($dbFile)){


##part used by the onoscenter to check if there is already the username..
  $db_user_File = $db_folder.'.db_users_account' ;
  $db = new SQLite3($db_user_File);
  $db->exec("CREATE TABLE if not exists onos_user (onos_username VARCHAR(40) PRIMARY KEY,user_password VARCHAR(40),onos_db TEXT )" );
  $query_string="select * from onos_user where onos_username='$username' ;";
  $result = $db->query($query_string);
  $row = $result->fetchArray();
  $real_password=test_input($row['user_password']);
  $db->close();
  if (   (strlen($real_password))!=0){  # if the password len is >0 then the row is NOT empty then the username already exist
    echo "the_username_already_exist";
    #include('login_error_page.php');
    #header("location: login_error.html"); 
    die();

  }







  $db = new SQLite3($dbFile);

  $query_string="select * from onos_sys where onos_key='$key' ;";
  $result = $db->query($query_string);
  $row = $result->fetchArray();
  $real_password=test_input($row['onos_password']);
  $db->close();

  #banana there is no check if the username already exist

  if (strcmp($onos_password,$real_password) == 0) {  #if the password is ok
    echo "onos password ok";
    $db = new SQLite3($db_account); #create the db account file
    $db->exec("CREATE TABLE if not exists onos_user (onos_username VARCHAR(40) PRIMARY KEY,user_password VARCHAR(40),onos_db TEXT )" );
    $db->exec("insert or replace INTO onos_user (onos_username,user_password,onos_db) VALUES ('$username','$user_pass','$dbFile')");
    $db->close();
    echo "#_onos_online_user_created";

  }
  else{
    echo "#_error wrong onos password ";

}

}
else{

  echo "#_error the db $dbFile does not exist " ;
  
  //die($sqliteError) ;



}








?>



</body>
</html>
