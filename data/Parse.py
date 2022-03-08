import pdfplumber
import re
import configparser
from docxtpl import DocxTemplate
import os
import sys

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Itrparser:

    def __init__(self, loc):
        self.pages = {}
        self.table = {}
        self.pageno = []
        self.tablep = []
        self.loc = loc
        self.configuration = {}
        self.year = int()
        self.itr = int()
        self.gst = int()

    def configdict(self, itr, year):
        # input : take the year and itr no (itr:int , year:string)
        # output : configuration to how parse the data ex {ITR_3_1:{key:[...],index:....},....}
        config = configparser.RawConfigParser()
        configloc = 'Config/config'+year+".cfg"
        config.read(resource_path(configloc))
        # example ITR_3
        section = "ITR_"+str(itr)
        sections = [section, section+"sum", section+"sub"]
        key_parent = ["main", "sum", "sub"]
        # store dict info to parse into list
        dictvalue = {}
        for idx in range(len(sections)):
            temp = {}
            temp_dict = dict(config.items(sections[idx]))
            for key in temp_dict.keys():
                temp[key] = temp_dict[key].split(",")
            dictvalue[key_parent[idx]] = temp
            # dict to its corresponding pages
        self.configuration = dictvalue


    def tableparse(self, tables, key, tidx):

        # input : table : nested list containing string
        #         key : column of the table whose first element from row to choose
        # output : value at first row of that column

        temp = 0
        key = re.compile(r".*{}.*".format(key.lower()))
        tablerow_add = int(self.configuration["main"]["tablerow_add"][tidx])
        tablecolumn = int(self.configuration["main"]["tablecolumn"][tidx])
        for table in tables:
            for j in range(len(table)):
                for k in range(len(table[j])):
                    if table[j][k] != None:
                        if key.match(table[j][k].lower()):
                            if tablecolumn == 0:
                                return table[j+tablerow_add][k].replace("\n","")
                            else:
                                for i in table[j]:
                                    if i != None:
                                        temp += 1
                                        if temp == tablecolumn:
                                            return i.replace("\n", "")



    def page_all(self, page, idx, table, page_idx):

        #   input  : string page
        #   output : dict containing the detail according to config file

        yr = self.year
        itr = self.itr

        # get config from the dict

        start = self.configuration["main"]["start"]
        last = self.configuration["main"]["last"]
        key = self.configuration["main"]["key"]
        ftype = self.configuration["main"]["ftype"]
        d_type = self.configuration["main"]["dtype"]
        columns = self.configuration["main"]["columns"]
        columne = self.configuration["main"]["columne"]

        # split page into list

        page_split = page.split("\n")
        data = {}

        # initialize re function

        if d_type[idx] == "string":
            regex_compile = re.compile(r".*{}.*".format(start[idx].lower()))
        else:
            regex_compile = re.compile(r".*{}.*{}.*\d".format(start[idx].lower(), last[idx].lower()))

        # loop through all the line of the page
        i = 0
        tidx = 0

        while i < len(page_split):
            if regex_compile.match(page_split[i].lower()):                                         # line match the re
                if ftype[idx] == 'table':
                    with pdfplumber.open(self.loc) as pdf:
                        table = pdf.pages[page_idx].extract_tables()
                # in order to find the number
                if d_type[idx] == "no":
                    *_, l = page_split[i].split(' ')
                    # change 1,323 to 1323 integer
                    try:
                        temp_no = int(''.join(l.split(',')))
                    except:
                        temp_no = ''.join(l.split(','))
                    data[key[idx]] = temp_no
                else:                                                                      # if it is a string
                    # itr3 2021-2022
                    if itr == 3 and yr == 2021:
                        *l, _ = page_split[i - 1].split(" ")
                        temp = ' '.join(l).split('(')
                        first_name = temp[0].strip()
                        try:
                            last_name = temp[1].strip()[:-1]
                            if last_name.lower().startswith("prop"):
                                last_name = " ".join(last_name.split(" ")[2:])
                            # Name,company name
                            data.update({"full_name": first_name, "cmpny_name": last_name})
                        except:
                            data.update({"full_name": first_name})

                    # all the other itr
                    else:
                        flag = 1
                        tempi = 0
                        if ftype[idx] == "same":
                            tempi = i
                        elif ftype[idx] == "up":
                            tempi = i + 1
                            i = 0
                            # weird 2019 syntax
                            if key[idx] == 'pan' and itr == 0:
                                tempi = tempi + 1
                        elif ftype[idx] == "down":
                            tempi = i - 1
                        elif ftype[idx] == "table":
                            flag = 0
                            data[key[idx]] = self.tableparse(table, start[idx], tidx)
                            tidx += 1

                        if itr == 4 and yr == 2021 and ftype[idx] == "itr4":      # weired formating need to used this for cmpny name
                            tempi = i + 2


                        if flag == 1:
                            temp = list(filter(('').__ne__, page_split[tempi].split(" ")))
                            if columne[idx] == columns[idx]:
                                data[key[idx]] = temp[int(columne[idx])]
                            else:
                                s = 0
                                col = int(columne[idx])
                                if col == 0:
                                    col = None
                                temp = ' '.join(temp[int(columns[idx]):col])
                                for s in range(len(temp)):
                                    if temp[s].isnumeric():
                                        s -= 1
                                        break
                                data[key[idx]] = temp[:s+1]
                idx += 1
                # no of import elements
                if idx < len(start):
                    if d_type[idx] == "string":
                        regex_compile = re.compile(r".*{}.*".format(start[idx].lower()))
                    else:
                        regex_compile = re.compile(r".*{}.*{}.*\d".format(start[idx].lower(), last[idx].lower()))
                else:
                    return data, -1
            i += 1
        return data, idx

    def sumorsub(self, key, value, dictvalue, flag):
        # Input:
        # key: section from the config file
        # value: list of all the parameter whose arithmetic operation needs to be done from dictvalue
        # dictvalue: value retrieve from the pdf
        # flag: 1 sum or 0 for sub
        # output : {key:function performed}
        temp = 0
        if type(dictvalue[value[0]]) == str:
            temp = ''
            if flag == 1:
                for i in value:
                    temp += dictvalue[i]+" "
        else:
            if flag == 1:
                for i in value:
                    temp += dictvalue[i]
            else:
                temp = dictvalue[value[0]]
                for i in value[1:]:
                    temp -= dictvalue[i]

        return {key: temp}

    def getfloat(self, data):
        s = ""
        for i in data:
            if i.isnumeric() or i == "." or i == "-":
                s = s+i
        if len(s) == 0 or s == "-":
            return float(0.0)
        return round(float(s), 2)

    def gst_table(self, page, gst):
        value = {}
        temp = []
        i = 0
        if gst == 1:
            while len(page) > i:
                if len(page[i]) > 1:
                    temp.append(page[i])
                    i += 1
                else:
                    temp.append(page[i]+page[i+1])
                    i += 2
            page = temp
            self.year = page[0][0][1]
            value["period"] = page[0][1][1]
            value["year"] = self.year
            value["gstin"] = page[1][0][1].strip()
            value["cmpny_name"] = page[1][2][1].replace("\n", "")
            value["tottaxa"] = self.getfloat(page[2][1][2])+self.getfloat(page[3][1][2])+self.getfloat(page[4][1][2])+\
                               self.getfloat(page[5][1][2])+self.getfloat(page[6][1][2])+self.getfloat(page[7][1][2])+\
                               self.getfloat(page[8][1][1])+self.getfloat(page[8][1][2])+self.getfloat(page[8][1][3])
        else:
            self.year = page[0][0][1]
            value["period"] = page[0][1][1]
            value["year"] = self.year
            value["gstin"] = page[1][0][1].strip()
            value["cmpny_name"] = page[1][2][1].replace("\n", "")
            value["tottaxb"] = self.getfloat(page[2][1][1]) + self.getfloat(page[2][2][1]) + \
                               self.getfloat(page[2][3][1]) + self.getfloat(page[2][5][1])
            value["inttax"] = self.getfloat(page[2][1][2]) + self.getfloat(page[2][2][2])
            value["centax"] = self.getfloat(page[2][1][3]) + self.getfloat(page[2][2][3])
            value["statax"] = self.getfloat(page[2][1][4]) + self.getfloat(page[2][2][4])
        return value


    def parse_data(self, itr_flag=0):
        # return itr:integer
        #        year: string
        if itr_flag == 0:
            value = {}
            idx = 0
            itr = -1
            year = ["2021-22", "2020-21", "2019-20"]
            with pdfplumber.open(self.loc) as pdf:
                page = pdf.pages[0].extract_text()

                for line in page.split('\n'):

                    # check for the year in the docx
                    if type(year) != str:
                        for i in year:
                            temp = line.replace(" ", "")
                            if temp.find(i) != -1:
                                year = i.split("-")[0]

                    # check for the itr no in the docx
                    if itr == -1:
                        if line.find("RETURN ACKNOWLEDGEMENT") != -1 or line.find("VERIFICATION FORM") != -1:
                            itr = 0
                        elif re.compile(r"ITR.?3").match(line):
                            itr = 3
                        elif re.compile(r"ITR.?4").match(line):
                            itr = 4
                        elif re.compile(r"ITR.?5").match(line):
                            itr = 5
                        elif re.compile(r"ITR.?6").match(line):
                            itr = 6
                        elif re.compile(r"ITR.?7").match(line):
                            itr = 7
                        else:
                            itr = -1
                    if type(year) == str and itr != -1:
                        break
                # if wrong form or document
                if itr == -1:
                    return value, year, itr
                self.itr = itr
                self.year = int(year)
                # call function and produce config dict
                self.configdict(itr, year)
                dictdata, idx = self.page_all(page, idx, None, 0)
                value.update(dictdata)
                pageadd = self.configuration["main"]["pageadd"]
                i = 1
                # loop through page after 1st page
                while i < 30 and itr != 0:
                    table = None
                    i = i+int(pageadd[idx])
                    pageadd[idx] = 0
                    page = pdf.pages[i].extract_text()                             # load pages in dictionary
                    dictdata, idx = self.page_all(page, idx, table, i)
                    value.update(dictdata)
                    if idx == -1:
                        break
                    i = i+1
            sumdict = self.configuration["sum"]
            subdict = self.configuration["sub"]

            if len(subdict) > 0:
                key = list(subdict.keys())
                variable = list(subdict.values())
                for i, j in zip(key, variable):
                    value.update(self.sumorsub(i, j, value, flag=0))

            if len(sumdict) > 0:
                key = list(sumdict.keys())
                variable = list(sumdict.values())
                for i, j in zip(key, variable):
                    value.update(self.sumorsub(i, j, value, flag=1))

            value.update({"yr1": year[-2:], "yr2": str(int(year[-2:])+1), "itr": itr})
            return value, year, itr
        else:
            # for gst parsing
            value = {}
            idx = 0
            with pdfplumber.open(self.loc) as pdf:
                page = pdf.pages[0].extract_tables()
                if itr_flag == 1:
                    page += pdf.pages[1].extract_tables()
                value.update(self.gst_table(page, itr_flag))
            return value

    def main(self, flag=0):
        return self.parse_data(flag)


