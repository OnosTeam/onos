# -*- coding: UTF-8 -*-
import codecs
obj_name_list=zone["objects"]   


#with codecs.open("css/play-zone.css",'r',encoding='utf8') as g:
#    css_file = g.read()
#    css_play_zone=css_file
#g.close()  
 


play_zone_start_html='''<!DOCTYPE html><html><head><!--onos_automatic_meta--><!--onos_automatic_page--><title>ONOS</title><!--onos_automatic_javascript-->
<meta charset="utf-8">
<link rel="stylesheet" href="../css/zone.css">
<style type="text/css">

<!--onos_automatic_body_style-->
    </style>
</head>
<body>

<div id="ReloadThis" >
	<div id="container-image">
       <img id="image" src="/img/header.jpg" class="image" />
	</div>


		<div id="container">
			<div id="play"  class="button" ><a href="/"><img class="flex" src="/img/home.png" class="image" /></a></div>
			<div id="teach" class="button" ><a href="/scenarios_list/"><img class="flex" src="/img/scenario-ico.png" class="image" /></a></div>
			<div id="setup" class="button" ><a href="/setup/"><img class="flex" src="/img/setup-ico.gif" class="image" /></a></div>
        <div id ="system_time"> <!--onos_system_time-->  </div>
		</div>

 '''


web_page=play_zone_start_html+ '''<div class="divisorio">'''+room.upper()+'''</div>'''



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
