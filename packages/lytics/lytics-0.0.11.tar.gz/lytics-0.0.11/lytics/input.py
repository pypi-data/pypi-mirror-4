# -*- coding: utf-8 -*-
import sys
import os
import logging

log = logging.getLogger("lytics")

class ReadLineIterator(object):
    """
    An iterator that calls readline() to get its next value.
    """
    def __init__(self, f): 
        self.f = f

    def __iter__(self): 
        return self

    def next(self):
        line = self.f.readline()
        if line: 
            return line
        else: 
            raise StopIteration


class InputHelper(object):
    "Stdin iterator for parsing contents"
    def __init__(self,*args,**kwargs):
        self.qs = ""

    def parse(self,cb=None):
        """
        Parse input into seperate entities defined by new lines
        """
        firstLine = True 
        ql = []
        txt = ""
        comment = ""
        inComment = False
        done = False
        def handle_row():
            if len(txt) > 3:
                ql.append((comment, txt ))
                if cb is not None:
                    cb((comment,txt))
        while not done:
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                break

            if not line:
                break

            # first line allows for querystring type params
            if firstLine:
                firstLine = False
                if "args?" in line:
                    qs = line[line.index("?")+1:]
                    if len(qs) > 0:
                        self.qs = "&" + qs
                    continue 

            #line = line.strip()
            #print("comment='%s' txt='%s'" % (comment,txt))
            if len(line) > 1 and line[0:2] == "/*":
                inComment = True
                comment += line
            elif len(line) > 1 and line[0:2] == "*/":
                inComment = False
                comment += line
            elif len(line) > 0 and line[0] == "#":
                comment += line
            elif len(line) > 1 and line[0:2] == "--":
                inComment = False
                comment += line
            elif inComment:
                comment += line
            elif len(line) > 1:
                parts = line.split("#")
                if len(parts) > 1:
                    txt += parts[0]
                else:
                    txt += line
            else:
                # empty line is a seperator, mark as new query
                handle_row()
                txt = ""
                comment = ""
            #print(comment)

        handle_row()

        return ql





