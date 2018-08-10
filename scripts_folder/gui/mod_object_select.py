# -*- coding: UTF-8 -*-

"""
| Display a list with all the objects in the objectDict
| 
|
"""

import os
from get_top_menu import *  # works because there is sys.path.append(lib_dir2)  in globalVar.py



part_to_insert_in_head = '''<link rel="stylesheet" href="/css/mod_object.css">
    <title>Object Mod</title>
'''.encode('ascii', 'ignore')


menu = getTopMenu(part_to_insert_in_head)
menu = menu.replace("right_menu_add_link_to_replace", "/obj_creation/")  # replace the link in the + of the right menu

objects_list = list(objectDict) # get list of all objects in the system

# current_object_name passed from webserver.py

print("current_object_name:" + current_object_name)

html = menu
html = html + '''

                 
                 <div class="row_type1" >
                 <a href="/mod_object_mail/''' + current_object_name + '''">
                 <div class="element_name col1">Modify mail notification for this object</div>
                 </a> <br>
                 </div>
                 
                 <div class="row_type1" >
                 <a href="/mod_object_perm/''' + current_object_name + '''">
                 <div class="element_name col1">Change object permissions and group</div>
                 </a> <br>
                 </div>

                 <div class="row_type1" >
                 <a href="/mod_object_rename/''' + current_object_name + '''">
                 <div class="element_name col1">Rename object</div>
                 </a> <br>
                 </div>

                 <div class="row_type1" >
                 <a href="/mod_object_delete/''' + current_object_name + '''">
                 <div class="element_name col1">Delete this object</div>
                 </a> <br>
                 </div>
                 
                 
                 '''


end_html = '''</body></html>'''          
web_page = html + end_html
