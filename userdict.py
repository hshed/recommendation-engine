'''
Created on Mar 5, 2013

@author: Hrishikesh
'''
import csv
import re
import time

s = time.time()
with open('BX-Users.csv', mode='r') as infile:
    reader = csv.reader(infile)
    reader.next()
    usersdict = [re.search(r"\d+",row[0]).group() for row in reader]
print time.time() - s, 'seconds'