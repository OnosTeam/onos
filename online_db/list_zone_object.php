<?php

session_start();
$user=$_SESSION["username"];
$dbFile=$_SESSION["dbFile"];
$previous_url=$_SESSION["prev_url"];

if(   ( !isset($_SESSION['dbFile'])) |(!isset($_SESSION['username']) ) ){
    header("location:index.html"); //to redirect back to "index.php" after logging out
    die( );
}


header('Cache-Control: max-age=60');

$update_page='

<script type="text/javascript" language="javascript">

var stop_update=0;


function stopUpdate(){
stop_update=1;
}

function startUpdatePag(){


setTimeout("updatePag()",450);

}
function restartUpdate(){
stop_update=0;
}



function updatePag(){

if (stop_update==1){
setTimeout("updatePag()",1050);
return;
}

var xmlHttp;
//var oldHtml=" ";
	try{	
		xmlHttp=new XMLHttpRequest();// Firefox, Opera 8.0+, Safari
	}
	catch (e){
		try{
			xmlHttp=new ActiveXObject("Msxml2.XMLHTTP"); // Internet Explorer
		}
		catch (e){
		    try{
				xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
			}
			catch (e){
				alert("No AJAX!?");
				return false;
			}
		}
	}

xmlHttp.onreadystatechange=function(){

	if(xmlHttp.readyState==4){

        var newtext=xmlHttp.responseText ;
    
        //var n = newtext.search("<!--start_updated_page-->");
        //alert(n);
        //var updated_page=newtext.substring(912);
                     
		document.getElementById("ReloadThis").innerHTML=newtext;

        setTimeout("updatePag()",1050);


       
 
	}
}

xmlHttp.open("GET",location.href,false);   //false for synchronous connection
xmlHttp.send(null);

}



//window.onload=function(){
//	updatePag()
//}


if(window.attachEvent) {
    window.attachEvent("onload", startUpdatePag);
} 
else {
    if(window.onload) {
        var curronload = window.onload;
        var newonload = function() {
            curronload();
            startUpdatePag();
        };
        window.onload = newonload;
    } else {
        window.onload = startUpdatePag;
    }
}







</script>


';

#<meta http-equiv='Refresh' content='1'>
$start_html= '<!DOCTYPE html><html>
    <head>
	<link rel="stylesheet" href="css/zone.css">
	<meta charset="utf-8">';




$menu_html='	<div id="container-image">
       <img id="image" src="img/header.jpg" class="image" />
	</div>
		<div id="container">
			<div id="play"  class="button" ><a href="list_zones.php"><img class="flex" src="img/play-ico.png" class="image" /></a></div>
			<div id="teach" class="button" ><a href="#"><img class="flex" src="img/scenario-ico.png" class="image" /></a></div>
			<div id="setup" class="button" ><a href="#"><img class="flex" src="img/setup-ico.gif" class="image" /></a></div>
		</div>


';





echo $start_html.$update_page."</head><body>";
echo '<!--start_updated_page-->';
echo '<div id="ReloadThis" >';
echo $menu_html;


//echo "session OK";
//echo "<br>";

//echo $dbFile;
//echo "<br>";

if (isset($_REQUEST['z'])) {
  $zone_name=$_REQUEST['z'];
}
else{
  echo "error no zone name passed in the get method";
  die;
}



echo '<div class="divisorio">'.$zone_name.'</div>';

$db = new SQLite3($dbFile);


$result = $db->query("select last_sync_time from onos_sys ;");

$row = $result->fetchArray();

$db->close();

$last_sync_time=$row['last_sync_time'];   # ("%Y-%m-%d-%H-%M-%S")   # '2015-08-19-09-15-18'



ini_set('date.timezone', 'UTC');
$time = date('Y:m:d:H:i:s', time() - date('Z')); // 
$date=substr($time,0,13);  #2015:08:19:10
$minute=date('i', time() - date('Z'));
$second=date('s', time() - date('Z'));

$last_date=substr($last_sync_time,0,13);
$last_minute=substr($last_sync_time,14,2);
$last_second=substr($last_sync_time,17,2);

if ($date==$last_date){# last sync between onos center and the online server is at least in current hour

  
 
  $seconds_since_last_sync=(intval($minute)*60 + intval($second)   )- (intval($last_minute)*60+intval($last_second) );

 
  if ( $seconds_since_last_sync<20){  
    echo "The Onos Center is connected";

  }
  else{
 
    echo "The Onos Center was connected ".$seconds_since_last_sync." seconds ago";
    
  }

  


}
else {

  echo "O.N.O.S. Center is not connected to this server";
  echo "<br>";
  echo $date;
  echo "<br>";
  echo $last_date;


}




$db = new SQLite3($dbFile);

$result = $db->query("select * from zones where zone_name =='".$zone_name."';");

$row = $result->fetchArray();


$db->close();

$zone_name=$row['zone_name'];

$zone_owner=$row['zone_owner'];

#echo "zone_owner ".$zone_owner;

$zone_permissions=$row['zone_permissions'];






$zone_objects=json_decode($row['zone_objects'],true);
#$zone_objects=$row['zone_objects'];



$db = new SQLite3($dbFile);

#foreach ($zone_objects as $obj_name=>$val){


echo "<br>";
echo "<br>";
foreach ($zone_objects as $i) {
  #echo "i:".$i;
  $obj_name=$i;

  $result = $db->query("select * from web_objects where obj_name =='".$obj_name."';");

  $row = $result->fetchArray();  
  
  $obj_html=$row["obj_html"];

  $obj_style=$row["obj_style"];

  $obj_status=$row["obj_status"];

  $obj_type=$row["obj_type"];

  if ($obj_status=="0"){
    $state_img_src="img/on.png";
    $obj_next_status="1";

  }
  else{
    $state_img_src="img/off.png";
    $obj_next_status="0";
   }

#  echo '<div style="'.$obj_style.'"><a href="change_object_status.php?z='.$zone_name.'&obj='.$obj_name.'&st='.$obj_next_status.'">'.       $obj_html.'</a></div>';

echo '
        <div class="oggetto-container">
			<div class="oggetto" style="'.$obj_style.'"><a href="change_object_status.php?z='.$zone_name.'&obj='.$obj_name.'&st='.$obj_next_status.'" onmousedown="stopUpdate()" onmouseout="restartUpdate()">'.$obj_html.'</a></div>
			<div id="stato-oggetto"><a href="change_object_status.php?z='.$zone_name.'&obj='.$obj_name.'&st='.$obj_next_status.'" onmousedown="stopUpdate()" onmouseout="restartUpdate()"><img class="flex" src="'.$state_img_src.'" class="image" /> </a> </div>
		</div>

';



  echo "<br>";

}

echo "<a href=".$previous_url.">Back</a>";
$db->close();

?>
</div>

</body>
</html>

