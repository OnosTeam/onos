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


  if (empty($_POST["zone_dict"])) {
    $json_zone_dict = "the post zone_dict is void";
  } 
  else {
    $json_zone_dict = $_POST["zone_dict"];
    #echo "zone dict json".$json_zone_dict;
  }


  if (empty($_POST["zone_sync"])) { #tell if the zones have to be overwrited
    $zone_sync = "0";
  } 
  else {
    $zone_sync = $_POST["zone_sync"];

  }

  if (empty($_POST["obj_sync"])) { #tell if the zones have to be overwrited
    $obj_sync = "0";
  } 
  else {
    $obj_sync = $_POST["obj_sync"];

  }

  if (empty($_POST["obj_dict"])) {
    $json_obj_dict = "the post obj_dict is void";
  } 
  else {
    $json_obj_dict = $_POST["obj_dict"];

  }


  if (empty($_POST["single_obj"])) {
    $json_single_obj = "error_post_single_obj_void";
  } 
  else {
    $json_single_obj = $_POST["single_obj"];

  }


}
else{
echo "no post data received";
die;
}


$db_folder=realpath('./').'/users_db/';
$user_folder_prefix=".dir";
$user_folder=$db_folder.$user_folder_prefix.$key."/";
$dbFile = $user_folder.'.db_onos_'.$key ;

if(file_exists($dbFile)){
  $db = new SQLite3($dbFile);
  $query_string="select * from onos_sys where onos_key='$key' ;";
  $result = $db->query($query_string);
  $row = $result->fetchArray();
  $real_password=test_input($row['onos_password']);
  $db->close();
  echo "real_password:".$real_password;
  if (strcmp($form_pass,$real_password) == 0) {  #if the password is ok
    echo "onos_password_ok";


    if ($zone_sync=="1"){
    #  echo "zone_sync sync:1";
      $db = new SQLite3($dbFile);
      #$db->exec("CREATE TABLE if not exists zones (zone_name VARCHAR(40) PRIMARY KEY,zone_objects TEXT,zone_order INTEGER , zone_owner VARCHAR(40) ,zone_permissions VARCHAR(16) )");
      $db->exec("DELETE FROM zones");#clear the table 
      $db->close();
      $zone_dict=json_decode($json_zone_dict,true);
    #  echo $zone_dict["$zone_name"];
      $db = new SQLite3($dbFile);
      $db->exec("BEGIN TRANSACTION;"); 
      foreach ($zone_dict as $zone_name=>$val){
      #  echo $zone_name.' <br>';
       # echo 'val:'.$zone_dict["$zone_name"]["zone_objects"].'<br>';
        $zone_objects=$zone_dict["$zone_name"]["objects"];
        $json_zone_objects=json_encode($zone_objects);
        #echo "zone_objects".$zone_objects;
        $zone_order=$zone_dict["$zone_name"]["order"];
        #echo "zone_order".$zone_order;
        $zone_owner=$zone_dict["$zone_name"]["owner"];
        $zone_permissions=$zone_dict["$zone_name"]["permissions"];


        $db->exec("insert or replace INTO zones (zone_name,zone_objects,zone_order,zone_owner,zone_permissions) VALUES ('$zone_name','$json_zone_objects',$zone_order,'$zone_owner','$zone_permissions')");

      }#  foreach end
      $db->exec("COMMIT TRANSACTION;"); 
      $db->close(); 




    }#end if ($zone_sync=="1")
    else{
      echo "zone_sync is not 1";
    }


    if ($obj_sync=="all"){  #update all objects 
      $db = new SQLite3($dbFile);
      #$db->exec("CREATE TABLE if not exists web_objects (obj_name VARCHAR(40) PRIMARY KEY,obj_status TEXT,obj_style TEXT , obj_html TEXT ,obj_type VARCHAR(40),obj_permission VARCHAR(16),obj_group  VARCHAR(40),obj_priority INTEGER  )" );

      $db->exec("DELETE FROM web_objects"); #clear the table 



      $db->exec("BEGIN TRANSACTION;"); 
      #echo "json_obj_dict:::::::".$json_obj_dict;
      $obj_dict=json_decode($json_obj_dict,true);

      foreach ($obj_dict as $obj_name=>$val){
        #$obj_name=$obj_dict["objname"];
        echo "obj_name:".$obj_name;
        $obj_status=addslashes($obj_dict["$obj_name"]["obj_status"]);


        if ($obj_status=="1") {   #banana  only 0 and 1 status accepted

          $obj_style=addslashes($obj_dict["$obj_name"]["obj_style1"]);
          $obj_html=addslashes($obj_dict["$obj_name"]["obj_html1"]);
        }
        else{
          $obj_style=addslashes($obj_dict["$obj_name"]["obj_style0"]);
          $obj_html=addslashes($obj_dict["$obj_name"]["obj_html0"]);          
        }


        $obj_type=addslashes($obj_dict["$obj_name"]["obj_type"]);   #banana obj_type will be used to make a different html in the page
        $obj_permission=addslashes($obj_dict["$obj_name"]["obj_permission"]);
        $obj_json_group=addslashes($obj_dict["$obj_name"]["obj_group"]);
        $obj_priority=addslashes($obj_dict["$obj_name"]["obj_priority"]);

    

        #echo "starttttttttttt:".$obj_status.$obj_style.$obj_html.$obj_type.$obj_permission.$obj_json_group.$obj_priority."endddddddddddd";

        $db->exec("insert or replace INTO web_objects (obj_name,obj_status,obj_style,obj_html,obj_type,obj_permission,obj_group,obj_priority) VALUES ('$obj_name','$obj_status','$obj_style','$obj_html','$obj_type','$obj_permission','$obj_json_group','$obj_priority')");


      }#  foreach end
      $db->exec("COMMIT TRANSACTION;"); 
      $db->close();

    }


    if ($obj_sync=="single"){   # update only one object

      if ($json_single_obj=="error_post_single_obj_void"){
        echo "error_post_single_obj_void ";
        die;
      }
      $db = new SQLite3($dbFile);
      #$db->exec("CREATE TABLE if not exists web_objects (obj_name VARCHAR(40) PRIMARY KEY,obj_status TEXT,obj_style TEXT , obj_html TEXT ,obj_type VARCHAR(40),obj_permission VARCHAR(16),obj_group  VARCHAR(40),obj_priority INTEGER  )" );

      $obj_dict=json_decode($json_single_obj,true);
      $obj_name=$obj_dict["objname"];
      $obj_status=$obj_dict["obj_status"];
      $obj_style=$obj_dict["obj_style"];
      $obj_html=$obj_dict["obj_html"];
      $obj_type=$obj_dict["obj_type"];
      $obj_permission=$obj_dict["obj_permission"];
      $obj_json_group=$obj_dict["obj_group"];
      $obj_priority=$obj_dict["obj_priority"];

      $db->exec("insert or replace INTO web_objects (obj_name,obj_status,obj_style,obj_html,obj_type,obj_permission,obj_group,obj_priority) VALUES ('$obj_name','$obj_status','$obj_style','$obj_html','$obj_type','$obj_permission','$obj_json_group','$obj_priority')");

      $db->close();

    }







  }
  else{
    echo "#_error_wrong_onos_password ";
    die;
}





}
else{
  echo "#_error the db $dbFile does not exist " ;

}


#echo "good";
echo "<br>";
echo $username;
echo "<br>";
echo $form_pass;
echo "<br>";
echo $key;
echo "<br>";






?> 
