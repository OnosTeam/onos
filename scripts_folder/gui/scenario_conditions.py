# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

html=scenario_to_mod

obj_name_comparison='(mystring=="select_an_element")||(mystring2=="select_an_element")'


obj_sel=''
obj_sel_number=''
obj_list=object_dict.keys()
obj_list.sort()

for n in range(0,25):
  obj_sel_number=obj_sel_number+'''<option>'''+str(n)+'''</option>'''

for obj in obj_list:
  obj_sel=obj_sel+'''<option>'''+str(obj)+'''</option>
      '''



#example conditions:  (#_year_#==2016)&(#_hours_#==8)&(#_minutes_#==0)
conditions_string=scenarioDict[scenario_to_mod]["conditions"]  #get the string where there are the conditions
print type(conditions_string)
html_conditions=''

if ("|" not in conditions_string ):  # if the users has modified by hand the conditions..


  list_of_single_conditions=conditions_string.split("&")
  i=0
  for c in list_of_single_conditions: # for each condition
    
    c=c.replace('#_','')
    c=c.replace('_#','')
    c=c.replace('(','')
    c=c.replace(')','')

    obj_sel_sx=obj_sel
    obj_sel_dx=obj_sel_number+obj_sel
   
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

      i=i+1
      obj_sel_sx=obj_sel_sx.replace('(',' ')

      obj_sel_sx=obj_sel_sx.replace('''<option>'''+str(left_element)+'''</option>''',' ')
      obj_sel_sx='''<option>'''+str(left_element)+'''</option>'''+obj_sel_sx


 
      obj_sel_dx=obj_sel_dx.replace('''<option>'''+str(right_element)+'''</option>''',' ')
      obj_sel_dx='''<option>'''+str(right_element)+'''</option>'''+obj_sel_dx

      operator_sel='''
      					<option>==</option>
      					<option>></option>
      					<option><</option>
                        <option>!=</option>  '''

      #replace the selected option and put it on the first line
      operator_sel=operator_sel.replace('<option>'+operator+'</option>',' ')   
      operator_sel='<option>'+operator+'</option>'+operator_sel

                   
      html_conditions=html_conditions+'''

<div id="container_'''+str(i)+'''" class="container1 border">

				<div class="testo">IF</div>
			<!--select1 -->
   				<select class="left_select"  name="select_l'''+str(i)+'''" >
               '''+obj_sel_sx+'''
   				</select>
			<!--fine select 1 -->

			<!--select2 -->
   				<select class="operator_select"  name="select_op'''+str(i)+'''">
'''+operator_sel+'''
   				</select>
			<!--fine select 2 -->

			<!--select3 -->
   				<select class="right_select"  name="select_r'''+str(i)+'''">
                '''+obj_sel_dx+'''
   				</select>
			<!--fine select 3 -->



</div><!-- fine container1 e fine riga -->





 '''


menu_number=str(i)

default_obj_sel_sx='''<option>select_an_element</option>'''+obj_sel
default_obj_sel_dx='''<option>select_an_element</option>'''+obj_sel



part_to_insert_in_head='''	<link rel="stylesheet" href="../../../css/scenario_conditions.css">


<script type="text/javascript">
function checkvalue() { 
    var mystring = document.getElementById('select_new_dx').value; 
    var mystring2 = document.getElementById('select_new_sx').value; 
    if('''+obj_name_comparison+''') {
        alert ('This is not allowed because already used or not valid');
        return false;
    } else {
        //alert("correct input");
        return true;
    }
}
</script>
'''



slashes="../../../"
html=getTopMenu(part_to_insert_in_head,slashes)



html=html+'''
        <br><br><br>
		<div class="divisorio">CONDITIONS</div>

<div id="body2"><!--serve per dare un riferimento diverso dal body per il potion:relative ovvero dal menu in giù semplifica la costruzione della pagina -->


<!--fine pezzo standard per header menu e nome pagina -->




<form action="" method="POST" >
<input type="hidden" name="mod_conditions" value="'''+scenario_to_mod+'''">
<input type="hidden" name="menu_number" value="'''+menu_number+'''">



'''+html_conditions+'''






<div id="container_a" class="container1 border">

				<div class="testo">IF</div>
			<!--select1 -->
   				<select class="left_select" id="select_new_sx" name="select_new_l" >
               '''+default_obj_sel_sx+'''
   				</select>
			<!--fine select 1 -->

			<!--select2 -->
   				<select class="operator_select" id="select_new_c" name="select_new_o">
      					<option>==</option>
      					<option>></option>
      					<option><</option>
                        <option>!=</option>
   				</select>
			<!--fine select 2 -->

			<!--select3 -->
   				<select class="right_select" id="select_new_dx" name="select_new_r">
                '''+obj_sel_number+default_obj_sel_dx+'''
   				</select>
			<!--fine select 3 -->



</div><!-- fine container1 e fine riga -->










<div id="container_c" class="container1">

        <button class="submit-button" type="submit" name="condition_add_submit" value="add_condition_submit" onclick="checkvalue()">Add condition</button>
        
	
</div>

<div id="container_d" class="container1">

        <button id="sbutton" class="submit-button" type="submit" name="finish_conditions_setup" value="finish_submit">Finish</button>

</div>

	
</div>			<!--chiusura body2 -->
	

<div id="footer"></div>

		
	
    </body>
</html>'''


web_page=html

