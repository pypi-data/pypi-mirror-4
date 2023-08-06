# _*_ coding: utf-8; _*_
"""
smblink role for Sphinx.

"""
from docutils import nodes
import re
import string

def convertToWSLStyle(text): #character escape function
    replaceDic = { 
        # Escape character : code list
        r'\^' :r'%5E', 
        r'\~' :r'%7E', 
        r'{'  :r'%7B', 
        r'}'  :r'%7D', 
        r'\[' :r'%5B', 
        r'\]' :r'%5D', 
        r';'  :r'%3B', 
        r'@'  :r'%40', 
        r'='  :r'%3D', 
        r'\&' :r'%26', 
        r'\$' :r'%24', 
        r'#'  :r'%23', 
        r' '  :r'%20', 
        '\\\\':r'/',   
    }

    text = re.sub(r'%', r'%25', text)     # escape "%" character at first
    for (reg, rep) in replaceDic.items(): # escape replaceDic characters
        text = re.sub(reg, rep, text)

    return text
    

"""
sphinx role function

"""
def smblink_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Role to create link addresses.
    """
    text = rawtext
    if '`' in text:
        text = text.split('`')[1]         # drop role name
    if '<' in text and '>' in text:
        name, path = text.split('<')      # split name, path by "<"
        path = path.split('>')[0]
        name = re.sub(r'[ ]+$','', name)  # remove spaces before "<"
    else:
        name = text
        path = name
    href = u"<a href=\"file:" + convertToWSLStyle(path) + u"\">" + name + u"</a>"
    node = nodes.raw('', href, format='html')
    return [node], []

def setup(app):
    app.add_role('smblink', smblink_role)

