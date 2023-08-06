import itertools
import hashlib
import json
import os
import csv

def MD5Decrypt(value):
	
	lookupvalue = value[:16] #Half the MD5 hash to match with hashes in dict

	letters = 'abcdefghijklmnopqrstuvwxyz' #Define letters to include the alphabet

	if not os.path.isfile("degenerated.txt"):
		
		#Generate the various lists, compile them in to one, output confirmation of creation
		oneChar = map(''.join, itertools.product(letters, repeat=1))
		twoChar = map(''.join, itertools.product(letters, repeat=2))
		threeChar = map(''.join, itertools.product(letters, repeat=3))
		fourChar = map(''.join, itertools.product(letters, repeat=4))
		fiveChar = map(''.join, itertools.product(letters, repeat=5))
		
		possibleValues = oneChar + twoChar + threeChar + fourChar + fiveChar
		print "List of possible combinations created..."
		
		with open("degenerated.txt", 'w') as f:
			json.dump(possibleValues, f) # Open degenerated.txt and write possibleValues to it
			
		print "... and written to file."

	else: 
		print "Values list found, moving on..."
		
	if not os.path.isfile("diction.csv"):
		
		with open("degenerated.txt", 'r') as f:
			possibleValues = json.load(f)
		
		fieldnames = ('md5', 'value')
		with open('diction.csv', 'wb') as myfile:
		
			myWriter = csv.DictWriter(myfile, fieldnames = fieldnames)
			headers = dict((n,n) for n in fieldnames)
			myWriter.writerow(headers)
			
			for value in possibleValues:
				myWriter.writerow({'md5' : hashlib.md5(value).hexdigest()[:16], 'value' : value})
			print "Hash list created and written to file."

	else: 
		print "Dictionary found, moving on..."
		
	with open('diction.csv', 'rb') as myfile:
		for row in csv.reader(myfile):
			if row[0] == lookupvalue:
				print "Key = " + row[1]
				return row[1]
				break
				