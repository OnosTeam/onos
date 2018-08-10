<?php

session_start();

#echo "session OK";
#echo "<br>";






$user=$_SESSION["username"];

$dbFile=$_SESSION["dbFile"];

if(   ( !isset($_SESSION['dbFile'])) |(!isset($_SESSION['username']) ) ){
  header("location:index.html"); //to redirect back to "index.php" after logging out
  die( );
}

$_SESSION["prev_url"]=$_SERVER['REQUEST_URI'];


#echo $user;
//print_r($_SESSION);
#echo "<br>";
#echo $db_file;
#echo "<br>";



if(!file_exists($dbFile)){

  $sqliteError= "Error , the database $dbFile does not exist";
  $sqliteError.= '<strong>'.$php_errormsg.'</strong>' ;
  $php_errormsg="" ;
  
  die() ;

}

$db = new SQLite3($dbFile);


$query_string="select * from zones;";

$result = $db->query($query_string);

$start_html='<!DOCTYPE html>

<html>

    <head>
	<link rel="stylesheet" href="css/play.css">
	<meta charset="utf-8">

    </head>
    <body>

	<div id="container-image">
       <img id="image" src="img/header.jpg" class="image" />
	</div>

		<div id="container">
			<div id="play"  class="button" ><a href="#"><img class="flex" src="img/play-ico.png" class="image" /></a></div>
			<div id="teach" class="button" ><a href="#"><img class="flex" src="img/scenario-ico.png" class="image" /></a></div>
			<div id="setup" class="button" ><a href="#"><img class="flex" src="img/setup-ico.gif" class="image" /></a></div>

<div id="exit" class="button" > <a href="logout.php">Log Out</a>  </div>
		</div>


    <div class="divisorio">LISTA ZONE</div>

';



echo $start_html;




while ($row = $result->fetchArray()){
  $zone_name=$row['zone_name'];
  $objlist=$row['zone_objects'];
  
  echo "<br>";
  echo "<br>";
  echo '<div class="zona-container">
			<div class="zona"><a href="list_zone_object.php?z='.$zone_name.'">'.$zone_name.'</a></div>
		</div>';
  echo "<br>";




}


#$result = $db->query("select * from web_objects;");

#while ($row = $result->fetchArray())
#{
#$obj_name=$row['obj_name'];
#$obj_status=$row['obj_status'];
#echo "<br>";
#echo "<br>";
#echo "obj_name:".$obj_name;
#echo "<br>";
#echo "obj_status:".$obj_status;

#}

$db->close();

echo "<br>";
echo "<br>";


echo '<div id="footer"></div>
    </body>
</html>';


?>
