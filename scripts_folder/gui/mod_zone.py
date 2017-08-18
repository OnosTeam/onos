# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py




# zone_to_mod is a variable from wenserver.py

default_zone_form_value="Scrivi il nome della zona"


part_to_insert_in_head='''

	<link rel="stylesheet" href="/css/zone_creation.css">
	<meta charset="utf-8">
	<title>Creazione Zona</title>
'''

javascript_to_insert_in_page='''

<script type="text/javascript">
function checkvalue() { 

  var mystring = document.getElementById('new_zone_to_create').value; 

  if (mystring=="'''+default_zone_form_value+'''"){ // to reset the value when not inserted by user.
    document.getElementById('new_zone_to_create').value="";
  }

  if(mystring=="'''+zone_to_mod+'''") {
    alert ('This is not allowed because already used or not valid');
    return false;
  }
  else {
    //alert("correct input");
    return true;
  }


}





</script>




    </head>


'''



menu=getTopMenu(part_to_insert_in_head)

html=menu




html=html.replace("<!--Javascript_to_replace-->",javascript_to_insert_in_page)


html=html+'''
        <form action="" method="POST" onsubmit="return checkvalue(this)" >
        	<input type="hidden" name="zone_setup_manager" value="'''+zone_to_mod+'''" >



			<div class="riga" >
			<input name="new_zone_to_create" id="new_zone_to_create" class="name_text" type="text" onfocus="if(this.value == 'Scrivi il nome della zona') { this.value = ''; }" value="'''+default_zone_form_value+'''"/>
			</div>

			<div class="riga" >
				<p class="testo_big">Lista oggetti della Zona</p> 
				<p class="testo_small">Seleziona la spunta per aggiungere o rimuovere gli oggetti </p> 					
			</div>

			<div id="select_box" >

'''




total_object_name_list=objectDict.keys()  
total_object_name_list.sort()#sorted by name
zone_obj_name_list=""

if zone_to_mod  in zoneDict.keys(): 

  logprint("zone in zoneDict")
  zone_obj_name_list=zoneDict[zone_to_mod]["objects"] 
  logprint("obj_name_list:"+str(zone_obj_name_list))   
  tmp_html='<tr><td class="web_obj_name">No web object present in this room</td><td></td><td class="web_obj_name"></td></tr>'

  zone_obj_name_list.sort()




  for a in zone_obj_name_list : # the object is inside the zone list so I will set it as checked in the html 


    html=html+'''
				<label for="'''+a+'''"><div class="riga_box" >				
					<input name="'''+a+'''_sel_obj" type="checkbox" value="checked" id="'''+a+'''" checked>
					<div class="check" ><i class="icon-checkmark"></i></div>
					<div class="ogg_selection" >'''+a+'''</div>					
				</div></label>    
  '''


for a in total_object_name_list : # the object is not inside the zone list so I will not set it as checked in the html 
  if a in zone_obj_name_list: #skip the already printed objects
    continue
     
  html=html+'''
				<label for="'''+a+'''"><div class="riga_box" >				
					<input name="'''+a+'''_sel_obj" type="checkbox" value="checked" id="'''+a+'''" >
					<div class="check" ><i class="icon-checkmark"></i></div>
					<div class="ogg_selection" >'''+a+'''</div>					
				</div></label>    
    ''' 
     

html=html+'''
			</div>
		
			<div class="riga" >
					<button class="save_button" type="submit" name="finish_zone_setup" value="zone_submit" >Salva  <i class="icon-floppy-disk"></i></button>




			</div>
		</form>
		
	</body>
</html>

'''

web_page=html


