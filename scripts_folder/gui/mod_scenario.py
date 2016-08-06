# -*- coding: UTF-8 -*-



scenarios_name_comparison='(mystring=="")'
for scenario in scenarioDict :
  if scenario!=scenario_to_mod: #dont add the current scenario name 
    scenarios_name_comparison=scenarios_name_comparison+'||(mystring=="'+scenario+'")'



functionsToRun_html=""
c=0
for a in scenarioDict[scenario_to_mod]["functionsToRun"]:
  if c==0:
    functionsToRun_html=a
    c=1
  else:
    functionsToRun_html=functionsToRun_html+';;;'+a



sel0=''
if scenarioDict[scenario_to_mod]["enabled"]==0:
  sel0="unchecked"
else:
  sel0="checked"


sel1=''

if scenarioDict[scenario_to_mod]["type_after_run"]=="0":
  sel1='''<option value="0">0</option>
  		  <option value="autodelete">autodelete</option>
  		  <option value="one_time_shot">one time shot</option>'''


elif scenarioDict[scenario_to_mod]["type_after_run"]=="autodelete":
  sel1='''<option value="autodelete">autodelete</option>
          <option value="0">0</option>
  		  <option value="one time shot">one time shot</option>'''

elif scenarioDict[scenario_to_mod]["type_after_run"]=="one_time_shot":
  sel1='''<option value="one time shot">one time shot</option>
          <option value="0">0</option>
          <option value="autodelete">autodelete</option>
          '''
  		  



sel2='''        <option value="0">0</option>
  				<option value="1">1</option>
  				<option value="2">2</option>
  				<option value="3">3</option>
  				<option value="4">4</option>
  				<option value="5">5</option>
  				<option value="6">6</option>
  				<option value="7">7</option>
  				<option value="8">8</option>
  				<option value="9">9</option>
  				<option value="10">10</option>'''

#remove the current priority and add it to the top
sel2=sel2.replace('''<option value="'''+str(scenarioDict[scenario_to_mod]["priority"])+'''">'''+str(scenarioDict[scenario_to_mod]["priority"])+'''</option>''',"")

sel2='''<option value="'''+str(scenarioDict[scenario_to_mod]["priority"])+'''">'''+str(scenarioDict[scenario_to_mod]["priority"])+'''</option>'''+sel2





sel3="0"


try:
  sel3=str(scenarioDict[scenario_to_mod]["delayTime"])
except:
  sel3="0"




html='''
<!-- pezzo standard per header menu e nome pagina -->

<!DOCTYPE html>

<html>

    <head>
	<link rel="stylesheet" href="../../css/mod_scenario.css">
	<meta charset="utf-8">

<script type="text/javascript">
function checkvalue() { 
    var mystring = document.getElementById('new_scenario_name').value; 
    if('''+scenarios_name_comparison+''') {
        alert ('This is not allowed because already used or not valid');
        return false;
    } else {
        //alert("correct input");
        return true;
    }
}
</script>




    </head>
    <body>

	<div id="container-image">
       <img id="image" src="../../img/header.jpg" class="image" />
	</div>




		<div id="container">
			<div id="play"  class="button" ><a href="/"><img class="flex" src="../../img/home.png" class="image" /></a></div>
			<div id="teach" class="button" ><a href="/scenarios_list/"><img class="flex" src="../../img/scenario-ico.png" class="image" /></a></div>
			<div id="setup" class="button" ><a href="/setup/"><img class="flex" src="../../img/setup-ico.gif" class="image" /></a></div>
		</div>



		<div class="divisorio">MOD SCENARIO "'''+scenario_to_mod+'''"</div>


		
		<div id="body2">
<!--fine pezzo standard per header menu e nome pagina -->


<form action="" method="POST" onsubmit="return checkvalue(this)" >
<input type="hidden" name="mod_scenario" value="'''+scenario_to_mod+'''">




<div id="container_a" class="border-container1">
<div   class="testo" >Scenario Name</div>

<input type="text" class="textbox" id="new_scenario_name" onclick="this.select();"    name="new_scenario_name"   value="'''+scenario_to_mod+'''">

</div>


<div id="container_b" class="border-container1">
			<div   class="testo" >Enabled</div>

			<input  type="checkbox" id="enabling" name="enabling" '''+sel0+'''>


</div>







<div id="container_d" class="border-container1">
			<div   class="testo" >Set type after run</div>

			 	<select id="select" name="set_type_after_run" >'''+sel1+'''
				</select> 


</div>

<div id="container_e" class="border-container1">
			<div   class="testo" >Delay time</div>

				<input type="text" name="delay_time" value="'''+sel3+'''" class="textbox" onclick="this.select();"/> 

</div>




<div id="container_f" class="border-container1">
			<div   class="testo" >Priority</div>

			 	<select id="select" name="priority">
  				'''+sel2+'''
				</select> 


</div>


<div id="container_e" class="border-container1">


<div   class="testo" >Conditions</div>

<input type="text" class="textbox" id="Conditions"   name="conditions"   value="'''+scenarioDict[scenario_to_mod]["conditions"]+'''">

</div>



<div id="container_e" class="border-container1">
<div   class="testo" >Functions to run</div>

<input type="text" class="textbox" id="functions"   name="functions"   value="'''+functionsToRun_html+'''">

</div>

<div id="container_condition">


                <button class="submit-button" type="submit" name="set_conditions_submit" value="condition_submit">Set condition</button>




</div>

</div>

<div id="container_set_function">



  				<button class="submit-button" type="submit" name="set_function_submit" value="functions_to_run">Set Functions to run</button>



</div>


<div id="container_i" class="ghost">



  				<button  class="submit-button" type="button" name="functions_to_run_after_delay"   value="">Set After delay function to run </button>



</div>




<div id="container_create" >



  				<button id="sbutton" class="submit-button" type="submit" name="finish_scenario_setup" value="finish_submit">Finish</button>




</div>


</form> 




 '''








end_html='''<div id="footer"></div>	</div> </body></html> '''


web_page=html+end_html




