def parsepdf(loc):

    # Input : loc :string location of file/pdf
    #         save_loc:string location where to save the generated docx
    # function parse the itr and get important information
    # Output : itr save at save location
    cl = Itrparser(loc)
    value, year, itr = cl.main()
    return value, year, itr

def parsepdfgst(loc, flag = 1):
    # Input : loc :string location of file/pdf
    #         save_loc:string location where to save the generated docx
    # function parse the itr and get important information
    # Output : gst save at save location
    cl = Itrparser(loc)
    value = cl.main(flag)
    return value


def save_as(value_dict,save_loc):
    try:
        page = []
        header = DocxTemplate(resource_path("template/header.docx"))
        for itr in range(0, 9):
            if itr in value_dict.keys():
                temploc = 'template/{}.docx'.format(itr)
                temp_docx = DocxTemplate(resource_path(temploc))
                if itr == 0 or itr == 7:
                    value_dict[itr].update(value_dict["trueval"])
                temp_docx.render(value_dict[itr])
                temp_docx.save(save_loc)
                sub_doc = header.new_subdoc(save_loc)
                page.append(sub_doc)
        footer = header.new_subdoc(resource_path("template/footer.docx"))
        context = {"pages": page, "remarks": value_dict["remarks"], "footer": footer}
        context.update(value_dict["trueval"])
        header.render(context)
        header.save(save_loc)
        return 1                                               # if file saved
    except:
        return 0
def save_aspdf(value_list, save_loc, remark):
    try:
        header = DocxTemplate(resource_path("template/gst.docx"))
        footer = header.new_subdoc(resource_path("template/footer.docx"))
        temp = value_list[0]
        context = {"contents": value_list, "footer": footer, "cmpny_name": temp["cmpny_name"], "years": temp["years"],
                   "gstin": temp["gstin"], "remarks": remark}
        header.render(context)
        header.save(save_loc)
        return 1
    except:
        return 0


