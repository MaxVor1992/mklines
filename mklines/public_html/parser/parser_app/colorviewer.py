import tkinter
import parser_utils

root = tkinter.Tk()
for name,color in parser_utils.colors.items():
    tkinter.Label(root,text=name, bg=color).pack(fill="x")

root.mainloop()
