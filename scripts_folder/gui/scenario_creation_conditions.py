# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

advanced_settings=0

logprint("gui scenario_creation_condition executed with path:"+path)
if current_username!="nobody":
  #print(usersDict[current_username])
  print("current_username="+current_username)
  if "advanced_settings" in usersDict[current_username].keys():  
    advanced_settings= usersDict[current_username]["advanced_settings"] # get data from dict passed from webserbver.py


 # scenario_to_mod is passed from namespace in webserver.py
 # paths passed from namespace in webserver.py


if path.find("scenario_conditions")!=-1:
  #this will understand if is a new scenario being created or if is a old scenario being modifyed and then make the links in the buttons act according to that

  logprint("mod_condition_found")
  add_button_link="condition_mod_add_submit"
  finish_button_link="finish_conditions_setup"
else:
  logprint("goto_operations_found")
  add_button_link="condition_add_submit"
  finish_button_link="goto_operations"








part_to_insert_in_head='''
	<link rel="stylesheet" href="/css/scenario_creation.css">
	<meta charset="utf-8">
   	<title>Creazione Scenario</title>

<script type="text/javascript">

function checkToEnableNumericForm(text_id,select_id){
  //alert(document.getElementById(select_id).value);
  if ( document.getElementById(select_id).value=="variabile_numerica" ){
  //  alert("a");
    document.getElementById(text_id).disabled = false;
  }
  else{
  //  alert("b");
    document.getElementById(text_id).disabled = true;
  }

}

</script>


'''


slashes="../../"
menu=getTopMenu(part_to_insert_in_head,slashes)



html=menu


html_object_list_drop_menu=""

system_object_list=[""]

obj_sel='''<option value="variabile_numerica">variabile_numerica</option>'''


obj_list=objectDict.keys()
obj_list.sort()

for object_name in obj_list:# for every object in the list make the html
  if (objectDict[object_name].getType()=="cfg_obj") : #don't display cfg objects in the scenarios
    continue
  if object_name.endswith("_body"):
    continue


  html_object_list_drop_menu=html_object_list_drop_menu+'''<option value="'''+object_name+'''">'''+object_name+'''</option>'''
  obj_sel=obj_sel+'''<option value="'''+object_name+'''">'''+object_name+'''</option>
      '''


html_object_list_drop_menu='''<option value="1">ON</option>'''+html_object_list_drop_menu
html_object_list_drop_menu='''<option value="0">OFF</option>'''+html_object_list_drop_menu
html_object_list_drop_menu='''<option value="">variabile_numerica</option>'''+html_object_list_drop_menu

initial__obj_sel_dx='''<option value="1">ON</option>
                       <option value="0">OFF</option>
                       <option value="">numeric_value</option>
                       '''




default_obj_sel_sx='''<option>select_an_element</option>'''+obj_sel
default_obj_sel_dx='''<option>select_an_element</option>'''+obj_sel



conditions_rows=""


conditions_string=scenarioDict[scenario_to_mod]["conditions"]  #get the string where there are the conditions

#list_of_single_conditions=conditions_string.split("&")  #each condition is separed by &












