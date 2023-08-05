import json
import io
import requests
import pandas as pd
import re
import heapq
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

vegetableName = []
vegetableQuantity = []
vegetableMrp = []

fruitName = []
fruitQuantity = []
fruitMrp = []

header = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
	'Cache-Control': 'no-cache, must-revalidate'
	}



def convertQuantity(mrp, wRange, baseUnit):
	if (baseUnit=='kg') or wRange.find("kg")!=-1 or wRange.find("Kg")!=-1 or wRange.find("KG")!=-1:
		p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
		if re.search(p, wRange) is not None:
			weights = [float(catch[0]) for catch in re.finditer(p, wRange)]

			avg = sum(weights) / len(weights)
			if(len(weights)>2):
				avg = sum(heapq.nlargest(2, weights)) / 2

			weightInKilograms = avg
			price = float(mrp) / weightInKilograms
			price = round(price, 2)
			return price
	
	else:
		p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
		if re.search(p, wRange) is not None:
			weights = [float(catch[0]) for catch in re.finditer(p, wRange)]
			
			avg = sum(weights) / len(weights)
			if(len(weights)>2):
				avg = sum(heapq.nlargest(2, weights)) / 2

			weightInKilograms = avg / 1000
			price = float(mrp) / weightInKilograms
			price = round(price, 2)
			return price
	
def convertWeight(mrp, w, baseUnit):
	if(baseUnit=='kg'):
		p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
		if re.search(p, w) is not None:
			weights = [float(catch[0]) for catch in re.finditer(p, w)]
			avg = sum(weights) / len(weights)
			weightInKilograms = avg
			price = float(mrp) / weightInKilograms
			price = round(price, 2)
			return price
		
	else:
		p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
		if re.search(p, w) is not None:
			weights = [float(catch[0]) for catch in re.finditer(p, w)]
			avg = sum(weights) / len(weights)
			weightInKilograms = avg / 1000
			price = float(mrp) / weightInKilograms
			price = round(price, 2)
			return price
	

def getAllVegatablesFromPage1():
	url = 'https://www.bigbasket.com/custompage/sysgenpd/?type=pc&slug=fresh-vegetables&page=2&tab_type=["all"]&sorted_on=popularity&listtype=pc'
	result = requests.get(url, headers=header)
	vegetablesData = json.loads(result.text)
	numberOfPages = vegetablesData['tab_info'][0]['product_info']['tot_pages']
	vegetablesData = vegetablesData['tab_info'][0]['product_info']['products']

	for prod in vegetablesData:
		#filter out combo products
		if(prod['w']!='Combo'):
			vegetableName.append(prod['p_desc'])
			vegetableQuantity.append('1 kg')

			#get mrp for products with weight range
			if(prod['pack_desc']):
				price = convertQuantity(prod['mrp'], prod['pack_desc'], prod['base_unit'])
				vegetableMrp.append(price)
		
				#get mrp for product with variable weight
			else:
				# if base unit is listed
				if('base_unit' in prod):
					vegetableMrp.append(convertWeight(prod['mrp'], prod['w'], prod['base_unit']))
				else:
					vegetableMrp.append(round(float(prod['mrp']),2))
				
def getAllVegetables():
	#get data from statically generated first page
	getAllVegatablesFromPage1()

	#get data from dynamically generated following pages
	for i in range(2,100):
		url = 'https://www.bigbasket.com/product/get-products/?slug=fresh-vegetables&page='+ str(i) +'&tab_type=[%22all%22]&sorted_on=popularity&listtype=pc'
		result = requests.get(url, headers=header)
		vegetablesData = json.loads(result.text)
		vegetablesData = vegetablesData["tab_info"]["product_map"]["all"]["prods"]
		
		#break if no more pages exist
		if len(vegetablesData)==0:
			break

		for prod in vegetablesData:
		#filter out combo products
			if(prod['w']!='Combo'):
				vegetableName.append(prod['p_desc'])
				vegetableQuantity.append('1 kg')

				#get mrp for products with weight range
				if(prod['pack_desc']):
					price = convertQuantity(prod['mrp'], prod['pack_desc'], prod['base_unit'])
					vegetableMrp.append(price)

				#get mrp for product with variable weight
				else:
					# if base unit is listed
					if('base_unit' in prod):
						vegetableMrp.append(convertWeight(prod['mrp'], prod['w'], prod['base_unit']))
					else:
						vegetableMrp.append(round(float(prod['mrp']),2))

