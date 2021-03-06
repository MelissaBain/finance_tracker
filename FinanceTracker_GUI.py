#!/usr/bin/env python

"""Finance Tracker: A Cash-Envelope, Mint & Sinking Fund Hybrid Budget Tool"""

import tkinter as tk
import csv
import datetime
import pandas as pd
import copy

__author__ = "Melissa Bain"

class FinanceTracker:

	def __init__(self, tkBudget):
		"""Initialized the finance tracker by making GUI and loading/updating budget"""
	
		#set up GUI
		self.tkBudget = tkBudget
		self.outerVar = tk.IntVar(value=0)		
		#record current date
		now = datetime.datetime.now()
		self.curDate = now.day
		self.curMonth = now.month
		self.curYear = now.year
		
		#make data structures to store budget info
		self.currentValues = {}
		self.budget = {}
		
		#load data or initialize program if first time running
		try:
			self.readSavings()
			self.loadBudget()
		except FileNotFoundError:
			self.makeRecord()

		#update budget and initialize category
		self.update()
		self.curCategory = None

	def displayGUI(self):
		for child in self.tkBudget.winfo_children():
			child.destroy()
		self.budgetFrame = tk.Frame(self.tkBudget)
		self.budgetFrame.grid(row=0,column=0,sticky='nsew')
		self.commandFrame = tk.Frame(self.tkBudget)
		self.commandFrame.grid(row=1,column=0,sticky='nsew')
		self.displayBudget()
		self.displayChoices()
		
	def makeRecord(self):
		"""Makes a csv file to record each budget log"""
	
		with open("budgetRecord.csv", 'w') as budgetRecord:
			writer = csv.writer(budgetRecord, delimiter='\t')
			writer.writerow(['Date','Category','Amount','Comment'])
			
	
	def proportionalUpdate(self):
		"""Gives proportion of the month that still remains for budget allocation purposes"""
	
		monthDays = [31,28,31,30,31,30,31,31,30,31,30,31]
		leapYearDays = [31,29,31,30,31,30,31,31,30,31,30,31]
		if self.curYear%4 == 0: #calculate if leap year
			totalDays = leapYearDays[self.curMonth-1]
		else:
			totalDays = monthDays[self.curMonth-1]
		return (totalDays-self.curDate+1)/totalDays
	
	def readSavings(self):
		"""Reads and saves the current sinking fund totals to the current values dictionary"""
		
		with open("currentTotals.txt", 'r') as f:
			for line in f:
				items = line.split(",")
				key, values = items[0], items[1]
				values = float(values.strip("\n"))
				self.currentValues[key] = values
		counter = 0

	def update(self):
		"""Updates sinking fund totals if the 1st of the month has passed since the last update"""
	
		keepUpdating = self.checkDate()
		if keepUpdating:
			self.loadBudget()
			for key in self.budget.keys():
				self.currentValues[key] += self.budget[key]

	def loadBudget(self):
		"""Reads and saves the budget to the budget dictionary"""
	
		self.budget = {}
		with open("monthlyBudget.txt", 'r') as f:
			for line in f:
				items = line.split(",")
				key, values = items[0], items[1]
				values = float(values.strip("\n"))
				self.budget[key] = values
		
	def saveBudget(self):
		"""Writes budget and saves file"""
	
		saveFile = open('monthlyBudget.txt', 'w')
		for key in self.budget.keys():
			string = key + ","+str(self.budget[key])+'\n'
			saveFile.write(string)
		saveFile.close
		
	def updateDate(self):
		"""Saves the current month and year to indicate totals were updated"""
	
		lastUpdate = open("last_update.txt", "w")
		lastUpdate.write(str(self.curMonth) + " " + str(self.curYear))
		lastUpdate.close()
		
	def checkDate(self):
		"""Checks to see if a month has passed. If so updates budget"""
	
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
		else: #if more than 1 month has passed don't update since unlikely user has accurate log of expenses
			print("Please manually update since over a month has passed")
			return False
			
	def logExpense(self, addition=False):
		"""Makes entry field in GUI to record expenses/additions"""
		if self.curCategory != None:
			self.displayChoices()
			amount = tk.StringVar()
			e = tk.Entry(self.commandFrame, width = 5, textvariable = amount)
			e.focus_set()
			if addition:
				self.clearItem(2,0,self.commandFrame)
				e.grid(row=2,column=0)
			else:
				self.clearItem(1,0,self.commandFrame)
				e.grid(row=1,column=0)

			e.bind('<Return>', lambda command: self.logExpense_helper(e.get(), addition))

			
	def logExpense_helper(self, amount,addition):
		"""Updates sinking fund values"""
	
		try:
			amount = float(amount)
			if addition:
				amount*=-1
			self.currentValues[self.curCategory] -= round(amount,2)
			self.getLabel(addition, amount)
		except:
			None
	
	def getLabel(self, addition, amount):
		labelFrame = tk.Frame(self.commandFrame)
		
		if addition:
			self.clearItem(2,0,self.commandFrame)
			labelFrame.grid(row=2,column=0)
		else:
			self.clearItem(1,0,self.commandFrame)
			labelFrame.grid(row=1,column=0)

		labelName = tk.StringVar()
		label = tk.Label(labelFrame, text = "Optional Explanation:")
		label.grid(row=0,column=0, sticky='e')
		e = tk.Entry(labelFrame, width = 10, textvariable=labelName)
		e.focus_set()
		e.grid(row=0,column=1,sticky='w')
		e.bind('<Return>', lambda command: self.logLabel(e.get(), amount, addition, labelFrame))
		
	def logLabel(self, label, amount, addition, labelFrame):
		keepGoing = True
		while keepGoing:
			try:
				with open('budgetRecord.csv', 'a') as budgetRecord:
					writer = csv.writer(budgetRecord, delimiter='\t')
					if addition:
						amountStr = "+"+str(-1*amount)
					else:
						amountStr = "-"+str(amount)
					writer.writerow([str(self.curMonth)+'/'+str(self.curDate)+'/'+str(self.curYear),self.curCategory,amountStr,label])
				keepGoing = False
				labelFrame.destroy()
			except:
				self.makeRecord()
		self.displayBudget()
		self.displayChoices()
	
	def displayChoices(self):
		for child in self.commandFrame.winfo_children():
			child.destroy()
		for col in range(1):
			tk.Grid.columnconfigure(self.commandFrame,col,weight=1)
			for row in range(5):
				tk.Grid.rowconfigure(self.commandFrame,row,weight=1)
		label = tk.Label(self.commandFrame, text="Current Category: "+str(self.curCategory))
		label.grid(row=0, column=0)
		button1=tk.Button(self.commandFrame, text= "Log Expense", command= lambda: self.logExpense())
		button1.grid(row=1,column=0,sticky='nsew')
		button1.bind('<Return>', lambda command: self.logExpense())
		
		button2 = tk.Button(self.commandFrame, text="Log One-time Windfall", command= lambda: self.logExpense(True))
		button2.grid(row=2,column=0,sticky='nsew')
		button2.bind('<Return>', lambda command: self.logExpense(True))
		
		button3=tk.Button(self.commandFrame, text= "Update Monthly Allowance", command = lambda: self.changeBudget())
		button3.grid(row=3,column=0,sticky='nsew')
		button3.bind('<Return>', lambda command: self.changeBudget())

		button4 = tk.Button(self.commandFrame, text= "View History", command = lambda: self.viewHistory())
		button4.grid(row=4, column = 0,sticky='nsew')
		button4.bind('<Return>', lambda command: self.viewHistory())
		
		button5 = tk.Button(self.commandFrame, text= "Delete this category", command = lambda: self.deleteCategory())
		button5.grid(row=5, column = 0,sticky='nsew')
		button5.bind('<Return>', lambda command: self.deleteCategory())
	
	def viewHistory(self):
		if self.curCategory != None:
			historyWindow = tk.Tk()
			historyWindow.title(str(self.curCategory))
			with open('budgetRecord.csv', 'r') as budgetRecord:
				csvReader = csv.reader(budgetRecord, delimiter ='\t')
				colorBool = True #make alternating colors
				for i, row in enumerate(csvReader):
					if i == 0 or row[1] == self.curCategory:
						self.displayRow(row,i,historyWindow, colorBool)
						if colorBool:
							colorBool = False
						else:
							colorBool=True
					
	def displayRow(self, row, i, tkWindow, colorBool):
		color = "gray90"
		if colorBool:
			color = "gray80"
		for j in [0,2,3]:
			value = row[j]
			label = tk.Label(tkWindow, text=value, bg=color)
			label.grid(row=i,column=j, sticky='ew')
		
		
	def addCategory(self):
		addWindow = tk.Tk()
		addWindow.title("Add a Category")
		label = tk.Label(addWindow, text="Enter name of category:")
		label.grid(row=0,column=0, sticky='w')
		name = tk.StringVar()
		e1 = tk.Entry(addWindow, textvariable=name)
		e1.grid(row=1,column=0, sticky='w')
		e1.focus_set()
		label = tk.Label(addWindow, text="Enter monthly budget:")
		label.grid(row=3,column=0, sticky='w')
		amount = tk.StringVar()
		e2 = tk.Entry(addWindow, textvariable=amount)
		e2.grid(row=4,column=0, sticky='w')
		label = tk.Label(addWindow, text="\nHow would you like this month's budget allocated?")
		label.grid(row=5,column=0, sticky='w')
		
		
		additionNames = ["Proportional","Entirety","Deferred","Custom Amount:"]
		additionType = tk.Frame(addWindow)
		v = tk.IntVar(additionType, value = 0)
		additionType.grid(row=6,column=0,sticky='nsew')
		for i, name in enumerate(additionNames):
			radiobutton=tk.Radiobutton(additionType,text=name, anchor='w', variable=v, value = i, command = lambda v=v: self.displayDescription(v.get(),addWindow))
			radiobutton.grid(row=i,column=0,sticky='nsew')
