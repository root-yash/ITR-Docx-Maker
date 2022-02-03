# This is a sample Python script.
from tkinter import *
from gui import open_file
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

main=Tk()
main.size
# Press the green button in the gutter to run the script.

if __name__ == '__main__':

    browse=Button(main, text="browse", command=open_file)
    l1 = Label(main, text="hello world")
    l2 = Label(main, text="hi india")
    l1.grid(row=6, column=0)
    l2.grid(row=5, column=1)
    browse.grid(row=1)
    main.mainloop()





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
