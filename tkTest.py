# import tkinter as tk
# 
# master = tk.Tk()
# 
# root = tk.Tk()
# frame = tk.Frame(root)
# frame.pack()
# 
# button = tk.Button(frame, 
#                    text="QUIT", 
#                    fg="red",
#                    command=quit)
# button.pack(side=tk.LEFT)
# 
# whatever_you_do = "Whatever you do will be insignificant, but it is very important that you do it.\n(Mahatma Gandhi)"
# msg = tk.Message(master, text = whatever_you_do)
# msg.config(bg='lightgreen', font=('times', 24, 'italic'))
# msg.pack()
# 
# tk.mainloop()

from tkinter import *

def printSomething():
    # if you want the button to disappear:
    # button.destroy() or button.pack_forget()
    label = Label(root, text= "Hey whatsup bro, i am doing something very interresting.")
    #this creates a new label to the GUI
    label.pack() 

root = Tk()

button = Button(root, text="Print Me", command=printSomething) 
button.pack()

root.mainloop()
