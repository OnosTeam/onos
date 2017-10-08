import csv
import sys
import time
import datetime
#for now you can use https://plot.ly/create/  or  http://app.rawgraphs.io/  to view the csv

day=str(datetime.datetime.today().day)
month=str(datetime.datetime.today().month)
year=str(datetime.datetime.today().year)
hours=str(datetime.datetime.today().hour)
minutes=str(datetime.datetime.today().minute)
seconds=str(datetime.datetime.today().second)
print("minutes")
print(minutes)
print("seconds")
print(seconds)

timestamp=str(time.time())[0:10]
#row_to_write=[self.status, '08/05/2007', '00.00.00', '1507141842','admin']
row_to_write=['1',day+'/'+month+'/'+year, hours+'.'+minutes+'.'+seconds ,timestamp,'user']

#row_to_write=['1', '08/05/2007', '00.00.00', '1507141842','admin']

try:
  with open("out.csv", 'a') as f:
    print row_to_write
    writer = csv.writer(f)
    writer.writerow(row_to_write) 

finally:
  print ""



