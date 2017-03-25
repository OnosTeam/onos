# -*- coding: UTF-8 -*-

import os,os.path,urllib2,re

global base_path
global onos_online_server_url
global current_local_fw
global current_hw











default_online_server_url="http://www.myonos.com/onos/"


if (os.path.exists("/sys/class/gpio")==1) : #if the directory exist ,then the hardware has embedded IO pins
  discovered_running_hardware="embedded_pc_board"
  base_path="/bin/onos/"
else:
  discovered_running_hardware="pc"  #the hardware has not IO pins
  base_path=os.getcwd()+"/"






def getCurrent_local_fw_hw(file_path):
  try:
    current_version_file=open(file_path+"fw_version.txt",'r') 
    current_version=current_version_file.read()
    current_version_file.close()

    current_local_fw=current_version[0:4] 

    current_hw=re.search('_(.+?)#',current_version).group(1)  #find the hw ("glinet") from current_version
    current_files_number=re.search('#files:(.+?)#',current_version).group(1) 
  except:
    current_local_fw="999"
    current_hw="glinet"
    current_files_number="0"





  return({"current_local_fw":current_local_fw,"current_hw":current_hw,"current_files_number":current_files_number})







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
          
  try:
    md5_file = open(base_path+"onos_update/md5sum_update_script.txt",'r')  
    md5_update_script_code=(md5_file.read()).strip()   #get the string and delete the \n
    md5_file.close()
    file_md5code=os.popen("md5sum "+base_path+"onos_update/onos_update.py").read().split(" ")[0] 
    downloaded_version_file=open(base_path+"onos_update/fw_version.txt",'r') 
    downloaded_version=downloaded_version_file.read()
    downloaded_version_file.close()
    current_downloaded_fw=downloaded_version[0:4] 
    current_downloaded_hw=re.search('_(.+?)#',downloaded_version).group(1)  #find the hw ("glinet") from downloaded_version
    current_downloaded_files_number=re.search('#files:(.+?)#',downloaded_version).group(1) 



  except:

    print "the directory/file update do not exist or are corrupted"
    current_downloaded_fw="0"
    current_downloaded_hw="glinet"
    downloaded_files_number="0"
    md5_update_script_code=-4
    file_md5code=-5
    current_downloaded_files_number="0"



  return({"current_downloaded_fw":current_downloaded_fw,"current_downloaded_hw":current_downloaded_hw,"current_downloaded_files_number":current_downloaded_files_number,"md5_update_script_code":md5_update_script_code,"file_md5code":file_md5code})



#if os.path.isfile(file_path):  #if the directory and the  file exist...


def get_online_fw_hw(version_url,current_hw):

  """
  | Get and parse the current online fw hw version
  |
  |
  """


  try:
    print "I try to download the current fw version number"
    response = urllib2.urlopen(version_url+'updates/'+current_hw+'/fw_version.txt')
    #the url will be like: http://www.myonos.com/onos/updates/glinet/fw_version.txt
    version_txt=response.read()  #now i got the txt file 
    #example: 5.15_glinet#files:226#

    online_fw=version_txt[0:4]
    online_hw=re.search('_(.+?)#',version_txt).group(1)  #find the hw from version_txt
    online_files_number=re.search('files:(.+?)#',version_txt).group(1) 
    


  except Exception, e :
    print "error, maybe there is not internet connection"
    print e.args 
    online_fw=0
    online_hw="glinet"
    online_files_number="0"
  print ("online_fw:"+online_fw)
  return({"online_fw":online_fw,"online_hw":online_hw,"online_files_number":online_files_number})



current_local_fw=getCurrent_local_fw_hw(base_path)["current_local_fw"]

md5_update_script_code=get_fw_hw_in_onos_update_folder(base_path)["md5_update_script_code"]

file_md5code=get_fw_hw_in_onos_update_folder(base_path)["file_md5code"]

current_downloaded_fw=get_fw_hw_in_onos_update_folder(base_path)["current_downloaded_fw"]


if (md5_update_script_code==file_md5code)&(float(current_local_fw)<float(current_downloaded_fw)):  #if the script exist and is not corrupted and the new fw version is newer than the current one




  namespace={}    
  try:
    global_file = open(base_path+"scripts_folder/globalVar.py",'r')  
    text=global_file.read()
    global_file.close()
    onos_online_server_url=re.search('onos_online_site_url="(.+?)"',text).group(1)  #find the domain from globalVar.py

  except:
    onos_online_server_url=default_online_server_url
   




  try: 
    execfile(file_path,globals(),namespace) #execute the python script
  
  except Exception, e :
    print "error0 execfile(file_path,globals(),namespace) #executing the python script  "
    print e.args 


else:#the directory doesn't exist i check if the enable_onos_auto_update is yes

  
  try:
    cfg_file = open(base_path+"scripts_folder/config_files/cfg.json",'r')  
    text0=cfg_file.read()
    cfg_file.close()

  except:
    text0=''' enable_onos_auto_update": "yes" '''


 
  if text0.find('''enable_onos_auto_update": "yes"''')!= -1:  #if the auto update is enabled

    try:
      global_file = open(base_path+"scripts_folder/globalVar.py",'r')  
      text=global_file.read()
      global_file.close()
  
      onos_online_server_url=re.search('onos_online_site_url="(.+?)"',text).group(1)  #find the domain from globalVar.py

    #example: 5.15_glinet#files:226#

      current_local_fw=getCurrent_local_fw_hw(base_path)["current_local_fw"]
      current_hw=getCurrent_local_fw_hw(base_path)["current_hw"]
      current_files_number=getCurrent_local_fw_hw(base_path)["current_files_number"]
    
    except:

      current_local_fw="3.15"
      current_hw="glinet"
      current_files_number="0"
      onos_online_server_url=default_online_server_url
    #free_ram_space=float((re.search('tmpfs(.+?)\n',os.popen("df").read()).group(1)).split()[2]) #get free ram space in kbytes

    


    online_fw=get_online_fw_hw(onos_online_server_url,current_hw)["online_fw"]


    #print "fw",fw
   
    #print "current_local_fw",current_local_fw
    if ( (float(online_fw))>(float(current_local_fw)) ):   # online fw is newer than the local one , so i update

      try_number=5
      while (try_number>0): #reatry 5 times to retrieve the file before to giveup
        md5_update_script_code=0 
        file_md5code=-1
        try:
          print onos_online_server_url+'updates/'+current_hw+'/onos_update.pya'
          python_update_script = urllib2.urlopen(onos_online_server_url+'updates/'+current_hw+'/onos_update.pya') 
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


        except Exception, e :
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

      except Exception, e :
        print "error1 execfile(file_path,globals(),namespace) #executing the python script  "
        print e.args 



    else: # onos is already updated
      print ("onos is already updated, current_local_fw:"+current_local_fw)

  else:
    print ("config disable automatic update")  




