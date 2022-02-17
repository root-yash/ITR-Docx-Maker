from tkinter import filedialog
from tkinter import *
from data.Parse import resource_path, parsepdf, save_as
import configparser
from collections import OrderedDict
import tkinter.messagebox

def getlocation():
    files = filedialog.askopenfilename(title="select the file", filetypes=[("PDF", "*.pdf")])
    return files


def generate_docx(context, remark, files, tble, save_remark):
    print(context)
    context.update({"remarks":remark})
    flag = save_as(context, files)
    back(save_remark, tble)
    if flag == 1:
        tkinter.messagebox.showinfo('File Saved', "Document has been saved")
    else:
        tkinter.messagebox.showinfo('Error', 'Document not saved')

def savelocation(context, tble):
    tble.withdraw()
    files = filedialog.asksaveasfilename(defaultextension='.docx', title="Save location", filetypes=[("Word Document", "*.docx")])
    ### GUI ###
    save_remark = Tk()
    save_remark.title("ITR Docx")
    save_remark.iconbitmap(resource_path("logo/ITR Docx-logosb.ico"))
    location(save_remark, 160, 820)
    bottom = Frame(save_remark)
    bottom.grid(row=0, column=0, columnspan=4)
    Label(bottom, text="Remarks:", padx=5, pady=5, width=20).grid(row=0, column=0, pady=(10, 10))
    Button(bottom, text="OK", width =30, command=lambda: generate_docx(context,textremark.get("0.0", "end"),files, tble, save_remark)).grid(row=1, columnspan=2, pady=(10, 10))
    textremark = Text(bottom, height=4)
    textremark.grid(row=0, column=1, columnspan=3, pady=(10, 10))
    # default text
    textremark.insert("0.0", "NIL")
    save_remark.protocol('WM_DELETE_WINDOW', lambda: back(save_remark, tble))
    save_remark.mainloop()
    ### GUI End ###

def back(tble,main):
    main.deiconify()
    tble.quit()
    tble.destroy()

def quit(tble,main):
    tble.quit()
    tble.destroy()
    main.quit()
    main.destroy()

def remarks(tble, nandkvalue):
    # input : tble: window class of tkinter
    #         nandkvalue: from config file
    #         valuedict: dict calculate from the pdf

    for i in nandkvalue:
        v = int(valuedict[i])
        v2 = tble.getvar(name=i + 'b')
        if v2 == "":
            v2 = 0
        else:
            v2 = int(v2)
        value = v2-v
        valuedict[i+'b'] = v2
        valuedict[i + 'r'] = value
        tble.setvar(name=i + 'r', value=value)

def next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break"

def previous_widget(event):
    event.widget.tk_focusPrev().focus()
    return "break"

def location(main, h, w):
    # main: tkinter
    height = h
    width = w
    x = int(main.winfo_screenwidth()/2 - width/2)
    y = int(main.winfo_screenheight()/2 - height/2)
    main.geometry("{}x{}+{}+{}".format(width, height, x, y))

def makecontext(valuedict, context):

    # input valuedict generated from current pdf
    # context stored value of value dict as {itr_no: {"trueval":valdict, "context":[valuedict1, valuedict2]}
    # update context
    if len(context) == 0 or valuedict["itr"] not in context.keys():
        temp = valuedict.copy()
        valuedict.update({"sno":"1"})
        if "cmpny_name" in temp.keys():
            temp['cmpny_name'] = "Balance Sheet of " + temp["cmpny_name"] + "\n"
        context.update({"trueval": temp, valuedict["itr"]: {"contents": [valuedict]}})
    else:
        temp_list = context[valuedict["itr"]]["contents"]
        valuedict.update({"and": "and", "sno": len(temp_list)+1})
        temp_list.append(valuedict)
        context[valuedict["itr"]]["contents"] = temp_list
    return context

def add_document(tble, main):
    browse = getlocation()
    if len(browse) == 0:
        return
    tble.quit()
    tble.destroy()
    table(main, browse)

