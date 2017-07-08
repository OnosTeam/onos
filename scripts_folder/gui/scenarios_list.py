# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

advanced_settings=0
if current_username!="nobody":
  #print(usersDict[current_username])
  print("current_username="+current_username)
  if "advanced_settings" in usersDict[current_username].keys():  
    advanced_settings= usersDict[current_username]["advanced_settings"] # get data from dict passed from webserbver.py


scenarios_name_comparison='(mystring=="TYPE NEW SCENARIO NAME")||(mystring=="")'
#for scenario in scenarioDict:
#  scenarios_name_comparison=scenarios_name_comparison+'||(mystring=="'+scenario+'")'

scenario_list=[]
for scenario in scenarioDict :
  scenario_list.append(scenario)
  scenarios_name_comparison=scenarios_name_comparison+'||(mystring=="'+scenario+'")'




part_to_insert_in_head='''
<link rel="stylesheet" href="../css/scenario_list.css">

<script type="text/javascript">

var scenarioArray = [[#_array_part_to_replace_#]];



function delete_check_box_show1(){

alert("ok");

  var cols = document.getElementsByClassName('delete_box');
  for(i=0; i<cols.length; i++) {
    cols[i].style.display = 'inherit';
  }

  var cols = document.getElementsByClassName('impostazioni-link');
  for(i=0; i<cols.length; i++) {
    cols[i].style.display = 'none';
  }



}

function delete_check_box_hide(){

  var cols = document.getElementsByClassName('delete_box');
  for(i=0; i<cols.length; i++) {
    cols[i].style.display = 'none';

  }


  var cols = document.getElementsByClassName('impostazioni-link');
  for(i=0; i<cols.length; i++) {
    cols[i].style.display = 'inherit';
  }

}


function delete_dialog() { 

var arrayLength = scenarioArray.length;
for (var i = 0; i < arrayLength; i++) {
    if (document.getElementById(scenarioArray[i]).checked){  // if this checkbox is checked
   //   alert(scenarioArray[i]);


      delete_check_box_hide();

      var r = confirm("are you sure to delete the Scenario?"+scenarioArray[i]);
      if (r == true) {
        document.getElementById("delete_scenario").value= scenarioArray[i];

      }
      else{
        document.getElementById(scenarioArray[i]).checked=false;
      }

    }

}
document.getElementById("delete_form").submit();


}


</script>

'''



menu=getTopMenu(part_to_insert_in_head)

menu=menu.replace("right_menu_add_link_to_replace","/scenario_creation/")  # replace the link in the + of the right menu


html=menu


javascript_array_part=''




html=html+'''

 
<form name="delete_form" action="" method="POST" id="delete_form" onsubmit="">
<input type="hidden" name="delete_scenario" id="delete_scenario" value="x"> 

'''


scenario_list.sort()

if advanced_settings==1:
  html=html+"advanced_settings=1"

for scenario in scenario_list :

  javascript_array_part=javascript_array_part+'''"delete_check_'''+scenario+'''",''' #create the contents of the array with all the scenario names


  html=html+'''
		<div class="riga" >
			<a href="/scenario_toggle/'''+scenario+'''/"><div class="scenario_name col1">'''+scenario+'''</div></a>
			<a href="/mod_scenario/'''+scenario+'''/"><div class="impostazioni-link col2"><i class="icon-wrench"></i></div></a>
            <input class ="delete_box col2" type="checkbox" id="delete_check_'''+scenario+'''"  name="delete_check_'''+scenario+'''">
		</div>
'''

if len(scenario_list)==0:
  html=html+'''<div id="no_scenarios">No scenario present</div> '''




end_html='''</form> <div id="footer"></div>	</div> </body></html> '''


javascript_array_part=javascript_array_part[0:-1]  #delete the final ","  from the data

html=html.replace("[#_array_part_to_replace_#]",javascript_array_part)  # inject the array data inside the html


web_page=html+end_html















