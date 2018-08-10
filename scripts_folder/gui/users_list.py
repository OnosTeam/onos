# -*- coding: UTF-8 -*-
import codecs
from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

part_to_insert_in_head='''
	<link rel="stylesheet" href="/css/users_list.css">

'''


html=getTopMenu(part_to_insert_in_head)

html=html+"Lista Utenti:<br>"


for user in online_usersDict.keys():
  html=html+"nome utente:"+user+"<br>"+"user_mail:"+online_usersDict[user]["user_mail"]+"<br><br>"




html=html+'''Crea nuovo utente: <a href="/gui/new_user.py"> nuovo utente </a>   <br><br><br><br><br>  '''
end_html='''<div id="footer"></div></body></html> '''


web_page=html+end_html

































