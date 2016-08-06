# -*- coding: UTF-8 -*-

from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

l=[]
l=sortZonesByOrderNumber()  #get a list of the zones ordered by the order number

part_to_insert_in_head=''' <link rel="stylesheet" href="../css/play.css"> '''
html=getTopMenu(part_to_insert_in_head)


for zone_name in l :             

  if (zoneDict[zone_name]["hidden"]!=0):  #skip the hidden elements
    continue     
  #html=html+'''<a href="/'''+zone_name+'''/index.html?="><div id="zone">'''+zone_name+'''</div></a>'''



  html=html+'''<br><br><br><div class="zona-container">
			<div class="zona"><a href="/'''+zone_name+'''/index.html?=">'''+zone_name+'''</a></div>
			<div id="setup-zona"><a href="/zone_objects_setup/'''+zone_name+'''"><img class="flex" src="../img/wrench.png" class="image" /></a></div>
		</div><br>'''

      

end_html='''<div id="footer"></div> </body></html>'''          
pag=html+end_html      #+'<a    href="/setup/">Rooms Configuration  </a><br/>'

web_page=pag
