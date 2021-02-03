# Figshare HRData Processing

Repository containing scripts to process HRdata for Figshare

## Testing locally

- Clone the Repository
- Download the input files into the repository directory
  - `aws s3 cp s3://vtlib-figshare-hrdata/figdata.xml ./hrdata.xml`
  - `aws s3 cp s3://vtlib-figshare-studentdata/student_export_20210125.csv ./studentdata.csv`
- Change the `is_dev` variable in `figshareFeedProcessor.py` to a non-zero value. (This isn't being properly used right now. Feel free to make changes)
- Run the Python script - `python3 figshareFeedProcessor.py`
- An `hrfeed.xml` file should be generated in addition to a `uniqdeptmsg.txt` if there are any changes in the departments
