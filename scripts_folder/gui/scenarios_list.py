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



menu=getTopMenu(part_to_insert_in_head)

menu=menu.replace("right_menu_add_link_to_replace","/scenario_creation")  # replace the link in the + of the right menu


html=menu




scenario_list.sort()

if advanced_settings==1:
  html=html+"advanced_settings=1"

for scenario in scenario_list :

  html=html+'''
		<div class="riga" >
			<a href="/scenario_toggle/'''+scenario+'''/"><div class="scenario_name col1">'''+scenario+'''</div></a>
			<a href="/mod_scenario/'''+scenario+'''/"><div class="impostazioni-link col2"><i class="icon-wrench"></i></div></a>
		</div>
'''

if len(scenario_list)==0:
  html=html+'''<div id="no_scenarios">No scenario present</div> '''




end_html=''' <div id="footer"></div>	</div> </body></html> '''


web_page=html+end_html