def table(main, browse):

    if len(browse) < 2:
        return

    # make main window disapper
    main.withdraw()
    global valuedict
    global context

    try:
        if type(context) != dict:
            context = {}
    except NameError:
            context = {}

    valuedict, yr, itr = parsepdf(loc=browse)
    makecontext(valuedict, context)
    # if wrong document opened
    if itr == -1:
        tkinter.messagebox.showinfo('Wrong Format', 'Wrong Pdf File is selected')
        main.deiconify()
        return

    tble = Tk()
    tble.title("ITR Docx")
    tble.iconbitmap(resource_path("logo/ITR Docx-logosb.ico"))

    try:
        if itr > 0 and itr < 7:
            if itr != 4:
                location(tble, 650, 897)

            config = configparser.RawConfigParser()
            config.read(resource_path('Config/config.cfg'))
            nandk = OrderedDict(config.items(section="ITR_" + str(itr)))
            namelist = list(nandk.keys())
            # if itr does not contain full name only company name
            if "full_name" in valuedict.keys():
                kk = "full_name"
            else:
                kk = "cmpny_name"
            title_name = ["Particulars", "BS From Income\nTax Website ", "From ITR", "Remark"]
            tble.resizable(False, False)
            head = Frame(tble, relief=SOLID)
            head.grid(columnspan=4, row=0, pady=(20, 20))
            Label(head, text="Full Name : "+valuedict[kk], font='Helvetica 10 bold', padx=10).grid(row=0, column=0)
            Label(head, text="Year : " + yr + "-" + str(int(yr)+1), font='Helvetica 10 bold', padx=10).grid(row=0, column=1)
            Label(head, text="ITR-" + str(itr), font='Helvetica 10 bold', padx=10).grid(row=0, column=2)
            title = Frame(tble, relief=SOLID)
            title.grid(columnspan=4, row=1)
            for i, t in enumerate(title_name):
                Label(title, text=t, padx=5, pady=5, width=20, font='Helvetica 12 bold').grid(row=1, column=i)

            # main_frame frame on which scroll and canvas is added

            tble_data = Frame(tble)
            if tble.winfo_screenwidth() < 2000 and itr != 4:
                main_frame = Frame(tble)
                main_frame.grid(row=2, columnspan=4)
                my_canvas = Canvas(main_frame, width=870, height=450)
                my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
                scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
                scrollbar.pack(side=RIGHT, fill=Y)
                my_canvas.configure(yscrollcommand=scrollbar.set)
                my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
                tble_data = Frame(my_canvas)
                my_canvas.create_window((0, 0), window=tble_data, anchor="nw")
            else:
                tble_data = Frame(tble)
                tble_data.grid(row=2, columnspan=4)

            name = Frame(tble_data)
            name.grid(row=2, column=0, padx=(5, 5))
            bank = Frame(tble_data)
            bank.grid(row=2, column=1, padx=(5, 5))
            form = Frame(tble_data)
            form.grid(row=2, column=2, padx=(5, 5))
            remark = Frame(tble_data)
            remark.grid(row=2, column=3, padx=(5, 5))
            bottom = Frame(tble)
            bottom.grid(row=3, columnspan=2, pady=(20, 10))

            # all the entry field and table
            for i in namelist:
                ent = StringVar(tble, value="", name=nandk[i]+'b')
                enr = IntVar(tble, value=0, name=nandk[i]+'r')
                Label(name, text=i[0].upper()+i[1:], padx=5, pady=5, width=30).pack()
                Entry(bank, width=30, textvariable=ent,borderwidth=1).pack(pady=5)
                Label(form, text=valuedict[nandk[i]], padx=5, pady=5, width=30, relief=SUNKEN).pack()
                Label(remark, textvariable=enr, padx=5, pady=5, width=30, relief=SUNKEN).pack()
            # down button
            bank.bind_class("Entry", "<Down>", next_widget)
            # up button
            bank.bind_class("Entry", "<Up>", previous_widget)

            Button(bottom, text="Get Back", padx=40, command=lambda: back(tble, main)).grid(row=1, column=0, padx=(20, 0))
            Button(bottom, text="Save As", padx=40, command=lambda: savelocation(context, tble)).grid(row=1, column=1)
            Button(bottom, text="Calculate Remark", padx=20, command=lambda: remarks(tble, list(nandk.values()))).grid(row=1, column=2)
            Button(bottom, text="Add More Documents", command=lambda: add_document(tble, main)).grid(row=1, column=3)


        else:
            if itr == 0:
                itr = "V"
            location(tble, 160, 900)
            tble.resizable(False, False)
            bottom = Frame(tble)
            bottom.grid(row=0, columnspan=4)
            Label(bottom, text="Name : "+valuedict["full_name"], width=50).grid(row=0, column=0, columnspan=2, padx=(0, 0), pady=(25, 25))
            Label(bottom, text="Pan : " + valuedict["pan"], width=30).grid(row=0, column=2, padx=(10, 0), pady=(25, 25))
            Label(bottom, text="ITR-" + str(itr), width=30).grid(row=0, column=3, padx=(10, 0), pady=(25, 25))
            Button(bottom, text="Save As", padx=40, pady=5, command=lambda: savelocation(context, tble)).grid(row=2, column=0, pady=(10, 10), padx=(100, 25))
            Button(bottom, text="Get Back", padx=40, pady=5, command=lambda: back(tble, main)).grid(row=2, column=1, pady=(10, 10), padx=(10, 25))
            Button(bottom, text="Add More Documents", padx=40, pady=5, command=lambda : add_document(tble, main)).grid(row=2, column=2, pady=(10, 10), padx=(10, 25))

    except KeyError:
        tkinter.messagebox.showinfo('Pdf Format', 'Weird Pdf File Format')
        back(tble, main)

    tble.protocol('WM_DELETE_WINDOW', lambda: quit(tble, main))
    tble.mainloop()