try:

  if ("|" not in conditions_string ):  # if the users has not modified by hand the conditions..


    list_of_single_conditions=conditions_string.split("&")
    i=0       
    logprint("list_of_single_conditions:"+str(list_of_single_conditions))
    for c in list_of_single_conditions: # for each condition
      c=c.replace('#_','')
      c=c.replace('_#','')
      c=c.replace('(','')
      c=c.replace(')','')

      obj_sel_sx=obj_sel
      obj_sel_dx=obj_sel
   
      operator=0
      if "==" in c:
        operator="=="
      elif "!=" in c:
        operator="!="
      elif ">" in c:
        operator=">"
      elif "<" in c:
        operator="<"
      if operator !=0:
        left_element=c.split(operator)[0]   #get the left element so from  (#_year_#==2016)   gets "#_year_#"
        right_element=c.split(operator)[1]  #get the right element so from  (#_year_#==2016)   gets "2016"
        logprint("left_element:"+left_element)
        logprint("right_element:"+right_element)
        i=i+1 

        obj_sel_sx=obj_sel_sx.replace('(',' ')

        obj_sel_sx=obj_sel_sx.replace('''<option>'''+str(left_element)+'''</option>''',' ')
        obj_sel_sx='''<option>'''+str(left_element)+'''</option>'''+obj_sel_sx


 
        obj_sel_dx=obj_sel_dx.replace('''<option>'''+str(right_element)+'''</option>''',' ')
        obj_sel_dx='''<option>'''+str(right_element)+'''</option>'''+obj_sel_dx



        operator_sel='''
      					<option>=</option>
      					<option>></option>
      					<option><</option>
                        <option>!=</option>  '''

      #replace the selected option and put it on the first line
        operator_sel=operator_sel.replace('<option>'+operator+'</option>',' ')   
        operator_sel='<option>'+operator+'</option>'+operator_sel

                   
        conditions_rows=conditions_rows+'''

		<div class="riga_container">

				<select class="select1" name="select_l'''+str(i)+'''">
 
                 '''+obj_sel_sx+'''
                </select>


			<select id="compara" name="select_op'''+str(i)+'''" >
                    '''+operator_sel+'''
			</select>
          <input  disabled class="textarea"  id="textarea_'''+str(i)+'''" type="text" name="numeric_value_field'''+str(i)+'''">
          <select class="listaoggetti" id="select_r'''+str(i)+'''" name="select_r'''+str(i)+'''" onchange="checkToEnableNumericForm('''+"'"+'''textarea_'''+str(i)+"'"+''','''+"'"+'''select_r'''+str(i)+"'"+''')">


 	         '''+obj_sel_dx+'''
          </select>
		</div>

  '''
  menu_number=str(i)



  added_condition_row='''

		<div class="riga_container">
			<div  class="nometesto">  
        	    <select  id="select_new_sx" name="select_new_l" > 
                '''+default_obj_sel_sx+'''
            	</select>
            </div>


			<select id="compara" name="select_new_o">
                    '''+operator_sel+'''
  			</select>
			<input disabled id="textarea" type="text" name="numeric_value_field">
			<select class="listaoggetti" id="select_new_r" name="select_new_r">
				'''+default_obj_sel_dx+'''
          	</select>
		</div>

  '''
  #conditions_rows=conditions_rows+added_condition_row  # add an empty row..


except Exception as e  :
  message="error0 in scenario_creation_conditions "
  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  







#        <form action="" method="POST" onsubmit="return checkvalue(this)">

#        <input type="hidden" name="scenario_creation_conditions" value="'''+scenario_to_mod+'''">


html=html+'''

        <form id="main_form" name="main_form" action="" method="post"  >
        <input type="hidden" name="mod_conditions" value="'''+scenario_to_mod+'''">
        <input type="hidden" name="menu_number" value="'''+menu_number+'''">
        <input type="hidden" name="scenario_creation_conditions" value="'''+scenario_to_mod+'''">




		<div id="nomescenario">
				<div class="testo">'''+scenario_to_mod+'''</div>
		</div>



		<div class="infotext">
			<div class="testo">Imposta ora le condizioni che ATTIVERANNO lo scenario.
          	ATTENZIONE! Impostando piu' di una condizione
         	ogniuna di esse dovra' verificarsi per attivare lo scenario</div>
		</div>


        '''+conditions_rows+'''

         <!--this button is hidden and will be pressed only when the user press enter key on a input form, will so reload the page saving the data  -->
         <button id="hidden_button" style="position: absolute;top: -1000px;" class="submit_button" type="submit" name="save_and_reload_this_page" value="'''+path+'''">HiddenSubmit</button> 

         <button class="submit_button" type="submit"  value="Aggiungi condizione" name="'''+add_button_link+'''" >Aggiungi condizione</button> 

         <button class="submit_button" type="submit"  value="invia" name="'''+finish_button_link+'''" >Salva</button> 


         </form>



'''









end_html='''<div id="footer"></div> </body></html> '''


web_page=html+end_html




























