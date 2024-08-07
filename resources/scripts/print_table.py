# -*- coding: utf-8 -*-

from prettytable import PrettyTable
import textwrap

from fpdf import FPDF
from PyPDF2 import PdfFileMerger

table = PrettyTable()

def add_divider():
    i=0
    line = ""
    while(i < 94):
        line += "="
        i += 1
    return line
def main():
    f = open("notebooks/mid_e2e/e2e_tmc_itf.rst", "r")
    parsing_code = False
    lines = f.readlines()
    i = 1
    table.field_names = ["Notebook in table form"]
    col1 = ""
    col2 = ""
    current_line1 = ""
    current_line2 = ""
    while(i < len(lines)):
        if("code::" in str(lines[i])):
            parsing_code = True
        elif("~~" in str(lines[i]) or "parsed-literal::" in str(lines[i]) or not parsing_code):
            current_line2 = str(lines[i])
            current_line = " ".join(textwrap.wrap(lines[i-1], 30, break_long_words=True))
            parsing_code = False
            if("parsed-literal::" in str(lines[i])):
                table.add_row([""], divider=True)
            if("~~" in str(lines[i])):
                #Avoid duplicates
                if(current_line1 != current_line2 and current_line1 != ""):
                    table.add_row([col2], divider=True)
                    current_line1 = ""
                    current_line2 = ""
                table.add_row([add_divider()])

            col2 = " ".join(textwrap.wrap(lines[i-1], 30, break_long_words=True))
            if("~~" not in col2 and "parsed-literal::" not in col2):
                table.add_row([col2])
            current_line2 = str(lines[i])
        else:
            if(not parsing_code):
                col1 = " ".join(textwrap.wrap(lines[i], 30, break_long_words=True))
                if("~~" not in col1 and "parsed-literal::" not in col1):
                    table.add_row([col1])
                    
        col1_str = col2_str = ""
        i+=1
    print(table)

if __name__ == '__main__':
    main()