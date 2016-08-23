# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

scenarios_name_comparison='(mystring=="TYPE NEW SCENARIO NAME")||(mystring=="")'
#for scenario in scenarioDict:
#  scenarios_name_comparison=scenarios_name_comparison+'||(mystring=="'+scenario+'")'

scenario_list=[]
for scenario in scenarioDict :
  scenario_list.append(scenario)
  scenarios_name_comparison=scenarios_name_comparison+'||(mystring=="'+scenario+'")'



part_to_insert_in_head='''

<link rel="stylesheet" href="../css/scenarios_list.css">

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

function delete_dialog(name) { 

//alert ('are you sure to delete the Scenario? :'+name);

var r = confirm("are you sure to delete the Scenario?"+name);
if (r == true) {
  document.getElementById("delete_scenario").value= name;
  document.getElementById("delete_form").submit();
}





}

</script>

'''



html=getTopMenu(part_to_insert_in_head)




html=html+'''

		<div class="divisorio">LISTA SCENARI</div>


	<div id="body2">
<!--fine pezzo standard per header menu e nome pagina -->

<form action="" method="POST" onsubmit="return checkvalue(this)">

<input type="hidden" name="new_scenario" value="/scenarios_list/">



		<div class="nuovo-container">

            <div class="nuovo-testo" >
            <input type="text" class="textbox" id="new_scenario_name" onclick="this.select();"    name="new_scenario_name"   value="TYPE NEW SCENARIO NAME">
            </div>
            
			<div  >
            <input id="nuovo-image" type="image" src="../img/croce.png" alt="Submit" >

</div>


		</a>
		</div>
</form> 


<form name="delete_form" action="" method="POST" id="delete_form" onsubmit="">
<input type="hidden" name="delete_scenario" id="delete_scenario" value="x"> 
</form>
 '''






scenario_list.sort()

for scenario in scenario_list :

  html=html+'''<div class="scenario-container">
			<div class="scenario"><a href="/mod_scenario/'''+scenario+'''/">'''+scenario+'''</a></div>
			<div class="setup-scenario"><a href="/mod_scenario/'''+scenario+'''/"><img class="flex" src="../img/wrench.png" class="image" /></a></div>
            <button class="delete-button"   value="'''+scenario+'''" onclick='delete_dialog("'''+scenario+'''");'  >DELETE</button> 
		</div>'''



end_html=''' <div id="footer"></div>	</div> </body></html> '''


web_page=html+end_html















