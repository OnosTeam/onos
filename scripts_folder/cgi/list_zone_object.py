# -*- coding: UTF-8 -*-
l=[]
l=sortZonesByOrderNumber()  #get a list of the zones ordered by the order number


html='''
<!DOCTYPE html>

<html>

    <head>
	<link rel="stylesheet" href="../css/play.css">
	<meta charset="utf-8">

    </head>
    <body>

	<div id="container-image">
       <img id="image" src="../img/header.jpg" class="image" />
	</div>

		<div id="container">
			<div id="play"  class="button" ><a href="#"><img class="flex" src="../img/play-ico.png" class="image" /></a></div>
			<div id="teach" class="button" ><a href="#"><img class="flex" src="../img/scenario-ico.png" class="image" /></a></div>
			<div id="setup" class="button" ><a href="#"><img class="flex" src="../img/setup-ico.gif" class="image" /></a></div>

<div id="exit" class="button" > <a href="logout.php">Log Out</a>  </div>
		</div>


    <div class="divisorio">LISTA ZONE</div>

 '''


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
