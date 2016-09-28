# coding=utf-8
from splinter import Browser
import time
import os
import zipfile

zipFile = zipfile.ZipFile('./testzip.zip', 'w')
zipFile.write('./test.txt', './ok.txt', zipfile.ZIP_DEFLATED)
zipFile.close()