# 			radiobutton.bind('<Return>', lambda command: radiobutton.focus_set())
		customAmount = tk.StringVar(additionType)
		e3 = tk.Entry(additionType, textvariable = customAmount, width=5)
		e3.grid(row=i, column = 1,sticky='nsew')
		label = tk.Label(addWindow, text="Description:")
		label.grid(row=7,column=0,sticky='w')
		self.displayDescription(v.get(),addWindow)
		
		e1.bind('<Return>', lambda command: e2.focus_set())
		button = tk.Button(addWindow, text = "Submit", command = lambda: self.addCategory_helper(e1.get(),e2.get(),addWindow, v.get(),e3.get()))
		button.bind('<Return>', lambda command: self.addCategory_helper(e1.get(),e2.get(),addWindow, v.get(),e3.get()))
		button.grid(row=9,column=0, sticky='w')
		e2.bind('<Return>', lambda command: button.focus_set())

	def displayDescription(self, num, window):
		descriptions=["You will be given the amount proportional to the\nnumber of remaining days in the month.",
					"You will be given the full month's budget.\n",
					"You will receive your first deposit next month.\n",
					"Enter the amount you wish to start with.\n"]
		self.clearItem(8, 0, window)
		label = tk.Label(window, text = descriptions[num])
		label.grid(row=8, column=0, sticky='w')
		
	def addCategory_helper(self, name, amount,window,additionType, customAmount):
		try:
			amount = float(amount)
			if name!="":
				self.budget[name]=round(amount,2)
				if additionType==0:
					self.currentValues[name]=round(amount*self.proportionalUpdate(),2)
				elif additionType==1:
					self.currentValues[name] = round(amount,2)
				elif additionType==2:
					self.currentValues[name] = 0
				else:
					try:
						self.currentValues[name] = round(float(customAmount),2)
					except ValueError:
						self.currentValues[name]=round(amount*self.proportionalUpdate(),2)
			window.destroy()
			self.setCurCategory(name)
			self.displayBudget()
			self.displayChoices()
		except:
			None
	
	def clearFrame(self):
		gridItems = self.tkBudget.grid_slaves()
		for item in gridItems:
			item.destroy()
			
	def changeBudget(self):
		if self.curCategory != None:
			self.displayChoices()
			amount = tk.StringVar()
			self.clearItem(3,0,self.commandFrame)
			e = tk.Entry(self.commandFrame, width = 5, textvariable = amount)
			e.focus_set()
			e.grid(row=3,column=0)
			e.bind('<Return>', lambda command: self.changeBudget_helper(e.get(), self.curCategory))

		
	def changeBudget_helper(self, amount, category):
		additionTypeWindow = tk.Tk()
		additionTypeWindow.title("How To Update")
		additionNames = ["Proportional","Entirety","Deferred","Custom Amount:"]
		additionType = tk.Frame(additionTypeWindow)
		additionType.grid(row=0,column=0,sticky='nsew')
		description = tk.Frame(additionTypeWindow)
		description.grid(row=1, column=0, sticky='nsew')
		label = tk.Label(description, text = "Description:")
		label.grid(row=0, column=0, sticky='nsew')
		
		v = tk.IntVar(additionType, value = 0)
		for i, name in enumerate(additionNames):
			radiobutton=tk.Radiobutton(additionType,text=name, anchor='w', variable=v, value = i, command = lambda v=v: self.displayDescription(v.get(),description))
			radiobutton.grid(row=i,column=0,sticky='nsew')
		self.displayDescription(v.get(),description)

		# try:
