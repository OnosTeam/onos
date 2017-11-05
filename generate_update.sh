

mkdir generated_update/
mkdir generated_update/scripts_folder


cd scripts_folder/
cp -r $(ls  | grep -v -e docs -e generated_update -e .pyc  )  ../generated_update/scripts_folder/

#cp -r scripts_folder/* generated_update/scripts_folder/
cd ..
cp fw_version.txt generated_update/fw_version.txt
cp online_db/updates/onos_update.pya generated_update/onos_update.pya

cd generated_update/
tar -zcvf scripts_folder.tar.gz scripts_folder/

md5sum scripts_folder.tar.gz|cut -f 1 -d " " > md5sum_tar.txt

md5sum onos_update.pya|cut -f 1 -d " " > md5sum_update_script.txt


rm -rf scripts_folder
