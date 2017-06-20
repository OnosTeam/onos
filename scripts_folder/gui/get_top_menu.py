#!/usr/bin/env python
# -*- coding: UTF-8 -*-


#note:
#  href="/">  for first page of onos
#  href="scenarios_list/" for the scenario list
#  href="/setup/" for the setup
#





web_page=''



def getTopMenu(text_to_insert_in_head="",slashes="../",right_menu={}):
  '''
  | Get a standard html for the menu , the variable slashes contain a string with 
  | how many "../" as needed to return to the onos main directory-
  | it will make the correct relative path for the immages and css.
  |
  |
  |
  | todo: use the dictionary right_menu to pass the html to use for the right menu , still to implement..
  | right_menu={"visible":1,"links":({"nuova":html},{"elimina":html},{"applica":html})}
  | right_menu["links"][0]["nuova"]="html_nuova"
  | right_menu["links"][1]["elimina"]="html_elimina"
  | right_menu["links"][2]["applica"]="html_applica"
  |

  '''

  global web_page 
  relative_path=slashes

   #for i in range (0,number_of_slashes):
   # relative_path=relative_path+"../"

  top_menu_html=u'''
<!DOCTYPE html>

<html>

    <head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
	<meta name="apple-mobile-web-app-capable" content="yes">

	<link rel="stylesheet" href="/css/onos-font.css">
	<link rel="stylesheet" href="/css/menu.css">

	<meta charset="utf-8">


<script>
var x = 0; //la metto prima della funzione perche voglio che esista sempre..non solo quando eseguo la funzione,altrimenti sarebbe sempre ricreata ed uguale a 0
var y = 0;


function menusxfunction(menu_sx,funzionesx) {
		if (funzionesx=="open_close_sx"){
	  		if(x === 0){ 
	      	x=1;
	      	y=0;
	      	document.getElementById('menu_sx').style.marginLeft = "0%";
	    	} 
	  		else {
	      	x=0;
	      	document.getElementById('menu_sx').style.marginLeft = "-100%"; 
	    	}  
	  	}
}

function menudxfunction(menu_rx,funzionedx) {
	if (funzionedx=="open_close_dx"){
  		if(y === 0){ 
      	y=1;
      	X=0;
      	document.getElementById('menu_rx').style.marginRight = "0%";
    	} 
  		else {
      	y=0;
      	document.getElementById('menu_rx').style.marginRight = "-100%"; 
    	}  
  	}
}

</script>



    </head>
   <body>

	<div id="invisible_top_banner"></div>


		<div id="menu_top_button" class="banner-color banner-col1" onclick="menusxfunction(this.id,'open_close_sx');"><i class="icon-menu"></i></div>
		<div id="date" class="banner-color banner-col2">12-10-2016</div>
		<div id="time" class="banner-color banner-col3">23:36</div>
		<div id="right_menu_button" class="banner-color banner-col4" onclick="menudxfunction(this.id,'open_close_dx');"><i class="icon-plus"></i></div>




	<div id="menu_sx">


		<a href="/"><div id="homebutton" class="vocemenu_sx" ><i class="icon-home3"></i>Home</div></a>
		<a href="/"><div id="zonebutton" class="vocemenu_sx" ><i class="icon-book"></i>Zone</div></a>
		<a href="/scenarios_list/"><div id="scenaributton" class="vocemenu_sx"><i class="icon-calculator"></i>Scenari</div></a>
		<a href="#"><div id="oggettibutton" class="vocemenu_sx"><i class="icon-price-tag"></i>Oggetti</div></a>
		<a href="/setup/"><div id="impostazionibutton" class="vocemenu_sx"><i class="icon-settings"></i>Impostazioni</div></a>
		<a href="#"><div id="accountbutton" class="vocemenu_sx"><i class="icon-user2"></i>Account</div></a>


		<div id="closebutton_sx" onclick="menusxfunction(this.id,'open_close_sx');"><i class="icon-cross"></i></div>

	</div>

	<div id="menu_rx">

		<a href="/zone-creation.html"><div class="menu_rx_riga" >
			<div id="newzone" class="voce-menu-R side-col1" >Nuova</div>
			<div class="icona-menu-R new side-col2"><i class="icon-plus"></i></div>
		</div></a>
			
		<div class="menu_rx_riga" >
			<div id="deletezone" class="voce-menu-R side-col1" >Elimina</div>
			<div class="icona-menu-R delete side-col2"><i class="icon-bin"></i></div>
		</div>
		
		<div class="menu_rx_riga" >
			<div id="submit" class="voce-menu-R side-col1" >Applica</div>
			<div class="icona-menu-R sub side-col2"><i class="icon-checkmark"></i></div>
		</div>

		<div id="closebutton_rx" onclick="menudxfunction(this.id,'open_close_dx');"><i class="icon-cross"></i></div>

	</div>
	

 '''.encode('ascii','ignore')



  





  web_page=top_menu_html


  tmp_page=web_page[0:web_page.find('<head>')+6]+text_to_insert_in_head+web_page[web_page.find('<head>')+6:]
  #warning!!! you have to write exactly "<head>"  not "< head>" nor "<head >" nor "<HEAD>"
  #the text_to_insert_in_head will be inserted in the start of head html 

  #web_page=web_page+text_to_insert_in_head
  return(tmp_page)

















