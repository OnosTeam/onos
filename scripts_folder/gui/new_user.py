
try:
  message=message+""

except:
  message=""

web_page=''' 
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="../css/new_user_form.css" type="text/css" media="all" />
  <meta name="viewport" content="width=device-width" , initial-scale=1, maximum-scale=1"> 
  <meta charset="utf-8">
  <title>O.N.O.S</title>
<script type="text/javascript" language="javascript">function SelectAll(id){    document.getElementById(id).focus();   document.getElementById(id).select();}</script>
</head>
<body>






<h1>Create a new user</h1>

<div id="body2">

  <form action="" method="POST"><input type="hidden" name="new_user_form" value="">

  

  <div id="container">
    <h1>Username</h1>
    <input class="textbox" id="create_user_form" name="create_user_form" onfocus="SelectAll('create_user_form')"; type="text" value=""  size="40" maxlength="200" />


  <h1>Password</h1>
  <input class="textbox" type="password" id="create_password_form" maxlength="200" size="40" name="create_password_form"  onfocus="SelectAll('create_password_form')"; value="" />


  <h1>Repeat Password</h1>
  <input class="textbox" type="password" id="repeat_password_form" maxlength="200" size="40" name="repeat_password_form"  onfocus="SelectAll('repeat_password_form')"; value="" />


  <h1>Mail</h1>
  <input class="textbox" type="text" id="create_mail_form" maxlength="200" size="40" name="create_mail_form"  onfocus="SelectAll('create_mail_form')"; value="" />

  </div>



<div id="error"><h2>'''+message+'''</h2></div>

  
  <div id="container2">
    <input  id="log" type="submit" value="LOGIN">
	<label id="login" for="log">LOGIN</label>

  </div>




</div>
</form> 
</body>
</html>'''
