# -*- coding: UTF-8 -*-

"""
| Display a list with all the objects in the objectDict
| 
|
"""

import os
from get_top_menu import *  # works because there is sys.path.append(lib_dir2)  in globalVar.py



part_to_insert_in_head = '''<link rel="stylesheet" href="/css/mod_object.css">
    <title>Objects list</title>
'''.encode('ascii', 'ignore')


menu = getTopMenu(part_to_insert_in_head)
menu = menu.replace("right_menu_add_link_to_replace", "/obj_creation/")  # replace the link in the + of the right menu

objects_list = list(objectDict) # get list of all objects in the system

html = menu


html = html + '''


 			<div class="row_type2" >
            
            <div>
            <p class="big_text" style="position:absolute;left:32%;">Rename the object</p> 
            <p class="small_text"  style="position:absolute;left:32%;">Insert a new name for the object and press save</p> 
            </div> 
            
            <div>
			<input name="mod_object_rename" id="mod_object_rename" 
            class="name_text"  type="text"  onfocus="if(this.value == 'Scrivi il nome della zona') { this.value = ''; }" value=""/>
            </div>

         <!--this button is hidden and will be pressed only when the user press enter key on a input form, will so reload the page saving the data  -->
         <button  id="hidden_button" style="position: absolute;top: -1000px;" class="submit_button" type="submit" name="save_and_reload_this_page" value="" onclick="replaceHiddenButtonValue()">HiddenSubmit</button> 

            <div style="padding-top:55px;align:'center'"; >

            <button class="save_button" type="submit" name="finish_obj_rename" value="finish_obj_rename" >Save <i class="icon-floppy-disk"></i></button></div>


			</div>


            '''


end_html = '''</body></html>'''          
web_page = html + end_html