def getAllFruitsFromPage1():
	url = 'https://www.bigbasket.com/custompage/sysgenpd/?type=pc&slug=fresh-fruits&page=2&tab_type=["all"]&sorted_on=popularity&listtype=pc'
	result = requests.get(url, headers=header)
	fruitsData = json.loads(result.text)
	numberOfPages = fruitsData['tab_info'][0]['product_info']['tot_pages']
	fruitsData = fruitsData['tab_info'][0]['product_info']['products']

	for prod in fruitsData:
		#filter out combo products
		if(prod['w']!='Combo'):
			fruitName.append(prod['p_desc'])
			fruitQuantity.append('1 kg')

			#get mrp for products with weight range
			if(prod['pack_desc']):
				if('base_unit' in prod):
					price = convertQuantity(prod['mrp'], prod['pack_desc'], prod['base_unit'])
					fruitMrp.append(price)
				else:
					fruitMrp.append(prod['mrp'])
		
				#get mrp for product with variable weight
			else:
				# if base unit is listed
				if('base_unit' in prod):
					fruitMrp.append(convertWeight(prod['mrp'], prod['w'], prod['base_unit']))
				else:
					fruitMrp.append(round(float(prod['mrp']),2))
				
def getAllFruits():
	#get data from statically generated first page
	getAllFruitsFromPage1()

	#get data from dynamically generated following pages
	for i in range(2,100):
		url = 'https://www.bigbasket.com/product/get-products/?slug=fresh-fruits&page='+ str(i) +'&tab_type=[%22all%22]&sorted_on=popularity&listtype=pc'
		result = requests.get(url, headers=header)
		fruitsData = json.loads(result.text)
		fruitsData = fruitsData["tab_info"]["product_map"]["all"]["prods"]
		
		#break if no more pages exist
		if len(fruitsData)==0:
			break

		for prod in fruitsData:
		#filter out combo products
			if(prod['w']!='Combo'):
				fruitName.append(prod['p_desc'])
				fruitQuantity.append('1 kg')

				#get mrp for products with weight range
				if(prod['pack_desc']):
					if('base_unit' in prod):
						price = convertQuantity(prod['mrp'], prod['pack_desc'], prod['base_unit'])
						fruitMrp.append(price)
					
					else :
						price = convertQuantity(prod['mrp'], prod['pack_desc'], "g")
						fruitMrp.append(price)
					

				#get mrp for product with variable weight
				else:
					# if base unit is listed
					if('base_unit' in prod):
						fruitMrp.append(convertWeight(prod['mrp'], prod['w'], prod['base_unit']))
					else:
						fruitMrp.append(round(float(prod['mrp']),2))

# getAllFruits()
# getAllVegetables()


def createCSV(path):
	vegetableDataTable = {'Product':vegetableName, 'Quantity':vegetableQuantity, 'MRP':vegetableMrp}
	df = pd.DataFrame.from_dict(vegetableDataTable)
	df.to_csv(os.path.join(path,r'vegetables.csv'))

	fruitDataTable = {'Product':fruitName, 'Quantity':fruitQuantity, 'MRP':fruitMrp}
	df = pd.DataFrame.from_dict(fruitDataTable)
	df.to_csv(os.path.join(path,r'fruits.csv'))

# createCSV()
# print("Added to CSV")

def addToFirestore():
	cred = credentials.Certificate("bigbasket-df971-firebase-adminsdk-l994g-a722739347.json")


	firebase_admin.initialize_app(cred)
	db = firestore.client()

	vegatableData = {
		'name': vegetableName,
		'quantity': vegetableQuantity,
		'mrp': vegetableMrp,
		'date': datetime.today().strftime('%Y-%m-%d'),
	}

	fruitData = {
		'name': fruitName,
		'quantity': fruitQuantity,
		'mrp': fruitMrp,
		'date': datetime.today().strftime('%Y-%m-%d'),
	}

	doc_ref = db.collection("bb_vegetables").document(datetime.today().strftime('%Y-%m-%d'))
	doc_ref.set(vegatableData)

	doc_ref = db.collection("bb_fruits").document(datetime.today().strftime('%Y-%m-%d'))
	doc_ref.set(fruitData)

# addToFirestore()
# print("Added to Firestore")

root = Tk()
root.title('BigBasket Webscraper')
root.geometry('500x200')

def addToCsvAndFirebase(path):
	getAllFruits()
	getAllVegetables()
	createCSV(path)
	addToFirestore()
	newLabel = Label(root, text='Added data to Firebase\nGenerated CSV successfully').pack()

def addToFirebase():
	getAllFruits()
	getAllVegetables()
	addToFirestore()
	newLabel = Label(root, text='Added data to Firebase').pack()

check = IntVar()
checkButton = Checkbutton(root, text="Generate CSV", variable=check, pady=5).pack()



def handleClick():
	label1 = Label(root, text='Loading...', pady=10).pack()
	checkStatus=check.get()
	if checkStatus==1:
		pathSelected = filedialog.askdirectory()
		addToCsvAndFirebase(pathSelected)
	else:
		addToFirebase()
	

generateButton = Button(root, text="Get data", command=handleClick, padx=100, pady=5).pack()

root.mainloop()