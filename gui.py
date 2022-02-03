from tkinter import filedialog
from data.Parse import parsepdf

def open_file():
    files = filedialog.askopenfilenames(title="select the file", filetypes=[("PDF","*.pdf")])
    for file in files:
        parsepdf(file)