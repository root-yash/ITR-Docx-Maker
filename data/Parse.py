import pdfplumber
import re
import configparser
import time
from docxtpl import DocxTemplate

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

    def configdict(self, itr, year):
        # input : take the year and itr no (itr:int , year:string)
        # output : configuration to how parse the data ex {ITR_3_1:{key:[...],index:....},....}
        config = configparser.RawConfigParser()
        config.read('Config/config'+year+".cfg")
        # example ITR_3
        section = "ITR_"+str(itr)
        temp = {}
        # store dict info to parse into list
        temp_dict = dict(config.items(section))
        for key in temp_dict.keys():
            temp[key] = temp_dict[key].split(",")
        # dict to its corresponding pages
        self.configuration = temp

        # table data
        # for i in self.tablep:
        #     if i == '':
        #         break
        #     temp = {}
        #     # store dict info to parse into list
        #     temp_dict = dict(config.items(section + "_" + i + 't'))
        #     for key in temp_dict.keys():
        #         temp[key] = temp_dict[key].split(",")
        #     # dict to its corresponding table
        #     self.configuration[i+'t'] = temp

    def tableparse(self, tables, key):

        # input : table : nested list containing string
        #         key : column of the table whose first element from row to choose
        # output : value at first row of that column

        key = re.compile(r".*{}.*".format(key.lower()))
        for table in tables:
            for j in range(len(table)):
                for k in range(len(table[j])):
                    if table[j][k] != None:
                        if key.match(table[j][k].lower()):
                            return table[j+1][k]

    def page_all(self, page, idx, table):

        #   input  : string page
        #   output : dict containing the detail according to config file

        yr = self.year
        itr = self.itr

        # get config from the dict

        start = self.configuration["start"]
        last = self.configuration["last"]
        key = self.configuration["key"]
        ftype = self.configuration["ftype"]
        d_type = self.configuration["dtype"]
        columns = self.configuration["columns"]
        columne = self.configuration["columne"]

        # split page into list

        page_split = page.split("\n")
        data = {}

        # initialize re function

        if d_type[idx] == "string":
            regex_compile = re.compile(r".*{}.*".format(start[idx].lower()))
        else:
            regex_compile = re.compile(r".*{}.*{}.*\d".format(start[idx].lower(), last[idx].lower()))

        # loop through all the line of the page
        for i in range(len(page_split)):
            if regex_compile.match(page_split[i].lower()):                                         # line match the re
                # in order to find the number
                if d_type[idx] == "no":
                    *_, l = page_split[i].split(' ')
                    # change 1,323 to 1323 integer
                    data[key[idx]] = int(''.join(l.split(',')))
                else:                                                                      # if it is a string
                    # itr3 2021-2022
                    if itr == 3 and yr == 2021:
                        *l, _ = page_split[i - 1].split(" ")
                        temp = ' '.join(l).split('(')
                        first_name = temp[0].strip()
                        last_name = temp[1].strip()[:-1]
                        if last_name.lower().startswith("prop"):
                            last_name = " ".join(last_name.split(" ")[2:])
                        # Name,company name
                        data.update({"Full Name": first_name, "cmpny_name": last_name})
                    # all the other itr
                    else:
                        flag = 1
                        tempi = 0
                        if ftype[idx] == "same":
                            tempi = i
                        elif ftype[idx] == "up":
                            tempi = i + 1
                        elif ftype[idx] == "down":
                            tempi = i - 1
                        else:
                            flag = 0
                            data[key[idx]] = self.tableparse(table, start[idx])

                        if flag == 1:
                            if columne[idx] == columns[idx]:
                                data[key[idx]] = (page_split[tempi].split(" "))[int(columne[idx])]
                            else:
                                s = 0
                                col = int(columne[idx])
                                if col == 0:
                                    col = None
                                temp = ' '.join((page_split[tempi].split(" "))[int(columns[idx]):col])
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
        return data, idx

    def parse_data(self):
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
                    if line.find("INDIAN INCOME TAX RETURN ACKNOWLEDGEMENT") != -1:
                        itr = 0
                    elif re.compile(r"ITR.?3").match(line):
                        itr = 3
                    elif re.compile(r"ITR.?4").match(line):
                        itr = 4
                    elif re.compile(r"ITR.?5").match(line):
                        itr = 5
                    elif re.compile(r"ITR.?6").match(line):
                        itr = 6
                    else:
                        itr = -1
                if type(year) == str and itr != -1:
                    break

            self.itr = itr
            self.year = int(year)
            # call function and produce config dict
            self.configdict(itr, year)
            dictdata, idx = self.page_all(page, idx, None)
            value.update(dictdata)

            ftype = self.configuration["ftype"]
            pageadd = self.configuration["pageadd"]
            i = 1
            # loop through page after 1st page
            while i < 30:
                table = None
                i = i+int(pageadd[idx])
                pageadd[idx] = 0
                page = pdf.pages[i].extract_text()                             # load pages in dictionary
                if ftype[idx] == 'table':
                    table = pdf.pages[i].extract_tables()
                dictdata, idx = self.page_all(page, idx, table)
                value.update(dictdata)
                if idx == -1:
                    break
                i = i+1
            print(len(value))
            print(value)
        return value, year, str(itr)

    def main(self):
        return self.parse_data()


def parsepdf(loc, save_loc):

    # Input : loc :string location of file/pdf
    #         save_loc:string location where to save the generated docx
    # function parse the itr and get important information
    # Output : itr save at save location
    s = time.time()
    cl = Itrparser(loc)
    value, year, itr = cl.main()
    docx = DocxTemplate('template/{}_{}.docx'.format(itr, year))
    docx.render(value)
    docx.save(save_loc)
    print(time.time()-s)
    return value, year
