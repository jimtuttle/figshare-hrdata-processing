#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from sys import exc_info
import csv
from datetime import date
from requests import post
from os import environ
import boto3


# Environmental variables
manualdata = "manualdata.xml"
staffdata = "figdata.xml"
studentdata = "student_export.csv"
xmloutputfile = "hrfeed.xml"
departmentsfile = "uniquedepartments.txt"
# Figshare variables
figshareurl = environ['FIGSHARE_API_URL']
figsharetoken = environ['FIGSHARE_TOKEN']
# Mailgun variables
mailgunkey = environ['MAILGUN_KEY']
mailgunurl = environ['MAILGUN_URL']
emailrecipient = environ['RECIPIENT_EMAIL']
emailsender = environ["SENDER_EMAIL"]
# AWS variables
awsid = environ["AWS_ACCESS_KEY_ID"]
awskey = environ["AWS_SECRET_ACCESS_KEY"]


def get_aws_files(keyid, accesskey, manualfile, stafffile, studentfile):
    s3 = boto3.client("s3", aws_access_key_id=keyid, aws_secret_access_key=accesskey)
    s3.download_file("vtlib-figshare-hrdata", manualfile, manualfile)
    s3.download_file("vtlib-figshare-hrdata", stafffile, stafffile)
    s3.download_file("vtlib-figshare-studentdata", studentfile, studentfile)


def process_manual_data(manualfile):
    try:
        records = []
        with open(manualfile, "r", ) as f:
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
    return olddepartments, newdepartements, adddepartments, removedepartments


def create_xml_output(records):
    outxml = "<HRFeed>\n"
    for record in records:
        outxml += "<Record>\n"
        for key, value in record.items():
            if key == "IsCurrent":
                outxml += "<IsCurrent>Y</IsCurrent>\n"
            else:
                if key == "Department":
                    if "& " in value:
                        value = value.replace("&", "&amp;")
                if (key == "PrimaryGroupDescriptor") or (key == "Username"):
                    pass  # Figshare isn't using these elements
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


def build_message(manualrecs, staffrecs, studentrecs, dedupilcatedrecs, olddepartments, newdepartements, adddepartments,
                  removedepartments):
    message = "Figshare Feed Processor Report: %s \n\n" % (date.today().strftime("%Y-%m-%d"))
    message += "Found %s manual records, %s staff records, and %s student records for total of %s records. %s records " \
               "were used after deduplication.\n" % (len(manualrecs), len(staffrecs), len(studentrecs),
                                                     str(len(manualrecs) + len(staffrecs) + len(studentrecs)),
                                                     len(dedupilcatedrecs))
    message += "This feed contained %s unique departments.  There were %s unique departments in the most recent feed.\n\n" \
               % (len(newdepartements), len(olddepartments))
    if len(adddepartments) > 0:
        message += "The following departments have been removed:\n"
        for d in adddepartments:
            message += "%s \n" % d
    else:
        message += "No departments were removed.\n"
    if len(adddepartments) > 0:
        message += "The following departments have been added:\n"
        for d in removedepartments:
            message += "%s \n" % d
    else:
        message += "No departments were added.\n"
    return message


def put_aws_files(keyid, accesskey, xmlfile, deptsfile):
    s3 = boto3.client("s3", aws_access_key_id=keyid, aws_secret_access_key=accesskey)
    s3.upload_file(xmlfile, "vtlib-figshare-hrdata", xmlfile)
    s3.upload_file(deptsfile, "vtlib-figshare-hrdata", deptsfile)


def update_figshare_api(url, token, outputfile):
    headers = {"Authorization": "token " + token}
    with open(outputfile, "rb") as fin:
        files = {"hrfeed": (outputfile, fin)}
        response = post(url, headers=headers, files=files)
        print(response.content)
        print(response.request.body)
        response.raise_for_status()


def send_message(key, url, sender, recipient, body):
    request_url = url.format()
    subject = "Figshare Feed Processor Report: %s" % (date.today().strftime("%Y-%m-%d"))
    response = post(request_url, auth=('api', key), data={
        "from": sender,
        "to": recipient,
        "subject": subject,
        "text": body
    })
    # print('Status: {0}'.format(response.status_code))
    # print('Body:   {0}'.format(response.text))


if __name__ == "__main__":
    get_aws_files(awsid, awskey, manualdata, staffdata, studentdata)
    manualrecords = process_manual_data(manualdata)
    staffrecords = process_staff_data(staffdata)
    studentrecords = process_student_data(studentdata)
    dedupilcatedrecords = dedup_records(manualrecords, staffrecords, studentrecords)
    olddepts, newdepts, adddepts, removedepts = find_unique_departments(dedupilcatedrecords)
    xmloutput = create_xml_output(dedupilcatedrecords)
    messagebody = build_message(manualrecords, staffrecords, studentrecords, dedupilcatedrecords, olddepts, newdepts,
                                adddepts, removedepts)
    put_aws_files(awsid, awskey, xmloutputfile, departmentsfile)
    update_figshare_api(figshareurl, figsharetoken, xmloutputfile)
    send_message(mailgunkey, mailgunurl, emailsender, emailrecipient, messagebody)
