# -*- coding: UTF-8 -*-

import sys,os,os.path,urllib2,re,platform
import json

global base_path
global onos_online_server_url
global current_local_fw
global current_hw



default_online_server_url="http://www.myonos.com/onos/"


platform=platform.node()
base_cfg_path=""
router_sn=""
base_path=""

#if (os.path.exists("/sys/class/gpio")==1) : #if the directory exist ,then the hardware has embedded IO pins
if (platform.find("Orange")!=-1)or(platform.find("orange")!=-1)or(platform.find("RouterOP")!=-1): #found uname with orange pi name or RouterOP
  base_path="/bin/onos/"
  router_sn=platform[0:12]  #get the serial number from /etc/hostname  
  router_hardware_type="RouterOP"
  enable_usb_serial_port=1
  base_cfg_path="/bin/onos/scripts_folder/"
  baseRoomPath="/bin/onos/scripts_folder/zones/"

else: #disable serial port
  base_path=""
  router_sn=platform[0:12]  #get the serial number from /etc/hostname  
  router_sn="RouterOP0000"
  router_hardware_type="RouterPC"
  enable_usb_serial_port=0
  base_cfg_path=""
  baseRoomPath=os.getcwd()+"/zones/"    #you musn't have spaces on the path..



def get_fw_hw_from_file(file_path):
  try:

    with open(file_path+"fw_version.txt", 'r') as current_version_file:
      current_version=current_version_file.read()

    current_version_dict=json.loads(current_version)  
    print("local_fw_file:"+current_version)

    if router_sn in list(current_version_dict):  #there is a specific update for this serial number
#{"fw":"5.29","hw":"RouterOP","files":"226","RouterOP0000":{"c_fw":"5.30","c_hw":"RouterOP","c_files":"226","c_folder":"RouterOP0000"} }
      current_fw=current_version_dict[router_sn]["c_fw"]
      current_hw=current_version_dict[router_sn]["c_hw"] 
      current_files_number=current_version_dict[router_sn]["c_files"] 
      folder=current_version_dict[router_sn]["c_folder"] 
      return({"current_local_fw":current_fw,"current_hw":current_hw,"current_files_number":current_files_number,"folder":folder})

    else:
#{"fw":"5.29","hw":"RouterOP","files":"226"}
      current_fw=current_version_dict["fw"]
      current_hw=current_version_dict["hw"]  #find the hw ("glinet") from current_version
      current_files_number=current_version_dict["files"] 
      folder=""
      return({"current_local_fw":current_fw,"current_hw":current_hw,"current_files_number":current_files_number,"folder":""})


  except Exception as e:
    print(str((e,sys.exc_info())) )
    current_fw="999"
    current_hw="RouterOP"
    current_files_number="0"


  return({"current_local_fw":current_fw,"current_hw":current_hw,"current_files_number":current_files_number,"folder":""})






update_dir=base_path+"onos_update/"
file_path=update_dir+"onos_update.py" 

md5_update_script_code=-4
file_md5code=-5



def get_fw_hw_in_onos_update_folder(base_path):

  """
  | Parse and return the data from the downloaded files present in the folder onos_update/
  |  
  |
  """
  folder=""
  if os.path.isdir(base_path+"onos_update"): #if the "onos_update" folder exist    
    print('the  '+base_path+"onos_update"+' folder  exist ')     
    try:
      md5_file = open(base_path+"onos_update/md5sum_update_script.txt",'r')  
      md5_update_script_code=(md5_file.read()).strip()   #get the string and delete the \n
      md5_file.close()
      file_md5code=os.popen("md5sum "+base_path+"onos_update/onos_update.py").read().split(" ")[0] 

      print("file to open:"+base_path+"onos_update")
      downloaded_version_file_dict=get_fw_hw_from_file(base_path+"onos_update")
      current_downloaded_fw=downloaded_version_file_dict["current_local_fw"] 
      current_downloaded_hw=downloaded_version_file_dict["current_hw"]  #find the hw ("glinet") from downloaded_version
      current_downloaded_files_number=downloaded_version_file_dict["current_files_number"]  
      folder=downloaded_version_file_dict["folder"] 

    except Exception as e:
      print(str((e,sys.exc_info())) )
      print "the directory/file update do not exist or are corrupted"
      current_downloaded_fw="0"
      current_downloaded_hw="glinet"
      downloaded_files_number="0"
      md5_update_script_code=-4
      file_md5code=-5
      current_downloaded_files_number="0"

  else: #the  "onos_update" folder doesn not exist 
    print('the  '+base_path+"onos_update"+' folder doesn not exist ')
    current_downloaded_fw="0"
    current_downloaded_hw="glinet"
    downloaded_files_number="0"
    md5_update_script_code=-4
    file_md5code=-5
    current_downloaded_files_number="0"


  return({"current_downloaded_fw":current_downloaded_fw,"current_downloaded_hw":current_downloaded_hw,"current_downloaded_files_number":current_downloaded_files_number,"md5_update_script_code":md5_update_script_code,"file_md5code":file_md5code,"folder":folder})



