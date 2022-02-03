from tkinter import filedialog
from data.Parse import parsepdf

def open_file():
    file = filedialog.askopenfilenames(title="select the file", filetypes=[("PDF","*.pdf")])
    parsepdf(file[0])