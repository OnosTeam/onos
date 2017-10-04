import csv
import sys

#for now you can use https://plot.ly/create/ to view the csv


row_to_write=['5', 'e', '08/05/2007', '00.00.00', '1507141842']

try:
  with open("out.csv", 'a') as f:
    print row_to_write
    writer = csv.writer(f)
    if len (row_to_write)==5:
      writer.writerow((row_to_write[0],row_to_write[1],row_to_write[2],row_to_write[3],row_to_write[4])) 
    else:
      writer.writerow((row_to_write[0],row_to_write[1])) 
finally:
  print ""



