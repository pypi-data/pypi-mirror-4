'''This file makes Microsoft Word (Office 2007) docx files from input data'''

from docx import *

def default_props():
    import getpass
    title = 'File created by Python-docx'
    subject = 'Python generated word document'
    creator = getpass.getuser() 
    keywords = ['',]
    return {'title':title,'subject':subject,'creator':creator,'keywords':keywords}

def create_docx(input,filename,props={}):
    """Input is a list of document contents in the format of
    props is the properties to save the document(s) which if unsupplied will use some default sludge."""
    
    prop = default_props()
    prop.update(props)
    
    # setup document
    rels = relationshiplist()
    wordrels = wordrelationships(rels)
    document = newdocument()
    body = document.xpath('/w:document/w:body', namespaces=nsprefixes)[0]
    #put content in
    if isinstance(input,basestring):
        body.append(paragraph(input)) 
    else: #list of paragraphs:
        for para in input:
            body.append(paragraph(para,style='Normal'))
    coreprops = coreproperties(title=prop['title'],subject=prop['subject'],creator=prop['creator'],keywords=prop['keywords'])
    appprops = appproperties()
    content_types = contenttypes()
    web_settings =  websettings()   
        
    # Save our document
    savedocx(document,coreprops,appprops,content_types,web_settings,wordrels,filename) 
        
if __name__ == '__main__':
    create_docx("testing's",'test.docx')