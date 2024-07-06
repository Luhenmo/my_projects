import tkinter as tk

def on_click():
    print("Button clicked")

app = tk.Tk()
app.title("Simple Tkinter App")

label = tk.Label(app, text="Hello, Tkinter!")
label.pack()

button = tk.Button(app, text="Click Me", command=on_click)
button.pack()

app.mainloop()
