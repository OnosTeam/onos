# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

advanced_settings=0
if current_username!="nobody":
  #print(usersDict[current_username])
  print("current_username="+current_username)
  if "advanced_settings" in usersDict[current_username].keys():  
    advanced_settings= usersDict[current_username]["advanced_settings"] # get data from dict passed from webserbver.py



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
	<link rel="stylesheet" href="css/scenario_creation.css">
	<meta charset="utf-8">
   	<title>Creazione Scenario</title>

'''


slashes="../../"
menu=getTopMenu(part_to_insert_in_head,slashes)




html=menu



html=html+'''
		<div class="riga" >
			<input class="name_text" type="text" onfocus="if(this.value == 'Scrivi il nome dello scenario') { this.value = ''; }" value="Scrivi il nome dello scenario"/>
		</div>
	

		
		<div class="infotext">
				<div class="testo">Seleziona UNO o PIU' oggetti o variabili</div>
		</div>


		<div class="multiselect_button">Libreria <i class="icon-book"></i></div>
		

		<div class="multiselect">
            <ul>
                <li>
                    <input type="checkbox" value="luce_1" />luce_1</li>
                <li>
                    <input type="checkbox" value="sensore_1" />sensore_1</li>
                <li>
                    <input type="checkbox" value="luce_2" />luce_2</li>
                <li>
                    <input type="checkbox" value="luce_3" />luce_3</li>
                <li>
                    <input type="checkbox" value="pompa" />pompa</li>
                <li>
                    <input type="checkbox" value="Nokia" />contatore persone (variabile)</li>
                <li>
                    <input type="checkbox" value="luce_1" />luce_1</li>
                <li>
                    <input type="checkbox" value="sensore_1" />sensore_1</li>
                <li>
                    <input type="checkbox" value="luce_2" />luce_2</li>
                <li>
                    <input type="checkbox" value="luce_3" />luce_3</li>
                <li>
                    <input type="checkbox" value="pompa" />pompa</li>
                <li>
                    <input type="checkbox" value="Nokia" />contatore persone (variabile)</li>
            </ul>
        </div>



		<div id="avanti_button">AVANTI</div>
 '''







end_html='''<div id="footer"></div>	</div> </body></html> '''


web_page=html+end_html




























