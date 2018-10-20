# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

advanced_settings=0
if current_username!="nobody":
  #print(usersDict[current_username])
  print("current_username="+current_username)
  if "advanced_settings" in usersDict[current_username].keys():  
    advanced_settings= usersDict[current_username]["advanced_settings"] # get data from dict passed from webserbver.py









obj_name_comparison='(mystring=="select_an_element")||(mystring2=="select_an_element")'


obj_sel=''

obj_list=objectDict.keys()
obj_list.sort()


#obj_sel_number=''
#for n in range(0,25):
#  obj_sel_number=obj_sel_number+'''<option>'''+str(n)+'''</option>'''


for obj in obj_list:
  if obj.endswith("_body"):
    continue
  obj_sel=obj_sel+'''<option>'''+str(obj)+'''</option>
      '''



obj_sel='''<option>0</option><option>1</option><option>variabile_numerica</option>'''+obj_sel


operator2_sel_default='''
      					<option> </option>
      					<option>+</option>
      					<option>-</option>
      					<option>/</option>
      					<option>*</option>
      					<option>%</option>
      					<option>&</option>
      					<option>|</option>
                        <option>===</option>  '''







#example conditions:  (#_year_#==2016)&(#_hours_#==8)&(#_minutes_#==0)
functionsToRun=scenarioDict[scenario_to_mod]["functionsToRun"]  #get the string where there are the functionsToRun
print(type(functionsToRun))
print("functionsToRun:", functionsToRun)
html_functionsToRun=''

i=0
for c in functionsToRun: # for each function
  operator2_sel=operator2_sel_default
  c=c.replace('#_','')
  c=c.replace('_#','')
  c=c.replace('(','')
  c=c.replace(')','')
  #c=c.replace('==','=')

  obj_sel_sx=obj_sel
  obj_sel_dx=obj_sel
  obj_sel_third='<option> </option>'+obj_sel
  
  if  c.find("!=") != -1 :  # detect if the opeartor is '!=' or '='
    operator='!='
  else:
    operator='='
     
#  if "=!" in c:
#    operator='=!'
#  elif "=" in c:
#    operator='=!'

  pos=c.find(operator)
  second_operator=""
  if (pos!=-1): # found an = in the string
    left_element=c.split(operator)[0] #c[0:pos]   #get the left element so from  (#_year_#==2016)   gets "#_year_#"

    if "===" in c:
      second_operator='=='
    elif "+" in c:
      second_operator='+'
    elif "-" in c:
      second_operator='-'
    elif "*" in c:
      second_operator='*'
    elif "/" in c:
      second_operator='/'
    elif "%" in c:
      second_operator='%'
    elif "^" in c:
      second_operator='^'
    elif "&" in c:
      second_operator='&'
    elif "|" in c:
      second_operator='|'


    if (second_operator!="") : #there is a second operator so there is also another element

      right_element=c[pos+1:c.find(second_operator)]  #get the right element so from  (#_year_#==2016)   gets "2016"
      if right_element[0]=='=':
        right_element=right_element[1:]
        
      if right_element[0]=='!':
        right_element=right_element[2:]


      third_element=c[c.find(second_operator)+1:]

      if len(third_element)>0:
        print "third_element",third_element

        obj_sel_third=obj_sel_third.replace('''<option>'''+str(third_element)+'''</option>''',' ')
        obj_sel_third='''<option>'''+str(third_element)+'''</option>'''+obj_sel_third


        #replace the selected option and put it on the first line
        operator2_sel=operator2_sel.replace('<option>'+second_operator+'</option>',' ')   
        operator2_sel='<option>'+second_operator+'</option>'+operator2_sel

    else:
      right_element=c.split(operator)[1]


#    if (right_element[0]=='=')or(right_element[0]=='!'):
#      right_element=right_element[1:]
      if right_element[0]=='=':
        right_element=right_element[1:]
        
      if right_element[0]=='!':
        right_element=right_element[2:]



    i=i+1
    obj_sel_sx=obj_sel_sx.replace('(',' ')

    obj_sel_sx=obj_sel_sx.replace('''<option>'''+str(left_element)+'''</option>''',' ')
    obj_sel_sx='''<option>'''+str(left_element)+'''</option>'''+obj_sel_sx


 
    obj_sel_dx=obj_sel_dx.replace('''<option>'''+str(right_element)+'''</option>''',' ')
    obj_sel_dx='''<option>'''+str(right_element)+'''</option>'''+obj_sel_dx

    operator_sel='''
      					<option>'''+operator+'''</option> 
      					<option>=</option> 
     				    <option>!=</option> 
                         '''


    #replace the selected option and put it on the first line
    #operator_sel=operator_sel.replace('<option>'+operator+'</option>',' ')   
    #operator_sel='<option>'+operator+'</option>'+operator_sel









                   
    html_functionsToRun=html_functionsToRun+'''

<div class="riga_container">

				
			<!--select1 -->
   				<select class="select select_1" id ="select_1"  name="select_l'''+str(i)+'''" >
               '''+obj_sel_sx+'''
   				</select>
			<!--fine select 1 -->

			<!--select2 -->
   				<select class="select select_2" id ="select_2"  name="select_op'''+str(i)+'''">
'''+operator_sel+'''
   				</select>
			<!--fine select 2 -->

			<!--select3 -->
   				<select class="select select_3" id ="select_3_'''+str(i)+'''"  name="select_r'''+str(i)+'''" 
onchange="checkToEnableNumericForm('''+"'"+'''text_area1_'''+str(i)+"'"+''','''+"'"+'''select_3_'''+str(i)+"'"+''')">
                '''+obj_sel_dx+'''
   				</select>
			<!--fine select 3 -->

            <input disabled id="text_area1_'''+str(i)+'''" name="text_area1_'''+str(i)+'''"  class ="textarea1" type="text" >  	<!--questa è la textarea che su smartphone ti permette di inserie i numeri con tastiera numerica anzichè qwerty-->


			<!--select4 -->
   				<select class="select select_4" id ="select_4"   name="second_op'''+str(i)+'''">
                '''+operator2_sel+'''
   				</select>
			<!--fine select 4 -->

			<!--select5 -->
   				<select class="select select_5" id ="select_5_'''+str(i)+'''"   name="third_element'''+str(i)+'''"   onchange="checkToEnableNumericForm('''+"'"+'''text_area2_'''+str(i)+"'"+''','''+"'"+'''select_5_'''+str(i)+"'"+''')">
                '''+obj_sel_third+'''
   				</select>
			<!--fine select 5 -->
            
            <input disabled id="text_area2_'''+str(i)+'''"  name="text_area2_'''+str(i)+'''"  class ="textarea2" type="text"> <!--questa è la textarea che su smartphone ti permette di inserie i numeri con tastiera numerica anzichè qwerty-->



</div><!-- fine container1 e fine riga -->





 '''