# 			amount = float(amount)
# 			difference = amount-self.budget[category]
# 			adjustment = difference*self.proportionalUpdate()
# 			self.logExpense_helper(adjustment, True)
# 			self.budget[category]=round(amount,2)
# 			self.displayBudget()
# 			self.displayChoices()
# 		except:
# 			None
					
	def deleteCategory(self):
		if self.curCategory!=None:
			self.displayChoices()
			confirmWindow = tk.Tk()
			confirmWindow.title("Confirmation")
			label = tk.Label(confirmWindow,text="Are you sure you want to delete "+self.curCategory+"?")
			label.grid(row=0,column=0)
			button = tk.Button(confirmWindow, text="Yes", command= lambda: self.deleteCategory_helper(self.curCategory,confirmWindow))
			button.grid(row=1, column=0)
			button.focus_set()
			button.bind('<Return>', lambda command: self.deleteCategory_helper(self.curCategory,confirmWindow))

		
	def deleteCategory_helper(self, category,window):
		del self.budget[category]
		del self.currentValues[category]
		window.destroy()
		self.curCategory = None
		self.displayGUI()

     	
	def displayBudget(self):
		for child in self.budgetFrame.winfo_children():
			child.destroy() 
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
		v = tk.StringVar()
		keys = list(self.currentValues.keys())
		for key in keys:
			button=tk.Radiobutton(self.budgetFrame, selectcolor="blue",indicatoron = 0, text=" " + key, variable = v, value = key, anchor="w", command = lambda v=v: self.setCurCategory(v.get()))
			button.grid(row=counter,column=0,sticky='nsew')
			label = tk.Label(self.budgetFrame, text = "$"+str(round(self.currentValues[key],2)), relief="groove")
			label.grid(row=counter, column=1,sticky='nsew')
			label = tk.Label(self.budgetFrame, text = "$"+str(round(self.budget[key],2)), relief="groove", anchor="e")
			label.grid(row=counter, column=2,sticky='nsew')
			counter+=1
		if self.curCategory == None and len(keys)>0:
			v.set(keys[0])
			self.setCurCategory(keys[0])
		else:
			v.set(self.curCategory)
		button = tk.Button(self.budgetFrame, text = "Add new category", command = self.addCategory)
		button.grid(row=counter, column=0)
		if self.curCategory==None:
			button.focus_set()

	
	def setCurCategory(self, category):
		self.curCategory = category
		self.clearItem(0,0,self.commandFrame)
		label = tk.Label(self.commandFrame, text="Current Category: "+str(self.curCategory))
		label.grid(row=0, column=0)
		self.displayChoices()


	def clearItem(self, row, col, grid):
		for item in grid.grid_slaves():
			if int(item.grid_info()["column"]) == col and int(item.grid_info()["row"])==row:
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
	FT.displayGUI()
# 	FT.displayBudget()
# 	FT.displayChoices()

	budget.mainloop()

	FT.saveValues()
	FT.saveBudget()
	FT.updateDate()
	

