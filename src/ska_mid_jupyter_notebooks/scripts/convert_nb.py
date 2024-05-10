import argparse
import csv
import sys
from pathlib import Path
from typing import cast

import nbformat
from nbformat.v4 import new_markdown_cell, new_notebook

parser = argparse.ArgumentParser(description="Converts a csv spreadsheet into a notebook")
parser.add_argument(
    "source",
    nargs="?",
    type=Path,
    default=sys.stdin,
    help="the source file (must be csv type)",
)
parser.add_argument(
    "dest",
    nargs="?",
    type=Path,
    default=sys.stdout,
    help="the destination file (must be .ipynb type",
)


def _main(dest: Path, source: Path):
    with dest.open("w") as destination_file:
        nb = new_notebook()
        with source.open("r") as source_file:
            for row in csv.DictReader(source_file):
                assert (
                    "Action" in row.keys()
                ), "Incorrect csv file: you need a column with heading Action"
                assert (
                    "Expected Result" in row.keys()
                ), "Incorrect csv file: you need a column with heading Expected Result"
                assert "#" in row.keys(), "Incorrect csv file: you need a column with heading #"
                data = f"**Step {row['#']}:**\n\n{row['Action']}  \n\nExpected Result:  \n_{row['Expected Result']}_"
                nb.cells.append(new_markdown_cell(data))
        nbformat.write(nb, destination_file)


def main():
    args = parser.parse_args()
    dest = cast(Path, args.dest)
    source = cast(Path, args.source)
    _main(dest, source)


if __name__ == "__main__":
    main()
