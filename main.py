from tkinter import Tk, StringVar, Button, SOLID
from gui import table, getlocation
from data.Parse import resource_path

def location(main):
    # main: tkinter
    height = 145
    width = 600
    x = int(main.winfo_screenwidth()/2 - width/2)
    y = int(main.winfo_screenheight()/2 - height/2)
    main.geometry("{}x{}+{}+{}".format(width, height, x, y))

def buttonbr(fun,dir_b):
    buttonb = fun()
    dir_b.set(buttonb)

if __name__ == '__main__':

    main = Tk()
    dir_b = StringVar(main, value="location of the pdf", name='browse')
    main.title('ITR Docx')
    main.iconbitmap(resource_path("logo/ITR Docx-logosb.ico"))
    location(main)
    label_b = Button(main, textvariable=dir_b, width=70, relief=SOLID)
    browse = Button(main, text="Select Pdf", command=lambda: buttonbr(getlocation, dir_b))
    enter = Button(main, text="Click To Process Pdf", width=80, command=lambda: table(main, main.getvar(name="browse")))
    label_b.grid(row=1, column=0, padx=(20, 5), pady=(25, 0))
    browse.grid(row=1, column=1, padx=(0, 20), pady=(25, 0))
    enter.grid(row=3, columnspan=2, padx=(20, 20), pady=(20, 20))
    main.mainloop()

# TODO Revised and orginal
# TODO 2019 in achnoledgenment
# TODO