#if os.path.isfile(file_path):  #if the directory and the  file exist...


def get_online_fw_hw(version_url,current_hw,router_sn):

  """
  | Get and parse the current online fw hw version
  |
  |
  """


  try:

    url_fw_version=version_url+'updates/'+current_hw+'/fw_version.txt'
    print "I try to download the current fw version number"
    print("at:"+url_fw_version)
    
    response = urllib2.urlopen(url_fw_version)
    #the url will be like: http://www.myonos.com/onos/updates/glinet/fw_version.txt
    version_txt=response.read()  #now i got the txt file 
    online_version_dict=json.loads(version_txt)  

    if router_sn in list(online_version_dict):  #there is a specific update for this serial number
#{"fw":"5.29","hw":"RouterOP","files":"226","RouterOP0000":{"c_fw":"5.30","c_hw":"RouterOP","c_files":"226","c_folder":"RouterOP0000"} }

      print("there is a specific update for this serial number")
      online_fw=online_version_dict[router_sn]["c_fw"]
      online_hw=online_version_dict[router_sn]["c_hw"] 
      online_files_number=online_version_dict[router_sn]["c_files"] 
      folder=online_version_dict[router_sn]["c_folder"] 
      return({"online_fw":online_fw,"online_hw":online_hw,"online_files_number":online_files_number,"folder":folder})

    else:
#{"fw":"5.29","hw":"RouterOP","files":"226"}
      print("i will check the general update file")
      online_fw=online_version_dict["fw"]
      online_hw=online_version_dict["hw"]  #find the hw ("glinet") from current_version
      online_files_number=online_version_dict["files"] 
      folder=""
      return({"online_fw":online_fw,"online_hw":online_hw,"online_files_number":online_files_number,"folder":""})

  except Exception as e:
    print "error, maybe there is not internet connection"
    print(str((e,sys.exc_info())) )
    print e.args 
    online_fw="0"
    online_hw="glinet"
    online_files_number="0"
  print ("online_fw:"+online_fw)
  return({"online_fw":online_fw,"online_hw":online_hw,"online_files_number":online_files_number,"folder":""})



current_local_fw_dict=get_fw_hw_from_file(base_path)
current_local_fw=current_local_fw_dict["current_local_fw"]
current_hw=current_local_fw_dict["current_hw"]
current_files_number=current_local_fw_dict["current_files_number"]
print("THE DICT IS:"+str(current_local_fw_dict) )


fw_hw_in_onos_update_folder_dict=get_fw_hw_in_onos_update_folder(base_path)
md5_update_script_code=fw_hw_in_onos_update_folder_dict["md5_update_script_code"]
file_md5code=fw_hw_in_onos_update_folder_dict["file_md5code"]
current_downloaded_fw=fw_hw_in_onos_update_folder_dict["current_downloaded_fw"]
online_fw_folder=fw_hw_in_onos_update_folder_dict["folder"]

