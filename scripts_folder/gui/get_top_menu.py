
#note:
#  href="/">  for first page of onos
#  href="scenarios_list/" for the scenario list
#  href="/setup/" for the setup
#





web_page=''



def getTopMenu(text_to_insert_in_head="",slashes="../"):
  '''
  | Get a standard html for the menu , the variable slashes contain a string with 
  | how many "../" as needed to return to the onos main directory-
  | it will make the correct relative path for the immages and css.
  |
  '''

  global web_page 
  relative_path=slashes

   #for i in range (0,number_of_slashes):
   # relative_path=relative_path+"../"

  top_menu_html='''<!DOCTYPE html>

<html>

    <head>
    <!--onos_automatic_meta-->
	<link rel="stylesheet" href="'''+relative_path+'''css/menu.css">


    </head>
    <body>

<div id="big-container">	



		<div id="upper-bar-image"><img class="flex" src="'''+relative_path+'''img/upper-bar.png" class="image" /></div>
		<div id="upper-bar-testo">ONOS House</div>
		

		<div id="container-menu"> 
			


			<div id="play-button" class="menu-button"><a href="/"><img class="flex" src="'''+relative_path+'''img/play.png" class="image" /></a></div>
			<div id="scenario-button" class="menu-button"><a href="/scenarios_list/"><img class="flex" src="'''+relative_path+'''img/scenario.png" class="image" /></a></div>
			<div id="settings-button" class="menu-button"><a href="/setup/"><img class="flex" src="'''+relative_path+'''img/settings.png" class="image" /></a></div>
			<div id="exit-button" class="menu-button"><a href="#"><img class="flex" src="'''+relative_path+'''img/exit.png" class="image" /></a></div>

		</div>


<!--fine pezzo standard per header menu e nome pagina 2321-->    '''







  web_page=top_menu_html


  tmp_page=web_page[0:web_page.find('<head>')+6]+text_to_insert_in_head+web_page[web_page.find('<head>')+6:]
  #warning!!! you have to write exactly "<head>"  not "< head>" nor "<head >" nor "<HEAD>"
  #the text_to_insert_in_head will be inserted in the start of head html 

  #web_page=web_page+text_to_insert_in_head
  return(tmp_page)

















