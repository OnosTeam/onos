<?php
  $db = new SQLite3('users_db/.db_users_account');
  $tablesquery = $db->query("SELECT name FROM sqlite_master WHERE type='table';");

  echo 'tables:';
  while ($table = $tablesquery->fetchArray(SQLITE3_ASSOC)) {
    echo $table['name'] . '<br />';
  }


$result = $db->query('SELECT * FROM onos_user;');

while ($row = $result->fetchArray()){
  $username=$row['onos_username'];
  $password=$row['user_password'];
  $onos_db=$row['onos_db'];
  echo "-----------------------";
  echo "<br>username:";
  echo $username;
  echo "<br>password:";
  echo $password;
  echo "<br>onos_db:";
  echo $onos_db;
  echo "<br>";
  echo "-----------------------";
}

$db->close();
?>
