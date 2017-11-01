import os,re,tarfile,time
#glinet_version_update  where tmps is mounted in /tmp  when you write to /tmp  tou write in ram
#note : to make an update file  you have to make a tar of the onos files inside the  script_folder  location where webserver.py is ...
#then rename the tar to scripts_folder.tar.gz
#don't make a tar from the previous directory!
#then update the online md5sum for the script and for the tar!



tmp_dir="/tmp/onos_update/"


print("current_hw:"+current_hw)
print("base_path:"+base_path)
print("current_local_fw"+current_local_fw)
print("online_fw_folder_url:"+online_fw_folder_url)   #get from the update_check.py that execute this script
print("os.getcwd():"+os.getcwd())

msg="ex0"
s_mail="1"
send_to_php_log(router_sn,current_hw,current_local_fw,msg,s_mail)

free_ram_space=0
try:
  free_ram_space=float((re.search('tmpfs(.+?)\n',os.popen("df").read().split("/tmp ")[0]).group(1)).split()[2]) #get free ram space in kbytes
except :
  print "error , cannot read free memory with df cmd"


if (free_ram_space < 4000): #if there are not at least 4 mbyte of free space in ram ...
  print "error the hardware has not enaught free ram space"
  msg="errRam"
  s_mail="1"
  send_to_php_log(router_sn,current_hw,current_local_fw,msg,s_mail)
  quit()
else: # there is enough free memory
  #os.system("touch va.txt")
  #http://myonos.com/onos/updates/glinet/scripts_folder.tar.gz


  if online_fw_folder_url=="local":  #the files are already in the onos_update/ folder
    print("local folder used for update")
    try:
      md5_file = open("onos_update/md5sum_tar.txt",'r')  
      md5_code=(md5_file.read()).strip()   #get the string and delete the \n
      md5_file.close()

      file_md5code=os.popen("md5sum onos_update/scripts_folder.tar.gz").read().split(" ")[0] 
      if md5_code!=file_md5code:
        print("0 update failed,corrupted tar")
        msg="errlocal"
        s_mail="0"
        send_to_php_log(router_sn,current_hw,current_local_fw,msg,s_mail)
        os.system("rm -f onos_update/")  # delete the folder so next time it will be redownloaded by update_check.py
        quit()
    except Exception as e:     
      message="error, maybe there is not internet connection"
      print(message)
      print(e)
      print(sys.exc_info())

 

  else:  # I need to download  the files..
    try_number=5  
    while (try_number>0): #retry 5 times to retrieve the file before to giveup
      #tar_file= urllib2.urlopen(onos_online_server_url+'updates/'+current_hw+'/scripts_folder.tar.gz').read() 
      md5sum_tar_url=online_fw_folder_url+'''/md5sum_tar.txt '''
      scripts_folder_tar_url=online_fw_folder_url+'''/scripts_folder.tar.gz'''
      print("i download md5sum_tar from:"+md5sum_tar_url) 
      print("i download scripts_folder_tar from:"+scripts_folder_tar_url) 
      try:
        os.system("mkdir -p "+tmp_dir)
        os.system("rm -f "+tmp_dir+"scripts_folder.tar.gz")
        os.system("rm -f "+tmp_dir+"md5sum_tar.txt")

        os.system('''wget -O '''+tmp_dir+'''md5sum_tar.txt '''+md5sum_tar_url )
        os.system('''wget -O '''+tmp_dir+'''scripts_folder.tar.gz '''+scripts_folder_tar_url)


        md5_file = open(tmp_dir+"md5sum_tar.txt",'r')  
        md5_code=(md5_file.read()).strip()   #get the string and delete the \n
        md5_file.close()

        file_md5code=os.popen("md5sum "+tmp_dir+"scripts_folder.tar.gz").read().split(" ")[0] 
        if md5_code!=file_md5code:
          print "file is corrupted"
          if try_number==1:
            print "update failed,corrupted tar"
            msg="errUp0"
            s_mail="0"
            send_to_php_log(router_sn,current_hw,current_local_fw,msg,s_mail)
            quit()
          else:
            try_number=try_number-1
            continue
            
 
        else: #the file is not corrupted
          print "tar is ok"
          break

      #fo = open("/tmp/onos_update/scripts_folder.tar.gz", "wb")
      #fo.write(tar_file)
      #tar_file.close()
      #fo.close()  
      except Exception, e :
        print "some error happened in the scripts_folder.tar.gz download"  
        print e.args
        try_number=try_number-1









  #here i have the right tar in  /tmp/onos/onos_update/
  os.system("mkdir -p "+tmp_dir+"downloaded_fw")
  os.system("tar xzf "+tmp_dir+"/scripts_folder.tar.gz -C "+tmp_dir+"downloaded_fw/")


#rm -R /tmp/ram/b/onos_5.15/scripts_folder/!(cgi|zone|config_files|zones|globalVar.py)
  #print ("rm -R "+base_path+"scripts_folder/!(cgi|zone|config_files|zones|globalVar.py)")
  #os.system('''rm -rf '''+base_path+'''scripts_folder/!(cgi|zone|config_files|zones|globalVar.py)''')


  print ('''ls -1 '''+base_path+'''scripts_folder/ | grep -v "cgi\|zone\|config_files\|zones\|globalVar.py" | xargs rm -rf ''')
  #os.system('''cd '''+base_path+'''scripts_folder/''')
  os.system('''cd '''+base_path+'''scripts_folder/ && ls -1 | grep -v "cgi\|zone\|config_files\|zones\|globalVar.py" | xargs rm -rf ''')


  print ('''cp -r -n'''+tmp_dir+'''downloaded_fw/scripts_folder/* '''+base_path+'''scripts_folder/''')
  os.system('''cp -r -n '''+tmp_dir+'''downloaded_fw/scripts_folder/* '''+base_path+'''scripts_folder/''')

  print "cleared directories"

  if online_fw_folder_url!="local":
    fw_version_url=online_fw_folder_url+'''/fw_version.txt''' 
    print("I get fw_version.txt from:"+fw_version_url)
    os.system('''wget -O '''+base_path+'''fw_version.txt '''+fw_version_url)
    time.sleep(10)
    os.system('''rm -rf '''+base_path+'''onos_update''')
    
  else:

    os.system('''cp onos_update/fw_version.txt '''+base_path+'''fw_version.txt ''')
    os.system('''rm -rf onos_update''')