menu_number=str(i)

default_obj_sel_sx='''<option>select_an_element</option>'''+obj_sel
default_obj_sel_dx='''<option>select_an_element</option>'''+obj_sel
default_obj_sel_dx2='''<option> </option>'''+obj_sel






part_to_insert_in_head='''

<link rel="stylesheet" href="/css/scenario_operations.css">
<title>Scenario Operations</title>

<script type="text/javascript">
function checkvalue() { 
  var mystring = document.getElementById('select_new_dx').value; 
  var mystring2 = document.getElementById('select_new_sx').value; 
  if('''+obj_name_comparison+''') {
    alert ('This is not allowed because already used or not valid');
    return false;
  }
  else {
    //alert("correct input");
    return true;
  }
}


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
html=getTopMenu(part_to_insert_in_head,slashes)










html=html+'''
		<div id="nomescenario">
				<div class="testo">'''+scenario_to_mod+'''</div>
		</div>



		<div id="infotext">
				<div class="testo">Imposta ora le AZIONI che lo scenario eseguirà automaticamente</div>
		</div>




<form action="" method="POST" >
<input type="hidden" name="function_to_run_1" value="'''+scenario_to_mod+'''">
<input type="hidden" name="scenario_operations" value="'''+scenario_to_mod+'''">
<input type="hidden" name="menu_number" value="'''+menu_number+'''">



'''+html_functionsToRun+'''






<div class="riga_container">

			<!--select1 -->
                <select id ="select_1" class ="select select_1" name="select_new_l">
               '''+default_obj_sel_sx+'''
   				</select>
			<!--fine select 1 -->

			<!--select2 -->
                <select id ="select_2" class ="select select_2" name="select_operator_new">
      					<option>=</option>
                        <option>!=</option>
   				</select>
			<!--fine select 2 -->

			<!--select3 -->
                <select id ="select_3new" class ="select select_3" name="select_new_r"  onchange="checkToEnableNumericForm('''+"'"+'''text_area1new'''+"'"+''','''+"'"+'''select_3new'''+"'"+''')"> 
                '''+default_obj_sel_dx+'''
   				</select>
			<!--fine select 3 -->

      <input disabled id="text_area1new" name="text_area1new" class ="textarea1" type="text"  > 			<!--questa è la textarea che su smartphone ti permette di inserie i numeri con tastiera numerica anzichè qwerty-->

			<!--select4 -->
   				<select id ="select_4" class ="select select_4"  name="second_operator_new">
                
                '''+operator2_sel_default+'''
   				</select>
			<!--fine select 4 -->

			<!--select5 -->
                <select id ="select_5new" class ="select select_5" name="select_new_third_element"  onchange="checkToEnableNumericForm('''+"'"+'''text_area2new'''+"'"+''','''+"'"+'''select_5new'''+"'"+''')">
                '''+default_obj_sel_dx2+'''
   				</select>
			<!--fine select 5 -->
            <input disabled id="text_area2new" name="text_area2new" class ="textarea2" type="text" > <!--questa è la textarea che su smartphone ti permette di inserie i numeri con tastiera numerica anzichè qwerty-->



</div><!-- fine container1 e fine riga -->



         <!--this button is hidden and will be pressed only when the user press enter key on a input form, will so reload the page saving the data  -->
        <button id="hidden_button" style="position: absolute;top: -1000px;"  class="submit_button" type="submit" name="save_and_reload_this_page" value="'''+path+'''">HiddenSubmit</button> 

        <button class="submit_button"  type="submit" name="scenario_operations_add_submit" value="scenario_operations_add_submit" onclick="checkvalue()">Add function</button>
        



        <button class="submit_button"  type="submit" name="finish_operation_setup" value="finish_submit">Finish</button>

	

<div id="footer"></div>

		
	
    </body>
</html>'''


web_page=html

