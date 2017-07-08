# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

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

part_to_insert_in_head='''
	<link rel="stylesheet" href="../../css/mod_scenario.css">


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

'''


slashes="../../"
html=getTopMenu(part_to_insert_in_head,slashes)

html=html+'''

<div id="nomescenario">
	<div class="testo">'''+scenario_to_mod+'''</div>
</div>
<div class="infotext">
	<div class="testo">Qui puoi modificare le impostazioni relative allo scenario</div>
</div>


<form action="" method="POST" onsubmit="return checkvalue(this)" >
<input type="hidden" name="mod_scenario" value="'''+scenario_to_mod+'''">


<div class="riga_container">
	<div class="riga_name">Nome</div>
		<input type="text" class="textbox" onclick="this.select();" name="new_scenario_name" value="'''+scenario_to_mod+'''">
	<div class="info_box">?</div>
</div>


<div class="riga_container">
	<div class="riga_name">Abilitato</div>
	<input type="checkbox" class="checkbox" name="enabling" '''+sel0+''' >
</div>


<div class="riga_container">
	<div class="riga_name">Tipo</div>
	<select class="select" name="set_type_after_run">'''+sel1+'''</select> 
	<div class="info_box">?</div>
</div>


<div class="riga_container">
	<div class="riga_name">Ritardo</div>
	<input type="text" class="textbox" name="delay_time" value="'''+sel3+'''" class="textbox" onclick="this.select();">
	<div class="info_box">?</div>
</div>



<div class="riga_container">
	<div class="riga_name">Priorit&agrave;</div>
	<select class="select" name="priority">'''+sel2+'''</select>
	<div class="info_box">?</div>
</div>







<div class="riga_container">
	<div class="riga_name">Condizioni</div>
	<input type="text" class="textbox" name="conditions" value="'''+scenarioDict[scenario_to_mod]["conditions"]+'''">
	<div class="info_box">?</div>
</div>




<div class="riga_container">
	<div class="riga_name">Function</div>
	<input type="text" class="textbox" name="functions" value="'''+functionsToRun_html+'''">
	<div class="info_box">?</div>
</div>


<button class="button" type="submit" name="set_conditions_submit" value="condition_submit">Set condition</button>
<button class="button" type="submit" name="set_function_submit" value="functions_to_run">Set Functions to run</button>
<!-- <button class="button" type="button" name="functions_to_run_after_delay" value="">Set After delay function to run </button> -->
<button class="button" type="submit" name="finish_scenario_setup" value="finish_submit">Finish</button>







</form> 




 '''








end_html='''<div id="footer"></div></body></html> '''


web_page=html+end_html




























