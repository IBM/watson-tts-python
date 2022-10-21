import os
from pathlib import Path
from IPython.display import Audio
from os.path import exists
import html


class HTMLTable:

    def __init__(self, fileName):
        self.ffout = open(fileName, "wt", encoding='utf-8-sig')

    def create(self):
        self.ffout.write("<!DOCTYPE html>\n")
        self.ffout.write(" <html>\n")
        self.ffout.write("  <head>\n")
        self.ffout.write("   <title>wavs2html</title>\n")
        self.ffout.write("   <style>\n")
        self.ffout.write("    table, th, td {\n")
        self.ffout.write("      border: 0px solid black;\n")
        self.ffout.write("      border-collapse: collapse;\n")
        self.ffout.write("    }\n")
        self.ffout.write("    th, td {\n")
        self.ffout.write("            padding: 5px;\n")
        self.ffout.write("    }\n")
        self.ffout.write("   </style>\n")
        self.ffout.write("  </head>\n")
        self.ffout.write("  <body>\n")
        self.ffout.write("<table>\n")

    def close(self):
        self.ffout.write("</table>")
        self.ffout.close()

    def print(self, s):
        self.ffout.write("</br>\n" + s + "</br>\n")

    def add_header(self, sHeader, sDelimiter):
        header = sHeader.split(sDelimiter)
        self.ffout.write("  <tr>\n")
        for column in header:
            self.ffout.write(" <td style=\"font-size:1.5em;\"  bgcolor=\"#D6EAF8\" ><u>{0}</u></td>\n".format(column.strip()))
        self.ffout.write("  </tr>\n")

    def add_cell(self, col, show_file_name=False):
        if col.endswith((".wav", ".mp4", ".flac", ".mp3")) and (exists(col)):
            p = Path(col.strip())
            audio = Audio(data=p.read_bytes(), embed=True)
            if show_file_name:
                cell = '{}<br>'.format(os.path.basename(p))
            else:
                cell = ''
            cell += audio._repr_html_()
            self.ffout.write("     <td>{}</td>\n".format(cell))
        else:
            self.ffout.write("<td>{0}</td>\n".format(html.escape(col.strip())))


    def add_row(self, sLine, sDelimiter):
        row = sLine.split(sDelimiter)
        self.ffout.write("  <tr>\n")
        for column in row:
            self.add_cell(column)

        self.ffout.write("  </tr>\n")

    def addTitle(self, title, sDelimiter):
        self.add_row(f'<span style="color:blue;"> <b>{title}</b> </span>', sDelimiter)


if __name__ == "__main__":
    htmlTable = HTMLTable("test.html");
    htmlTable.create()
    htmlTable.add_header("header zz1111;; header 2222;;  header 3333;;  header 4444", ";;")
    htmlTable.add_row("cell 00, cell 01, " + "/Users/alexanderfaisman/dev/tinytools/test_runner/test.wav", ",")

    htmlTable.close()
