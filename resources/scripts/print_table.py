# -*- coding: utf-8 -*-

from prettytable import PrettyTable
import textwrap

table = PrettyTable()

# Class
class PrintTable:
    def __init__(self, values, captions, widths, aligns):
        if not all([len(values[0]) == len(x) for x in [captions, widths, aligns]]):
            raise Exception()
        self._tablewidth = sum(widths) + 3*(len(captions)-1) + 4
        self._values = values
        self._captions = captions
        self._widths = widths
        self._aligns = aligns

    def print(self):
        self._printTable()

    def _printTable(self):
        formattext_head = ""
        formattext_cell = ""
        for i,v in enumerate(self._widths):
            formattext_head += "{" + str(i) + ":<" + str(v) + "} | "
            formattext_cell += "{" + str(i) + ":" + self._aligns[i] + str(v) + "} | "
        formattext_head = formattext_head[:-3]
        formattext_head = "  " + formattext_head.strip() + "  "
        formattext_cell = formattext_cell[:-3]
        formattext_cell = "  " + formattext_cell.strip() + "  "

        print("-"*self._tablewidth)
        print(formattext_head.format(*self._captions))
        print("-"*self._tablewidth)
        for w in self._values:
            print(formattext_cell.format(*w))
        print("-"*self._tablewidth)

def print_table (cols, rows, border_horizontal = '-', border_vertical = '|', border_cross = '+'):
    #cols = [list(x) for x in zip(*tbl)]
    lengths = [max(map(len, map(str, col))) for col in cols]
    f = border_vertical + border_vertical.join(' {:>%d} ' % l for l in lengths) + border_vertical
    s = border_cross + border_cross.join(border_horizontal * (l+2) for l in lengths) + border_cross

    print(s)
    for row in rows:
        #print(f.format(*row))
        print(s)

def main():
    #PrintTable(yourdata, [column_captions], column_widths, text_aligns).print()
    f = open("notebooks/mid_e2e/e2e_tmc_itf.rst", "r")
    parsing_code = False
    lines = f.readlines()
    i = 1
    table.field_names = ["Action===============================================", "Results==============================================================="]
    col1 = ""
    col2 = ""
    while(i < len(lines)):
        if("code::" in str(lines[i])):
            parsing_code = True
            print("==Col2==")
            col1 = textwrap.wrap(lines[i], 30, break_long_words=True)
        elif("~~~" in str(lines[i]) or "parsed-literal::" in str(lines[i]) or not parsing_code):
            print("==Col1==")
            parsing_code = False
            print("Keep this*:" + lines[i-1])
            col2 = textwrap.wrap(lines[i-1], 30, break_long_words=True)
            table.add_row([col2 , col1])
        col1_str = col2_str = ""
        i+=1
    print(table)

if __name__ == '__main__':
    main()