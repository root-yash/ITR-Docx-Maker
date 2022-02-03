import pdfplumber
import re
import configparser
import time


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

        config = configparser.RawConfigParser()
        config.read('Config/config'+year+".cfg")
        section = "ITR_"+str(itr)
        # all the page no at which info is present
        self.pageno = dict(config.items(section))["pages"].split(",")
        self.tablep = dict(config.items(section))["tablep"].split(",")

        for i in self.pageno:
            temp = {}
            # store dict info to parse into list
            temp_dict = dict(config.items(section+"_"+i))
            for key in temp_dict.keys():
                temp[key] = temp_dict[key].split(",")
            # dict to its corresponding pages
            self.configuration[i] = temp

        for i in self.tablep:
            if i == '':
                break
            temp = {}
            # store dict info to parse into list
            temp_dict = dict(config.items(section + "_" + i +'t'))
            for key in temp_dict.keys():
                temp[key] = temp_dict[key].split(",")
            # dict to its corresponding pages
            self.configuration[i+'t'] = temp

    def load_data(self):
        itr = -1
        year = ["2021-22", "2020-21", "2019-20"]
        with pdfplumber.open(self.loc) as pdf:
            pages = pdf.pages[0].extract_text()

            for page in pages.split('\n'):
                if type(year) != str:
                    for i in year:
                        temp = page.replace(" ", "")
                        if temp.find(i) != -1:
                            year = i.split("-")[0]
                if itr == -1:
                    if page.find("INDIAN INCOME TAX RETURN ACKNOWLEDGEMENT") != -1:
                        itr = 0
                    elif page.find("ITR-3") != -1:
                        itr = 3
                    elif page.find("ITR-4") != -1:
                        itr = 4
                    elif page.find("ITR-5") != -1:
                        itr = 5
                    elif page.find("ITR-6") != -1:
                        itr = 6
                    else:
                        itr = -1
                if type(year) == str and itr != -1:
                    break

            self.configdict(itr, year)
            self.pages['0'] = pages
            for i in self.pageno[1:]:
                self.pages[i] = pdf.pages[int(i)].extract_text()                                        # load pages in dictionary

            self.itr = itr
            self.year = int(year)

    def page_all(self, page, no):

        #   input  : string page
        #   output : dict containing the detail according to config file
        yr = self.year
        itr = self.itr

        start = self.configuration[no]["start"]
        last = self.configuration[no]["last"]
        key = self.configuration[no]["key"]
        ftype = self.configuration[no]["ftype"]
        d_type = self.configuration[no]["dtype"]
        columns = self.configuration[no]["columns"]
        columne = self.configuration[no]["columne"]
        page_split = page.split("\n")
        data = {}
        idx = 0

        if d_type[idx] == "string":
            regex_compile = re.compile(r"^{}".format(start[idx]))
        else:
            regex_compile = re.compile(r".*{}.*{}.*\d".format(start[idx], last[idx]))
        for i in range(len(page_split)):
            if regex_compile.match(page_split[i]):
                if d_type[idx] == "no":
                    *_, l = page_split[i].split(' ')
                    # change 1,323 to 1323 integer
                    data[key[idx]] = int(''.join(l.split(',')))
                else:
                    # itr 2021-2022
                    if itr == 3 and yr == 2021:
                        *l, _ = page_split[i - 1].split(" ")
                        temp = ' '.join(l).split('(')  # temp variable to store split list
                        first_name = temp[0].strip()
                        last_name = temp[1].strip()[:-1]
                        if last_name.lower().startswith("prop"):
                            last_name = " ".join(last_name.split(" ")[2:])
                        # [Name,companyname]
                        data.update({"Full Name": first_name, "Company_name": last_name})
                    else:
                        if ftype[idx] == "up":
                            *l, _ = page_split[i - 1].split(" ")
                        else:
                            if columne[idx] == columns[idx]:
                                data[key[idx]] = (page_split[i].split(" "))[int(columne[idx])]
                            else:
                                data[key[idx]] = ' '.join((page_split[i].split(" "))[int(columns[idx]):int(columne[idx])])
                idx += 1
                if idx < len(start):                                                                           # no of element to search in the page
                    if d_type[idx] == "string":
                        regex_compile = re.compile(r"^{}".format(start[idx]))
                    else:
                        regex_compile = re.compile(r".*{}.*{}.*\d".format(start[idx], last[idx]))             # change the value to the variable of the line where it is present
                else:
                    break
        return data

    def tableparse(self):
        data_dict = {}
        with pdfplumber.open(self.loc) as pdf:
            for i in self.tablep:
                table_l = []
                table = pdf.pages[int(i)].extract_table()
                row = int(self.configuration[i+'t']["row"][0])
                column = int(self.configuration[i+'t']["column"][0])
                key = self.configuration[i+'t']["key"][0]
                table = table[row]
                for j in table:
                    if type(j) == str:
                        if len(j) > 0:
                            table_l.append(j)
                data_dict[key] = table_l[column]
        return data_dict

    def itr3(self):
        value = {}
        for i in self.pageno:
            value.update(self.page_all(self.pages[i], i))
        return value

    def main(self):

        self.load_data()
        func_dict = {0: " ", 3: self.itr3()}
        value = func_dict[self.itr]
        if len(self.tablep[0]) > 0:
            value.update(self.tableparse())
        print(value)
        print(len(value))

def parsepdf(loc):
    s = time.time()
    cl = Itrparser(loc)
    cl.main()
    print(time.time()-s)
