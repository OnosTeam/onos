<?php
ini_set('display_errors', 'On');

function test_input($data) {
  $data = trim($data);
  $data=rtrim($data);
  $data = stripslashes($data);
  $data = htmlspecialchars($data);
  return $data;
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {


  if (empty($_POST["username_form"])) {
    $username = "the post data is void";
  } 
  else {
    $username = test_input($_POST["username_form"]);
  }


  if (empty($_POST["password_form"])) {
    $form_pass = "the post data is void";
  } 
  else {
    $form_pass = test_input($_POST["password_form"]);
  }


}
else{

echo "no post data received";
die;
}

$db_folder=realpath('./').'/users_db/';
$dbFile = $db_folder.'.db_users_account' ;

//echo $dbFile;

if(!file_exists($dbFile)){

  echo "error database db_users_account does not exist " ;
 //echo "Error , the database $dbFile does not exist";

  #include('login_error_page.php');
  header("location: login_error.html"); 
  die();
  
  //die($sqliteError) ;

}

$db = new SQLite3($dbFile);
$query_string="select * from onos_user where onos_username='$username' ;";
$result = $db->query($query_string);
$row = $result->fetchArray();
$real_password=test_input($row['user_password']);
$db->close();
if (   (strlen($real_password))==0){  # if the password len is 0 then the row is empty then the username is wrong
  echo "the username is wrong please retry";
  #include('login_error_page.php');
  header("location: login_error.html"); 
  die();

}


if (strcmp($form_pass,$real_password) == 0) {
   //echo "the password is ok";
  $db = new SQLite3($dbFile);
  $query_string="select * from onos_user where onos_username='$username' ;";
  $result = $db->query($query_string);
  $row = $result->fetchArray();
  $onos_db=test_input($row['onos_db']);
  $db->close();

  session_start();
  $_SESSION["username"] = $username;
  $_SESSION["dbFile"] = $onos_db;
  #$_SESSION["dbpass"]=$dbFile;
         
  header("location: list_zones.php");

//now i redirect the user to the right database



}
else{ 
  #echo "the password is wrong please retry";
  #include('login_error.html');
  header("location: login_error.html"); 
  #die();


}











?>

