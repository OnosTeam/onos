# -*- coding: UTF-8 -*-

import os
from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

csv_folder=csv_path

logprint("csv_list  executed:"+current_path)

part_to_insert_in_head='''<link rel="stylesheet" href="/css/csv_list.css">

   	<title>Csv list</title>
'''.encode('ascii','ignore')


menu = getTopMenu(part_to_insert_in_head)
menu = menu.replace("right_menu_add_link_to_replace","/zone_creation/") # replace the link in the + of the right menu

file_list = os.listdir(os.getcwd()+"/csv")
html = menu

for file_name in file_list:
    html = html +'''<div class="riga" >'''
    html = html + '''    <a href="'''+csv_folder+file_name+''' "><div class="zone-name col1">'''+file_name+'''</div></a> <br> '''
    html = html + '''</div>'''    
    
        

end_html = '''</body></html>'''          
web_page = html + end_html
