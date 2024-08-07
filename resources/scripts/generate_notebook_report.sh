#!/bin/bash
jupyter nbconvert --to rst  ../../notebooks/mid_e2e/e2e_tmc_itf.ipynb ../../notebooks/mid_e2e/e2e_tmc_itf.txt
python3 print_table.py | tee ready_to_pdf.txt
#Last step is to convert the generated ready_to_pdf.txt file to pdf