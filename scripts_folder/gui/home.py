# -*- coding: UTF-8 -*-
# encoding=utf8

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

l=[]
l=sortZonesByOrderNumber()  #get a list of the zones ordered by the order number

part_to_insert_in_head='''<link rel="stylesheet" href="css/zone-list.css">

   	<title>Zone list</title>
'''.encode('ascii','ignore')


menu=getTopMenu(part_to_insert_in_head)
menu=menu.replace("right_menu_add_link_to_replace","/zone_creation/")  # replace the link in the + of the right menu

html=menu

for zone_name in l :             

  if (zoneDict[zone_name]["hidden"]!=0):  #skip the hidden elements
    continue     
  #html=html+'''<a href="/'''+zone_name+'''/index.html?="><div id="zone">'''+zone_name+'''</div></a>'''



  html=html+'''

		<div class="riga" >
			<a href="/'''+zone_name+'''/index.html?="><div class="zone-name col1">'''+zone_name+'''</div></a>
			<a href="/zone_creation/'''+zone_name+'''"><div class="impostazioni-link col2"><i class="icon-wrench"></i></div></a>
		</div>

'''.encode('ascii','ignore')

      

end_html='''</body></html>'''          
pag=html+end_html      #+'<a    href="/setup/">Rooms Configuration  </a><br/>'

web_page=pag
