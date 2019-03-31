import tkinter as tk
import csv
import datetime
import pandas as pd

class FinanceTracker:

	def __init__(self, tkBudget):
		self.tkBudget = tkBudget
		now = datetime.datetime.now()
		self.curDate = now.day
		self.curMonth = now.month
		self.curYear = now.year
		self.currentValues = {}
		self.keyDictionary = {}
		self.budget = {}
		try:
			self.readSavings()
			self.loadBudget()
		except FileNotFoundError:
			self.configure()
			self.readSavings()
			self.loadBudget()
		self.update()

	def configure(self):
		
		categories = input("Please type the budget categories you wish to track, separated by a comma. Press enter when done.\n")
		categories = [x.strip() for x in categories.split(',')]
		for category in categories:
			self.currentValues[category] = 0
		
		corrections = 'y'
		while corrections == 'y':
		
			print("\nThese are the categories you entered:\n",list(self.currentValues.keys()))
			corrections = input("\nIs there anything you need to change or add? If yes, type 'y' & press enter. Otherwise just press enter.\n")
			if corrections == 'y':
				deletions = input("Are there any categories you wish to delete? (You will have the chance to add replacements shortly.)\nIf yes, type 'y' press enter. Otherwise just press enter.\n")
				if deletions == 'y':
					categoryToDelete = input("What category would you like to delete? Please type the name as previously recorded and then press enter.\n")
					if categoryToDelete in self.currentValues: 
						del self.currentValues[categoryToDelete]
				additions = input("Are there any categories you wish to add? If so enter them separated by commas & press enter. Otherwise just press enter.\n")
				if additions!= "":
					additions = [x.strip() for x in additions.split(',')]
					for addition in additions:
						self.currentValues[addition]=0
		
		self.setBudget()
		self.updateDate()
		
		
	def setBudget(self):
		monthDays = [31,28,31,30,31,30,31,31,30,31,30,31]
		leapYearDays = [31,29,31,30,31,30,31,31,30,31,30,31]
		if self.curYear%4 == 0:
			totalDays = leapYearDays[self.curMonth-1]
		else:
			totalDays = monthDays[self.curMonth-1]
		
		currentTotals = open('currentTotals.txt', 'w')
		budget = open('monthlyBudget.txt', 'w')
		
		proportion = self.proportionalUpdate()
		
		for key in self.currentValues.keys():
			budgetValue = input("\nHow much would you like to be contributed each month to "+key+"?\n")
			budget.write(key + ","+budgetValue+'\n')
			currentTotals.write(key + ","+str(round(float(budgetValue)*proportion,2))+'\n')

		currentTotals.close()
		budget.close()
	
	def proportionalUpdate(self):
		monthDays = [31,28,31,30,31,30,31,31,30,31,30,31]
		leapYearDays = [31,29,31,30,31,30,31,31,30,31,30,31]
		if self.curYear%4 == 0:
			totalDays = leapYearDays[self.curMonth-1]
		else:
			totalDays = monthDays[self.curMonth-1]
		return (totalDays-self.curDate+1)/totalDays
	
	def readSavings(self):
		with open("currentTotals.txt", 'r') as f:
			for line in f:
				items = line.split(",")
				key, values = items[0], items[1]
				values = float(values.strip("\n"))
				self.currentValues[key] = values
		counter = 0
		for key in self.currentValues.keys():
			self.keyDictionary[counter] = key
			counter+=1

	def update(self):
		keepUpdating = self.checkDate()
		if keepUpdating:
			self.loadBudget()
			for key in self.budget.keys():
				self.currentValues[key] += self.budget[key]

	def loadBudget(self):
		self.budget = {}
		with open("monthlyBudget.txt", 'r') as f:
			for line in f:
				items = line.split(",")
				key, values = items[0], items[1]
				values = float(values.strip("\n"))
				self.budget[key] = values
		
	def saveBudget(self):
		saveFile = open('monthlyBudget.txt', 'w')
		for key in self.budget.keys():
			string = key + ","+str(self.budget[key])+'\n'
			saveFile.write(string)
		saveFile.close
		
	def updateDate(self):
		lastUpdate = open("last_update.txt", "w")
		lastUpdate.write(str(self.curMonth) + " " + str(self.curYear))
		lastUpdate.close()
		
	def checkDate(self):
		lastUpdate = open("last_update.txt", "r")
		date = lastUpdate.read().split(" ")
		lastMonth = int(date[0])
		lastYear = int(date[1])
		monthsPassed = (self.curYear - lastYear) * 12 + self.curMonth - lastMonth
		if monthsPassed == 1:
			self.updateDate()
			return True
		elif monthsPassed == 0:
			return False
		else:
			print("Please manually update since over a month has passed")
			return False
			
	def logExpense(self, category, addition=False):
		amount = tk.StringVar()
		e = tk.Entry(self.tkBudget, textvariable = amount)
		e.grid(row=1,column=3)
		button = tk.Button(self.tkBudget, text="Log", command = lambda: self.logExpense_helper(float(e.get()),category, addition))
		button.grid(row=1,column=4)
			
	def logExpense_helper(self, amount,category,addition):
		if addition:
			amount*=-1
		self.currentValues[category] -= amount 
		self.currentValues[category] = round(self.currentValues[category],2)
		self.saveUpdates()
		self.displayBudget()

	def updateCategory(self, category):
		label = tk.Label(self.tkBudget,text="Category: " + category)
		label.grid(row=0,column=2)
		button=tk.Button(self.tkBudget, text= "Log Expense", command= lambda: self.logExpense(category))
		button.grid(row=1,column=2)
		button = tk.Button(self.tkBudget, text="Log One-time Windfall", command= lambda: self.logExpense(category, True))
		button.grid(row=2,column=2)
		button=tk.Button(self.tkBudget, text= "Update Monthly Allowance", command = lambda: self.changeBudget(category))
		button.grid(row=3,column=2)
		button = tk.Button(self.tkBudget, text= "Delete this category")
		button.grid(row=4, column = 2)
	
	def clearFrame(self):
		gridItems = self.tkBudget.grid_slaves()
		for item in gridItems:
			item.destroy()
			
	def changeBudget(self, category):
		print("change the ammount")
     	
	def displayBudget(self):
		self.clearFrame()
		counter = 0
		for key in self.currentValues:
			button=tk.Button(self.tkBudget, width=8,height=2, text=" " + key, anchor="w",relief="groove", command = lambda key=key: self.updateCategory(key))
			button.grid(row=counter,column=0)
			label = tk.Label(self.tkBudget, width=5, height=2, text = self.currentValues[key], relief="groove")
			label.grid(row=counter, column=1)
			counter+=1
		button = tk.Button(self.tkBudget, text = "Add new category")
		button.grid(row=counter, column=0)
		
	
	def saveUpdates(self):
		saveFile = open('currentTotals.txt', 'w')
		for key in self.currentValues.keys():
			string = key + ","+str(self.currentValues[key])+'\n'
			saveFile.write(string)
		saveFile.close
		
	def maintain(self, num):
		self.loadBudget()
		self.readSavings()
		
		if num == '1':
			key = input("Please enter the name of the category you wish to add.\n")
			budgetValue = float(input("Please enter the desired monthly budget.\n"))
			
			self.budget[key] = budgetValue
			proportion = self.proportionalUpdate()
			self.currentValues[key] = round(proportion*budgetValue,2)
			
		elif num == '2':
			key = input("Please enter the name of the category you wish to delete.\n")
			if key in self.currentValues: 
				del self.currentValues[key]
				del self.budget[key]
			else:
				print("Category not found!")
				
		elif num == '3':
			keepGoing = True
			while keepGoing:
				key = input("Please enter the name of the category you wish to change the budget for.\n")
				if key in self.budget:
					oldValue = self.budget[key]
					print("Your current monthly budget for " + key + " is: " + str(oldValue))
					amount = float(input("Please enter your new desired monthly budget for this category.\n"))
					self.budget[key] = amount
					proportion = self.proportionalUpdate()
					self.currentValues[key] += (amount-oldValue) * proportion
					keepGoing = False
				else:
					print("Category not found!")
			
		elif num == '4':
			keepGoing = True
			while keepGoing:
				key = input("Please enter the name of the category you wish to do a one-time addition to.\n")
				if key in self.currentValues:
					amount = float(input("Please input the ammount you would like to add and the press enter.\n"))
					self.currentValues[key] += amount
					keepGoing = False
				else:
					print("Category not found!")
		
		elif num == '5':
			print("-----------------------------\nYour allowance per month is:\n")
			for key in self.budget:
				print(key, ": ", self.budget[key])
			print("-----------------------------\n")

		self.saveBudget()
		self.saveUpdates()

if __name__ == '__main__':
	budget = tk.Tk()
	FT = FinanceTracker(budget)
	FT.displayBudget()
	keepGoing = True
	updated = False
	FT.saveUpdates()
	
	budget.mainloop()
	
	
# root = tkinter.Tk()

# open file
# with open("test.csv", newline = "") as file:
#    reader = csv.reader(file)

def categoryClick():
	test = tk.Tk()
	label=tk.Button(test, text ="yay")
	label.grid(row=0,column=0)
	
# with open("currentTotals.txt", 'r') as f:
# 	counter = 0
# 	for line in f:
# 		items = line.split(",")
# 		key, value = items[0], items[1]
# 		value = float(value.strip("\n"))
# 		label=tkinter.Button(root, width=8,height=2, text=" " + key, anchor="w",relief="groove", command = categoryClick)
# 		label.grid(row=counter,column=0)
# 		label = tkinter.Label(root, width=5, height=2, text = value, relief="groove")
# 		label.grid(row=counter, column=1)
# 		counter+=1
# 
# root.mainloop()
	
