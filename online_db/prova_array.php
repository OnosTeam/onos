<?php


$zone0=array("s"=>"22","d"=>"23");
$zone1=array("s"=>"211","de"=>"54");
$zone_dict=array("a"=>$zone0,"b"=>$zone1);



foreach ($zone_dict as $zone_name=>$val){
 echo $zone_name.' <br>';
 echo 'val:'.$zone_dict["$zone_name"]["s"].'<br>';


}


?>
