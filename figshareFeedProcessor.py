#!/usr/bin/env python3
#import boto3
import xml.etree.ElementTree as ET


"""
    Make changes to incoming HR data from VT Enterprise Systems before feeding to Figshare.

    @author jjt
    @version Oct 1, 2020
"""


# Environment variables
quota = '1073741824'  # default disk quota
bucket = 'vtlib-figshare-hrdata'
inputfile = 'hrdata.xml'
outputfile = 'hrfeed.xml'


def push_to_figshare():
    """Submit reformatted HR XML to Figshare HR API."""
    pass


def lambda_handler(event, context):
    # s3_client = boto3.client('s3')
    # s3.download_file(bucket, 'OBJECT_NAME', filename)
    pass


def remediate_file(infile):
    """Takes input XML file.  Returns reformatted XML.
    For records with no email, creates email address from username.
    """
    outxml = ET.Element('HRFeed')
    outxml.tail = '\n'
    outxml.text = '\n'
    tree = ET.parse(infile)
    root = tree.getroot()
    for child in root:
        record = ET.SubElement(outxml, 'Record')
        record.tail = '\n'
        record.text = '\n'
        for elem in child:
            elementname = elem.attrib['name'].replace('[', "").replace("]", "")
            value = elem.text.strip()
            if elementname == 'Email' and value == '':
                for subchild in child:
                    if subchild.attrib['name'] == '[Username]':
                        username = subchild.text.strip()
                        email = username+'@vt.edu'
                recordelement = ET.SubElement(record, elementname)
                recordelement.text = email
                recordelement.tail = '\n'
            elif (elementname == 'PrimaryGroupDescriptor') or (elementname == 'Username'):
                # XML fields not needed by Figshare
                continue
            else:
                recordelement = ET.SubElement(record, elementname)
                recordelement.text = value
                recordelement.tail = '\n'
        quotaelement = ET.SubElement(record, 'Quota')
        quotaelement.text = quota
        quotaelement.tail = '\n'
    outxml = ET.ElementTree(outxml)
#    with open(outputfile, "wb") as elements:
#        outxml.write(elements)
    return outxml


if __name__ == "__main__":
    inputfile = 'hrdata.xml'
    output = remediate_file(inputfile)
