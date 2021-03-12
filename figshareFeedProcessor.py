#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import iconv   # iconv -f iso-8859-1 -t UTF-8 figdata.xml -o figdata2.xml
import xmltodict
from sys import exc_info
import csv
from datetime import date


# Environmental variables
is_dev = 0 # Set to non-zero when running locally for testing
quota = "1073741824"  # default disk quota
manualdata = "manualdata.xml"
staffdata = "figdata.xml"
studentdata = "student_export.csv"
xmloutputfile = "hrfeed.xml"
departmentsfile = "uniquedepartments.txt"


def process_manual_data(manualfile):
    try:
        records = []
        with open(manualfile, "r",) as f:
            data = f.read().replace("\n", "")
        root = ET.fromstring(data)
        for child in root:
            record = {}
            for elem in child:
                record[elem.tag] = elem.text.strip()
            records.append(record)
        return records
    except():
        print("Error processing manual file:", exc_info()[0])


def process_staff_data(stafffile):
    try:
        records = []
        with open(stafffile, "r", encoding="iso-8859-1") as f:
            data = f.read().replace("\n", "")
        root = ET.fromstring(data)
        for child in root:
            record = {}
            for elem in child:
                elementname = elem.attrib["name"].replace("[", "").replace("]", "").strip()
                elementvalue = elem.text.strip()
                record[elementname] = elementvalue
            records.append(record)
        return records
    except():
        print("Error processing staff file:", exc_info()[0])


def process_student_data(studentfile):
    try:
        records = []
        with open(studentfile, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records
    except():
        print("Error processing student file:", exc_info()[0])


def dedup_records(manual, staff, student):
    # priority of records: manual, staff, student
    duplicatecount = 0
    dedups = []
    uniqueids = []
    duplicates = []
    for record in manual:
        if record["Proprietary_ID"] not in uniqueids:
            dedups.append(record)
            uniqueids.append(record["Proprietary_ID"])
        else:
            duplicates.append(record["Proprietary_ID"])
    for record in staff:
        if record["Proprietary_ID"] not in uniqueids:
            dedups.append(record)
            uniqueids.append(record["Proprietary_ID"])
        else:
            duplicates.append(record["Proprietary_ID"])
            duplicatecount += 1
    for record in student:
        if record["Proprietary_ID"] not in uniqueids:
            dedups.append(record)
            uniqueids.append(record["Proprietary_ID"])
        else:
            duplicates.append(record["Proprietary_ID"])
            duplicatecount += 1
    return dedups


def find_unique_departments(records):
    olddepartments = [line.strip() for line in open("uniquedepartments.txt")]  # departments in last processed records
    newdepartements = []  # departments in current records
    adddepartments = []  # departments new in current records
    removedepartments = []  # departments that were in the last processed records but not current records
    for record in records:
        d = record["Department"]
        if d not in newdepartements:
            newdepartements.append(d)
    for d in newdepartements:
        if d not in olddepartments:
            adddepartments.append(d)
    for d in olddepartments:
        if d not in newdepartements:
            removedepartments.append(d)
    adddepartments.sort()
    with open(departmentsfile, mode="wt", encoding="utf-8") as f:
        f.write("\n".join(newdepartements))


def create_xml_output(records):
    outxml = "<HRFeed>\n"
    for record in records:
        outxml += "<Record>\n"
        for key, value in record.items():
            if key == "IsCurrent":
                outxml += "<IsCurrent>Y</IsCurrent>\n"
            elif (key == "PrimaryGroupDescriptor") or (key == "Username"):
                pass # Figshare isn't using these elements
            else:
                outxml += "<%s>%s</%s>\n" % (key, value, key)
        if "Quota" not in record.keys():
            outxml += "<Quota>1073741824</Quota>\n"
        outxml += "</Record>\n"
    outxml += "</HRFeed>"
    f = open(xmloutputfile, "w")
    f.write(outxml)
    f.close()
    return outxml


def build_message(manualrecs, staffrecs, studentrecs, dedupilcatedrecs, ):
    message = "Figshare Feed Processor Report: %s \n\n" % (date.today().strftime("%Y-%m-%d"))
    message += "The following changes have been discovered in the HR Feed department field:/n"


def send_email(adddepts, removedepts):
    if len(adddepts) > 0:
        message += "Departments that were newly discovered in the HR Feed:/n"
        for d in adddepts:
            message+= "/t {} /n".format(d)
        message += "/n"
    if len(removedepts) > 0:
        message += "Departments that no longer exist in the HR Feed:/n"
        for d in removedepts:
            message += "/t {} /n".format(d)
        message += "/n"
    if not is_dev:
        with open("uniqdeptmsg.txt", "w") as uniqd:
            uniqd.write(message)


if __name__ == "__main__":
    manualrecords = process_manual_data(manualdata)
    staffrecords = process_staff_data(staffdata)
    studentrecords = process_student_data(studentdata)
    dedupilcatedrecords= dedup_records(manualrecords, staffrecords, studentrecords)
    find_unique_departments(dedupilcatedrecords)
    xmloutput = create_xml_output(dedupilcatedrecords)






