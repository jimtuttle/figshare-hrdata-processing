#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import os
from os.path import join

"""
    Make changes to incoming HR data from VT Enterprise Systems before feeding to Figshare.

    @author jjt
    @version Oct 1, 2020
"""


# Environment variables
is_dev = 0 # Set to non-zero when running locally for testing
quota = '1073741824'  # default disk quota
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
    uniquedepartments = []
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
            elif elementname == 'Department':
                if value not in uniquedepartments:
                    uniquedepartments.append(value)
            elif (elementname == 'PrimaryGroupDescriptor') or (elementname == 'Username'):
                # XML fields not needed by Figshare
                continue
            elif (elementname == 'IsCurrent'):
                # Change true/false to Y/N
                recordelement = ET.SubElement(record, elementname)
                recordelement.text = 'Y' if value == "true" else 'N'
                recordelement.tail = '\n'
            else:
                recordelement = ET.SubElement(record, elementname)
                recordelement.text = value
                recordelement.tail = '\n'
        quotaelement = ET.SubElement(record, 'Quota')
        quotaelement.text = quota
        quotaelement.tail = '\n'
    outxml = ET.ElementTree(outxml)
    if not is_dev:
        with open(outputfile, "wb") as elements:
            outxml.write(elements)
    return outxml, uniquedepartments


def departmentchanges(currentdepts):
    """
    Find departments that are new and departments that no longer exist in the feed.
    """
    existingdepts = [line.rstrip('\n') for line in open(join(os.getcwd(), 'uniquedepartments.txt'))]
    adddepts = []
    removedepts = []
    for d in currentdepts:
        if d not in existingdepts:
            adddepts.append(d)
        else:
            existingdepts.remove(d)
    removedepts = existingdepts
    if (removedepts.len > 0) or (adddepts.len > 0):
        alert = True
    else:
        alert = False

    return alert, adddepts, removedepts


def email_changes(adddepts, removedepts):
    """
    Email list when values in Department field has changed.
    """
    today = date.today()
    message = "The following changes have been discovered in the HR Feed departement field:/n"

    if adddepts.len > 0:
        message += "Departments that were newly discovered in the HR Feed:/n"
        for d in adddepts:
            message+= "/t {} /n".format(d)
        message += "/n"
    if removedepts > 0:
        message += "Departments that no longer exist in the HR Feed:/n"
        for d in removedepts:
            message += "/t {} /n".format(d)
        message += "/n"
    if not isdev:
        with open("uniqdeptmsg.txt", "wb") as elements:
            outxml.write(message)


if __name__ == "__main__":
    inputfile = 'hrdata.xml'
    output, currentdepartments = remediate_file(inputfile)
    alert, adddepts, removedepts = departmentchanges(currentdepartments)
    if alert:
            email_changes(adddepts, removedepts)
    output = lambda_handler('', '')
