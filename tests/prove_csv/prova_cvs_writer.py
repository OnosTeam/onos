import csv
import sys


fr = open("in.csv", 'rt')

csv_list=[]
try:
    reader = csv.reader(fr)
    for row in reader:
        print row
        csv_list.append(row) 
finally:
    fr.close()



print(csv_list)


fw = open("out.csv", 'wt')

try:
  writer = csv.writer(fw)
  for row_to_write in csv_list:
    print row_to_write
    if len (row_to_write)==5:
      writer.writerow((row_to_write[0],row_to_write[1],row_to_write[2],row_to_write[3],row_to_write[4])) 
    else:
      writer.writerow((row_to_write[0],row_to_write[1])) 
finally:
  fw.close()

print open(sys.argv[1], 'rt').read()

