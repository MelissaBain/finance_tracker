import datetime
import pandas as pd

class FinanceTracker:

	def __init__(self):
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
		print('''\n-----------------------------------------
   Welcome to your new Fiance Tracker!
-----------------------------------------\n''')
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
		
		print('''--------------------------------------------------------------------------------------------------------------
For each category, you will be asked to input a number that will serve as the monthly budget for that category.
Enter either an integer or decimal and then press enter after each prompt.
--------------------------------------------------------------------------------------------------------------''')
		self.setBudget()
		self.updateDate()
		print('''\nYour category totals will automatically be updated upon the first of the next month.
They have been initialized at the appropriate fraction equal to how far into this current month we are.
You always have the chance to do one-time deposites to account for previous savings, unexpected windfalls, etc.''')
		
		print('''---------------------------------------------------------------------------------------
Congrats! Your finance tracker is now configured. 
Press enter to be directed to the screen you will usually see upon opening your tracker.
---------------------------------------------------------------------------------------''')
		input()
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		
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
		return (totalDays-self.curDate)/totalDays
	
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
			
	def logExpense(self):
		print("Please enter one of the following categories:\n")
		for key in self.keyDictionary.keys():
			print("Type ", key, " for category ", self.keyDictionary[key])
		key = input("\nWhich number category would you like?\n")
		category = self.keyDictionary[int(key)]
		amount = float(input("How much did you spend?\n"))
		self.currentValues[category] -= amount 
		self.currentValues[category] = round(self.currentValues[category],2)

	def displayBudget(self):
		print("\n------------------------------------------------------\nCurrently you have the following saved in each category:")
		for key in self.currentValues:
			print(key, ": $", self.currentValues[key])
		print("------------------------------------------------------\n")
	
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
	FT = FinanceTracker()
	FT.displayBudget()
	keepGoing = True
	updated = False
	
	maintenanceNeeded = input('''\nDo you have any structural changes to make?
Examples:
	- viewing your monthly allowances
	- adding/deleting a budget category
	- changing the monthly budget for a category
	- recording a one-time addition to a category
If yes, please enter 'y'. Otherwise just press enter.\n''')
	
	while maintenanceNeeded == 'y':
		num = input('''\nPress the number corresponding to the action you wish to perform:
(1) - Add a category to your budget
(2) - Delete a category in your budget
(3) - Change the monthly allocation for a category
(4) - Record a one-time addition to a category
(5) - View your monthly allowances\n''')
		FT.maintain(num)
		if int(num)<5:
			print("After your updates, your budget stands as follows:")
			FT.displayBudget()
		maintenanceNeeded = input("Do you have any further maintenance? If so, enter 'y'. Otherwise, just press enter to continue.\n")
	
	while keepGoing:
		response = input("Do you have expenses to log? (y/n)\n")
		if response == "y":
			FT.logExpense()
			updated = True
		else:
			keepGoing=False

	if updated:
		print("After your updates, your budget stands as follows:")
		FT.displayBudget()

	FT.saveUpdates()