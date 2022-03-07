from tkinter import Tk, StringVar, Button, SOLID
from gui import table, getlocation, back, location, getlocations, gsttable
from data.Parse import resource_path

def buttonbr(fun,dir_b):
    # To get the location of the file and save it
    buttonb = fun()
    dir_b.set(buttonb)

def opening_gst(landing):
    landing.withdraw()
    main = Tk()
    dir_b = StringVar(main, value="location of the Gst 1 pdfs", name='browse')
    dir_b2 = StringVar(main, value="location of the Gst 3B pdfs", name='browse2')
    main.title('ITR Docx')
    main.iconbitmap(resource_path("logo/ITR Docx-logosb.ico"))
    location(main, 160, 600)
    label_b = Button(main, textvariable=dir_b, width=70, relief=SOLID)
    label_b2 = Button(main, textvariable=dir_b2, width=70, relief=SOLID)
    browse1 = Button(main, text="Select Pdf", command=lambda: buttonbr(getlocations, dir_b))
    browse2 = Button(main, text="Select Pdf", command=lambda: buttonbr(getlocations, dir_b2))
    enter = Button(main, text="Click To Process Pdf", width=80,
                   command=lambda: gsttable(main, landing, main.getvar(name="browse"), main.getvar(name="browse2")))
    label_b.grid(row=1, column=0, padx=(20, 5), pady=(25, 0))
    label_b2.grid(row=2, column=0, padx=(20, 5), pady=(25, 0))
    browse1.grid(row=1, column=1, padx=(0, 20), pady=(25, 0))
    browse2.grid(row=2, column=1, padx=(0, 20), pady=(25, 0))
    enter.grid(row=3, columnspan=2, padx=(20, 20), pady=(20, 20))
    main.protocol('WM_DELETE_WINDOW', lambda: back(main, landing))
    main.mainloop()
    landing.deiconify()

def opening_itr(landing):

    # when itr button is clicked it would run the itr
    # take landing page

    landing.withdraw()
    main = Tk()
    dir_b = StringVar(main, value="location of the pdf", name='browse')
    main.title('ITR Docx')
    main.iconbitmap(resource_path("logo/ITR Docx-logosb.ico"))
    location(main, 145, 600)
    label_b = Button(main, textvariable=dir_b, width=70, relief=SOLID)
    browse = Button(main, text="Select Pdf", command=lambda: buttonbr(getlocation, dir_b))
    enter = Button(main, text="Click To Process Pdf", width=80, command=lambda: table(main, landing, main.getvar(name="browse")))
    label_b.grid(row=1, column=0, padx=(20, 5), pady=(25, 0))
    browse.grid(row=1, column=1, padx=(0, 20), pady=(25, 0))
    enter.grid(row=3, columnspan=2, padx=(20, 20), pady=(20, 20))
    main.protocol('WM_DELETE_WINDOW', lambda: back(main, landing))
    main.mainloop()

if __name__ == '__main__':
    landing = Tk()
    landing.title('ITR Docx')
    landing.iconbitmap(resource_path("logo/ITR Docx-logosb.ico"))
    location(landing, 80, 500)
    button_gst = Button(landing, text="GST Doc", width=32, pady=10, relief=SOLID, command=lambda: opening_gst(landing))
    button_itr = Button(landing, text="ITR Doc", width=32, pady=10, relief=SOLID, command=lambda: opening_itr(landing))
    button_gst.grid(row=0, column=0, padx=(10, 5), pady=(20, 20))
    button_itr.grid(row=0, column=1, padx=(5, 10), pady=(20, 20))
    landing.mainloop()

# TODO Revised and orginal
# TODO 2019 in achnowledgenment
# TODO

