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
# 		for key in self.currentValues.keys():
# 			self.keyDictionary[counter] = key
# 			counter+=1

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
		self.clearColumns(4)
		amount = tk.StringVar()
		e = tk.Entry(self.tkBudget, width = 5, textvariable = amount)
		e.grid(row=1,column=4)
		button = tk.Button(self.tkBudget, text="Log", command = lambda: self.logExpense_helper(e.get(),category, addition))
		button.grid(row=1,column=5)
			
	def logExpense_helper(self, amount,category,addition):
		try:
			amount = float(amount)
			if addition:
				amount*=-1
			self.currentValues[category] -= round(amount,2)
			self.displayBudget()
		
		except:
			None

	def updateCategory(self, category):
		self.displayBudget()
		label = tk.Label(self.tkBudget,text="Selected Category: " + category)
		label.grid(row=0,column=3)
		button=tk.Button(self.tkBudget, text= "Log Expense", command= lambda: self.logExpense(category))
		button.grid(row=1,column=3)
		button = tk.Button(self.tkBudget, text="Log One-time Windfall", command= lambda: self.logExpense(category, True))
		button.grid(row=2,column=3)
		button=tk.Button(self.tkBudget, text= "Update Monthly Allowance", command = lambda: self.changeBudget(category))
		button.grid(row=3,column=3)
		button = tk.Button(self.tkBudget, text= "Delete this category", command = lambda: self.deleteCategory(category))
		button.grid(row=4, column = 3)
	
	def addCategory(self):
		self.clearColumns(3)
		label = tk.Label(self.tkBudget, text="Enter name of category:")
		label.grid(row=0,column=3)
		name = tk.StringVar()
		e1 = tk.Entry(self.tkBudget, textvariable=name)
		e1.grid(row=1,column=3)
		label = tk.Label(self.tkBudget, text="Enter monthly budget:")
		label.grid(row=3,column=3)
		amount = tk.StringVar()
		e2 = tk.Entry(self.tkBudget, textvariable=amount)
		e2.grid(row=4,column=3)
		button = tk.Button(self.tkBudget, text = "Submit", command = lambda: self.addCategory_helper(e1.get(),e2.get()))
		button.grid(row=5,column=3)
		
	def addCategory_helper(self, name, amount):
		try:
			amount = float(amount)
			if name!="":
				self.budget[name]=round(amount,2)
				self.currentValues[name]=round(amount*self.proportionalUpdate(),2)
			self.displayBudget()
		except:
			self.displayBudget()
	
	def clearFrame(self):
		gridItems = self.tkBudget.grid_slaves()
		for item in gridItems:
			item.destroy()
			
	def changeBudget(self, category):
		self.clearColumns(4)
		label = tk.Label(self.tkBudget,text="Current Monthly Budget: " + str(self.budget[category]))
		label.grid(row=0,column=4)
		amount = tk.StringVar()
		e = tk.Entry(self.tkBudget, width = 5, textvariable = amount)
		e.grid(row=1,column=4)
		button = tk.Button(self.tkBudget, text="Update", command = lambda: self.changeBudget_helper(e.get(),category))
		button.grid(row=2,column=4)
		
	def changeBudget_helper(self, amount, category):
		try:
			amount = float(amount)
			difference = amount-self.budget[category]
			adjustment = difference*self.proportionalUpdate()
			self.logExpense_helper(adjustment, category, True)
			self.budget[category]=round(amount,2)
		except:
			None
					
	def deleteCategory(self,category):
		self.clearColumns(4)
		label = tk.Label(self.tkBudget,text="Are you sure?")
		label.grid(row=0,column=4)
		button = tk.Button(self.tkBudget, text="Yes", command= lambda: self.deleteCategory_helper(category))
		button.grid(row=1, column=4)
		
	def deleteCategory_helper(self, category):
		del self.budget[category]
		del self.currentValues[category]
		self.displayBudget()
     	
	def displayBudget(self):
		self.clearFrame()
		frame = tk.Frame(self.tkBudget)
		frame.grid(row=0,column=0,sticky='nsew')
		for col in range(3):
			tk.Grid.columnconfigure(frame,col,weight=1)
			for row in range(len(self.currentValues.keys())):
				tk.Grid.rowconfigure(frame,row,weight=1)
		label=tk.Label(frame, text = "Category")
		label.grid(row = 0, column = 0,sticky='nsew')
		label = tk.Label(self.tkBudget, text = "Available Balance")
		label.grid(row=0,column=1,sticky='nsew')
		label = tk.Label(self.tkBudget, text = "Monthly Allowance")
		label.grid(row=0,column=2,sticky='nsew')
		counter = 1
		category = tk.StringVar()
		for key in self.currentValues:
			button=tk.Radiobutton(self.tkBudget,indicatoron = 0, text=" " + key, variable=category, value = key, anchor="w",relief="groove", command = lambda key=key: self.updateCategory(category.get()))
			button.grid(row=counter,column=0,sticky='nsew')
			label = tk.Label(self.tkBudget, text = "$"+str(round(self.currentValues[key],2)), relief="groove")
			label.grid(row=counter, column=1,sticky='nsew')
			label = tk.Label(self.tkBudget, text = "$"+str(round(self.budget[key],2)), relief="groove")
			label.grid(row=counter, column=2,sticky='nsew')
			counter+=1
		button = tk.Button(self.tkBudget, text = "Add new category", command = self.addCategory)
		button.grid(row=counter, column=0)
	
# 	def setCurCategory(
	def clearColumns(self, column):
		for item in self.tkBudget.grid_slaves():
			if int(item.grid_info()["column"]) >= column:
				item.grid_forget()
	
	def saveValues(self):
		saveFile = open('currentTotals.txt', 'w')
		for key in self.currentValues.keys():
			string = key + ","+str(self.currentValues[key])+'\n'
			saveFile.write(string)
		saveFile.close
		
	

if __name__ == '__main__':
	budget = tk.Tk()
	tk.Grid.rowconfigure(budget, 0, weight=1)
	tk.Grid.columnconfigure(budget, 0, weight=1)
	FT = FinanceTracker(budget)
	FT.displayBudget()

	budget.mainloop()

	FT.saveValues()
	FT.saveBudget()
	
	
	
# root = tkinter.Tk()

# open file
# with open("test.csv", newline = "") as file:
#    reader = csv.reader(file)

def categoryClick():
	test = tk.TK()
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
	