if (md5_update_script_code==file_md5code)&(float(current_local_fw)<float(current_downloaded_fw)):  #if the script exist and is not corrupted and the new fw version is newer than the current one
  print("the script exist and is not corrupted and the new fw version is newer than the current one")
  namespace={"current_hw":current_hw,"base_path":base_path,"current_local_fw":current_local_fw,"online_fw_folder":online_fw_folder}    
  try:
    global_file = open(base_path+"scripts_folder/globalVar.py",'r')  
    text=global_file.read()
    global_file.close()
    onos_online_server_url=re.search('onos_online_site_url="(.+?)"',text).group(1)  #find the domain from globalVar.py

  except:
    onos_online_server_url=default_online_server_url
   




  try: 
    execfile(file_path,globals(),namespace) #execute the python script
  
  except Exception as e:     
    message="error0 execfile(file_path,globals(),namespace) #executing the python script  "
    print(str(e,sys.exc_info() ) )
    print e.args 


else:#the directory doesn't exist i check if the enable_onos_auto_update is yes

  
  try:
    cfg_file = open(base_path+"scripts_folder/config_files/cfg.json",'r')  
    text0=cfg_file.read()
    cfg_file.close()

  except:
    text0=''' enable_onos_auto_update": "yes" '''


 
  if text0.find('''enable_onos_auto_update": "yes"''')!= -1:  #if the auto update is enabled

    print('enable_onos_auto_update": "yes"')
    try:
      global_file = open(base_path+"scripts_folder/globalVar.py",'r')  
      text=global_file.read()
      global_file.close()
  
      onos_online_server_url=re.search('onos_online_site_url="(.+?)"',text).group(1)  #find the domain from globalVar.py




    
    except:

      current_local_fw="3.15"
      current_hw="glinet"
      current_files_number="0"
      onos_online_server_url=default_online_server_url
    #free_ram_space=float((re.search('tmpfs(.+?)\n',os.popen("df").read()).group(1)).split()[2]) #get free ram space in kbytes

    

    online_fw_hw_dict=get_online_fw_hw(onos_online_server_url,current_hw,router_sn)
    online_fw=online_fw_hw_dict["online_fw"]
    online_update_folder=online_fw_hw_dict["folder"]

    #print "fw",fw
   
    #print "current_local_fw",current_local_fw
    if ( (float(online_fw))>(float(current_local_fw)) ):   # online fw is newer than the local one , so i update
      print("online fw is newer than the local one , so i update")
      try_number=5
      while (try_number>0): #retry 5 times to retrieve the file before to giveup
        md5_update_script_code=0 
        file_md5code=-1
        try:
          url_fw_download=onos_online_server_url+'updates/'+current_hw+"/"+online_update_folder+'/onos_update.pya'
          print(url_fw_download)
          python_update_script = urllib2.urlopen(url_fw_download) 
          python_script=python_update_script.read() 
          python_update_script.close()
          os.system("mkdir -p "+base_path+"onos_update")
          os.system("rm -f "+base_path+"onos_update/onos_update.py")

          fo = open(base_path+"onos_update/onos_update.py", "wb")
          fo.write(python_script)
          fo.close()
          md5_update_script = urllib2.urlopen(onos_online_server_url+'updates/'+current_hw+'/md5sum_update_script.txt') 
          md5_update_script_code=(md5_update_script.read()).strip()
          md5_update_script.close()
          fo2 = open(base_path+"onos_update/md5sum_update_script.txt", "w")
          fo2.write(md5_update_script_code)
          fo2.close()
          file_md5code=os.popen("md5sum "+base_path+"onos_update/onos_update.py").read().split(" ")[0] 

        except Exception as e:
          print "error downloading the update script "
          print e.args 

        if md5_update_script_code!=file_md5code:
          print "md5_update_script_code is corrupted"
          print md5_update_script_code
          print "vs"
          print file_md5code
          if try_number==1:
            print "update failed,corrupted tar"
            quit()
          else:
            try_number=try_number-1
            continue     
 
        else: #the file is not corrupted
          print "updated script is ok"
          break

      try: 
        namespace={}     
        execfile(base_path+"onos_update/onos_update.py",globals(),namespace) #execute the python script

      except Exception as e:
        print "error1 execfile(file_path,globals(),namespace) #executing the python script  "
        print e.args 



    else: # onos is already updated
      print ("onos is already updated, current_local_fw:"+current_local_fw+",online_fw:"+online_fw)

  else:
    print ("config disable automatic update")  




