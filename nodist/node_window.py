#!/usr/bin/env python

# Built-in modules
import tkinter
import tkinter.scrolledtext


class NodeWindow():
    def __init__(self):
        self.root =tkinter.Tk()
        self.st = tkinter.scrolledtext.ScrolledText(self.root, state='disabled')
        self.st.configure(font='TkFixedFont')
        self.st.pack()

    def add(self, msg):
        def append():
            self.st.configure(state='normal')
            self.st.insert(tkinter.END, msg)
            self.st.insert(tkinter.END, '\n')
            self.st.configure(state='disabled')
            # Autoscroll to the bottom
            self.st.yview(tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.st.after(0, append)
        self.root.update_idletasks()
        self.root.update()
        
if __name__ == '__main__':

    text_handler = NodeWindow()

    text_handler.add('Beispiel:')
    text_handler.add('message')
    text_handler.add('message')
    text_handler.add('message')
    text_handler.add('message')




    