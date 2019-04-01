import tkinter as tk
import csv
import datetime
import pandas as pd

class FinanceTracker:

	def __init__(self, tkBudget):
		self.tkBudget = tkBudget
		self.budgetFrame = tk.Frame(self.tkBudget)
		self.budgetFrame.grid(row=0,column=0,sticky='nsew')
		self.commandFrame = tk.Frame(self.tkBudget)
		self.commandFrame.grid(row=1,column=0,sticky='nsew')
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
			None

		self.update()
		self.curCategory = None


		

	
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
		try:
			lastUpdate = open("last_update.txt", "r")
		except:
			return False
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
			
	def logExpense(self, addition=False):
		self.clearColumns(4)
		amount = tk.StringVar()
		e = tk.Entry(self.tkBudget, width = 5, textvariable = amount)
		e.grid(row=1,column=4)
		button = tk.Button(self.tkBudget, text="Log", command = lambda: self.logExpense_helper(e.get(),self.curCategory, addition))
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

	def updateCategory(self):
		for col in range(1):
			tk.Grid.columnconfigure(self.commandFrame,col,weight=1)
			for row in range(4):
				tk.Grid.rowconfigure(self.commandFrame,row,weight=1)

		button=tk.Button(self.commandFrame, text= "Log Expense", command= lambda: self.logExpense())
		button.grid(row=0,column=0,sticky='nsew')
		button = tk.Button(self.commandFrame, text="Log One-time Windfall", command= lambda: self.logExpense(True))
		button.grid(row=1,column=0,sticky='nsew')
		button=tk.Button(self.commandFrame, text= "Update Monthly Allowance", command = lambda: self.changeBudget())
		button.grid(row=2,column=0,sticky='nsew')
		button = tk.Button(self.commandFrame, text= "Delete this category", command = lambda: self.deleteCategory())
		button.grid(row=3, column = 0,sticky='nsew')
	
	def addCategory(self):
		self.clearColumns(3)
		addWindow = tk.Tk()
		addWindow.title("Add a Category")
		label = tk.Label(addWindow, text="Enter name of category:")
		label.grid(row=0,column=0)
		name = tk.StringVar()
		e1 = tk.Entry(addWindow, textvariable=name)
		e1.grid(row=1,column=0)
		label = tk.Label(addWindow, text="Enter monthly budget:")
		label.grid(row=3,column=0)
		amount = tk.StringVar()
		e2 = tk.Entry(addWindow, textvariable=amount)
		e2.grid(row=4,column=0)
		button = tk.Button(addWindow, text = "Submit", command = lambda: self.addCategory_helper(e1.get(),e2.get(),addWindow))
		button.grid(row=5,column=0)
# 		addWindow.bind('<Return>', self.addCategory_helper(e1.get(),e2.get(),addWindow))
		
	def addCategory_helper(self, name, amount,window):
		try:
			amount = float(amount)
			if name!="":
				self.budget[name]=round(amount,2)
				self.currentValues[name]=round(amount*self.proportionalUpdate(),2)
			window.destroy()
			self.displayBudget()
		except:
			self.displayBudget()
	
	def clearFrame(self):
		gridItems = self.tkBudget.grid_slaves()
		for item in gridItems:
			item.destroy()
			
	def changeBudget(self):
		amount = tk.StringVar()
		e = tk.Entry(self.tkBudget, width = 5, textvariable = amount)
		e.grid(row=1,column=4)
		button = tk.Button(self.tkBudget, text="Update", command = lambda: self.changeBudget_helper(e.get(),self.curCategory))
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
					
	def deleteCategory(self):
		confirmWindow = tk.Tk()
		confirmWindow.title("Confirmation")
		label = tk.Label(confirmWindow,text="Are you sure?")
		label.grid(row=0,column=0)
		button = tk.Button(confirmWindow, text="Yes", command= lambda: self.deleteCategory_helper(self.curCategory,confirmWindow))
		button.grid(row=1, column=0)
		
	def deleteCategory_helper(self, category,window):
		del self.budget[category]
		del self.currentValues[category]
		window.destroy()
		self.budgetFrame.destroy()
		self.displayBudget()
     	
	def displayBudget(self):
		self.budgetFrame = tk.Frame(self.tkBudget)
		self.budgetFrame.grid(row=0,column=0,sticky='nsew')
		for col in range(3):
			tk.Grid.columnconfigure(self.budgetFrame,col,weight=1)
			for row in range(len(self.currentValues.keys())+1):
				tk.Grid.rowconfigure(self.budgetFrame,row,weight=1)
		label=tk.Label(self.budgetFrame, text = "Category")
		label.grid(row = 0, column = 0,sticky='nsew')
		label = tk.Label(self.budgetFrame, text = "Available Balance")
		label.grid(row=0,column=1,sticky='nsew')
		label = tk.Label(self.budgetFrame, text = "Monthly Allowance")
		label.grid(row=0,column=2,sticky='nsew')
		counter = 1
		for key in self.currentValues:
			button=tk.Radiobutton(self.budgetFrame,indicatoron = 0, text=" " + key, value = key, anchor="w",relief="groove", command = lambda key=key: self.setCurCategory(key))
			button.grid(row=counter,column=0,sticky='nsew')
			label = tk.Label(self.budgetFrame, text = "$"+str(round(self.currentValues[key],2)), relief="groove")
			label.grid(row=counter, column=1,sticky='nsew')
			label = tk.Label(self.budgetFrame, text = "$"+str(round(self.budget[key],2)), relief="groove", anchor="e")
			label.grid(row=counter, column=2,sticky='nsew')
			counter+=1
		button = tk.Button(self.budgetFrame, text = "Add new category", command = self.addCategory)
		button.grid(row=counter, column=0)
	
	def setCurCategory(self, category):
		self.curCategory = category

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
	budget.title("My Budget Tracker")
	for row in range(3):
		tk.Grid.rowconfigure(budget, row, weight=1)
		for col in range(1):
			tk.Grid.columnconfigure(budget, col, weight=1)
	FT = FinanceTracker(budget)
	FT.displayBudget()
	FT.updateCategory()

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
	
