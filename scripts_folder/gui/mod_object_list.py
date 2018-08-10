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

for object_name in objects_list:
    html = html + '''<div class="row_type1" >'''
    html = html + '''    <a href="mod_object_select/''' + object_name + ''' ">
                         <div class="element_name col1">''' + object_name + '''</div>
                         </a> <br> '''
    html = html + '''</div>'''


end_html = '''</body></html>'''          
web_page = html + end_html
