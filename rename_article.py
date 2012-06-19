#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
File: rename_pdf.py
Author: Steve Genoud
Date: 2012-06-14
Description: Automatically renames papers
'''

import re
import sys
import os.path
import tempfile
from xml.dom import minidom
import shutil
import urllib


def is_handler(fcn):
    """
    Decorator to register handlers
    
    The handlers are processes that take the text of the pdf and returns a
    title. The are processed in the order they are registered.
    """
    
    HANDLERS.append(fcn)
    return fcn
HANDLERS = []

def clean_title(title):
    """Transforms a title in a file name"""
    
    title = re.sub('\W', ' ', title)
    title = re.sub(' +',' ', title)
    title = title.title()
    return title.strip().replace(' ', '_')

def get_file_name(file_path):
    """Helper function that extract the name of the file"""
    
    dir_, file_ = os.path.split(file_path)
    file_name, ext = os.path.splitext(file_)
    return file_name

def new_file_path(text, file_path):
    file_name = get_file_name(file_path)
    for handler in HANDLERS:
        new_file_name = handler(text)
        if new_file_name:
            return file_path.replace(file_name, new_file_name)
    else:
        return file_path

def _print_changes(old_path, new_path):
    """Helper function that prints the changes to the standard output"""
    
    od, op = os.path.split(old_path)
    nd, np = os.path.split(new_path)
    if op == np:
        print '%s could not be renamed' % op
    else:
        print '%s has been renamed %s' % (op, np)


def rename_article(file_path, info=False):
    """
    Automatically renames the paper at file_path
    
    This is the main function of this module, the info argument sets if info is 
    printed at the console
    """
    
    text = page_extractor_pdftotext(file_path)
    new_path = new_file_path(text, file_path)
    shutil.move(file_path, new_path)

    if info:
        _print_changes(file_path, new_path)


############################################

def page_extractor_pyPdf(file_name):
    """Extracts the text of a pdf with pyPdf"""
    
    import pyPdf
    file_reader = pyPdf.PdfFileReader(open(file_name, 'r'))
    first_page = file_reader.getPage(0)
    return first_page.extractText()

def page_extractor_pdftotext(file_name):
    """Extracts the text of a pdf with pdftotext (from xpdf)"""
    
    import subprocess
    tmpfile = tempfile.NamedTemporaryFile()
    subprocess.call('pdftotext -l 3 "%s" "%s"' % (file_name, tmpfile.name), shell=True)
    text = tmpfile.read()
    return text


#############################################
#############################################

# Definition of Handlers

def extract_doi(text):
    # This code comes from this stackoverflow question: 
    # http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
    print text
    DOI_ID = re.compile(r'\b(10\.\d{4,}(?:\.[0-9]+)*/(?:(?![\"\&\'\<\>])\S)+)\b')

    search = DOI_ID.search(text)
    if search is None:
        return None

    return search.group(0)

def title_from_doi(doi):

    url = 'http://doi.crossref.org/servlet/query?pid=sgenoud@ethz.ch&format=xml&id=%s' % doi
    metadata = minidom.parse(urllib.urlopen(url))
    titles = metadata.getElementsByTagName('title')
    if not len(titles):

        #Sometimes the doi belong to a subelement of the article
        parent = metadata.getElementsByTagName('sa_component')
        if parent:
            return title_from_doi(parent[0].getAttribute('parent_doi'))
        return False
    
    title = titles[0].firstChild.data
    return clean_title(title)

@is_handler
def doi_handler(text):
    doi = extract_doi(text)
    if doi is None:
        return False
    new_file_name = title_from_doi(doi)
    return new_file_name

#############################################

def extract_arxiv(text):
    ARXIV_ID = re.compile(r'arxiv\s*:\s*(?P<id>(\d{4}\.\d{4})|(.{2,10}\/\d{7}))', re.I)
    search = ARXIV_ID.search(text)
    if search is None:
        return None

    return search.group('id')

def title_arxiv(arxiv_id):
    url = 'http://export.arxiv.org/api/query?id_list=%s' % arxiv_id
    metadata = minidom.parse(urllib.urlopen(url))

    titles = metadata.getElementsByTagName('entry')
    if not len(titles):
        return False
    
    title = (titles[0]
             .getElementsByTagName('title')[0]
             .firstChild.data)
    return clean_title(title)

@is_handler
def arxiv_handler(text):
    arxiv_id = extract_arxiv(text)
    if arxiv_id is None:
        return False
    new_file_name = title_arxiv(arxiv_id)
    return new_file_name

#############################################

def extract_pnas(text):
    ss = '\s*/*\s*'
    PNAS_DOI = re.compile(ss.join((r'www.pnas.org', r'cgi', r'doi', 
                                   r'10.1073', r'(?P<doi>.*)\b')))
    search = PNAS_DOI.search(text)
    if search is None:
        return None

    for doi in search.groups():
        is_doi = extract_doi('a 10.1073/' + doi + ' a')
        if is_doi is not None:
            return is_doi

@is_handler
def pnas_handler(text):
    doi = extract_pnas(text)
    if doi is None:
        return False
    new_file_name = title_from_doi(doi)
    return new_file_name


if __name__ == '__main__':
    rename_article(sys.argv[1])

