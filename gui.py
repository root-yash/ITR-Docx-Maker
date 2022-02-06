from tkinter import filedialog
from data.Parse import parsepdf


def open_file():
    value = {}
    files = filedialog.askopenfilenames(title="select the file", filetypes=[("PDF", "*.pdf")])
    for file in files:
        value = parsepdf(file, file[:-4]+".docx")

