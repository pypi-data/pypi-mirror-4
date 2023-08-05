#!/usr/bin/python
# -*- coding: utf-8 -*-


def function(inputdic, inputgt, outputgt):
    linkstr = inputdic["list"].string
    #mkdir tmp dir
    #store as tmp
    import tempfile
    tmpfiledir = tempfile.mkdtemp()
    linklist = linkstr.strip(" []").split(",")
    linklist = [x.strip(' \'"') for x in linklist ]
    for link in linklist:
        #call wget to tmp dir
        import subprocess
        subprocess.call(["wget", "-P", tmpfiledir, link])
    import zipfile
    zout = zipfile.ZipFile(inputdic["outfile"].string, "w")
    import os
    for fname in os.listdir(tmpfiledir):
        zout.write(tmpfiledir + "/" + fname)
    return {"output":"True"}


iclass = "PythonTransformer"
inputdic = {"list":"cstring","outfile":"cstring"} #list:LinkList
outputdic = {"output":"TrueFalse"}

