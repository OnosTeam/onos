# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

advanced_settings=0
if current_username!="nobody":
  #print(usersDict[current_username])
  print("current_username="+current_username)
  if "advanced_settings" in usersDict[current_username].keys():  
    advanced_settings= usersDict[current_username]["advanced_settings"] # get data from dict passed from webserbver.py



scenarios_name_comparison='(mystring=="TYPE NEW SCENARIO NAME")||(mystring=="")'
for scenario in scenarioDict :
  scenarios_name_comparison=scenarios_name_comparison+'||(mystring=="'+scenario+'")'



default_phrase_new_scenario="Scrivi il nome dello scenario"
scenarios_name_comparison=scenarios_name_comparison+'||(mystring.search("'+default_phrase_new_scenario+'" )!=-1)'  # add the default phrase to the black list


javascript_scenario_name_check='''

<script type="text/javascript">
function checkvalue() { 
    var mystring = document.getElementById('new_scenario_name').value; 
    if('''+scenarios_name_comparison+''') {
        alert ('Nome Scenario invalido o usato, inserisci un nome diverso');
        return false;
    } else {
        //alert("correct input");
        return true;
    }
}


</script>

'''








part_to_insert_in_head='''
	<link rel="stylesheet" href="/css/scenario_creation.css">
	<meta charset="utf-8">
   	<title>Creazione Scenario</title>

'''


slashes="../../"
menu=getTopMenu(part_to_insert_in_head,slashes)


menu=menu.replace("<!--Javascript_to_replace-->",javascript_scenario_name_check) # replace <!--Javascript_to_replace--> with javascript code

html=menu


html_object_list=""



system_object_list=[""]
for object_name in objectDict.keys():# for every object in the dictionary make the html
  if (objectDict[object_name].getType()=="cfg_obj") : #don't display cfg objects in the scenarios
    continue

  html_object_list=html_object_list+'''<li>
                    <input type="checkbox" name="'''+object_name+"_checkbox"+'''" value="'''+object_name+"_checkbox"+'''" />'''+object_name+'''</li>'''





html=html+'''

       
        <form action="" method="POST" onsubmit="return checkvalue(this)">

        <input type="hidden" name="scenario_creation" value="/scenario_creation/">

		<div class="riga" >
			<input class="name_text" name="new_scenario_name" id="new_scenario_name" type="text" onclick="if(this.value == '	'''+default_phrase_new_scenario+''' '){ this.value = ''; }" value=' '''+default_phrase_new_scenario+''' '/>
		</div>
	

		
		<div class="infotext">
				<div class="testo">Seleziona UNO o PIU' oggetti o variabili</div>
		</div>


		<div class="multiselect_button">Libreria <i class="icon-book"></i></div>
		

		<div class="multiselect">
            <ul>
            '''+html_object_list+'''  
            </ul>
        </div>



		 <div id="avanti_button"><input type="submit" value="Conferma"> </div>

         </form>
 '''







end_html='''<div id="footer"></div> </body></html> '''


web_page=html+end_html




























