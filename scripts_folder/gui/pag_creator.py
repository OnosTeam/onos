# -*- coding: UTF-8 -*-
import codecs
from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py
obj_name_list=zone["objects"]   


#with codecs.open("css/play-zone.css",'r',encoding='utf8') as g:
#    css_file = g.read()
#    css_play_zone=css_file
#g.close()  
part_to_insert_in_head='''<!--onos_automatic_page--><!--onos_automatic_javascript--><link rel="stylesheet" href="../css/zone.css"><style type="text/css"><!--onos_automatic_body_style--></style>


'''
html=getTopMenu(part_to_insert_in_head)

play_zone_html=html+'''
<body>

<div id="ReloadThis" >


 '''


web_page=play_zone_html+ '''<div class="divisorio">'''+room.upper()+'''</div>'''



web_page_old=web_page

for a in obj_name_list :      # for every web_obj in the room


  web_page=web_page+'''

<div class="oggetto-container"> 
    <!--onos_automatic_object_a-->   
  <div class="oggetto" <!--onos_automatic_local_style--> >

    <!--onos_automatic_object_html-->

  </div> 

      <div id="stato-oggetto">
      <!--start_img'''+a+'''--><img class="flex" src="/img/on.png" class="image" />  <!--end_img'''+a+'''-->
      </div>
    </a>



  </div>'''

if len(obj_name_list)<2: #only the body
  web_page=web_page_old+"No objects present in this zone" 
        


web_page=web_page+'''<div id="footer"></div></div><!--end reload--></body></html>''' #the closing div is for the reload_page_indicator div
