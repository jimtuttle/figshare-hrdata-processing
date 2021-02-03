# Figshare HRData Processing

Repository containing scripts to process HRdata for Figshare

## Pipeline Structure

The pipeline is divided into three stages with one job each. Look at the [CI file](.gitlab-ci.yml) for reference.
- fetch_input_files (stage: `fetch`)
  This fetches the latest file from the `HRDATA_BUCKET` and `STUDENTDATA_BUCKET` and saves them as `hrdata.xml` and `studentdata.csv` which are stored as artifacts so that they are available in the next stage.
- process_files (stage: `process`)
  This stage is meant to run the transformation/change on the input files. It runs a single script (`figshareFeedProcessor.py`) and outputs `hrfeed.xml`, and optionally `uniqdeptmsg.txt` depending on whether any new department was added or removed. Both of these files are set as artifacts so that they can be retrieved by the next stage to send the emails.
- send_things (stage: `send`)
  This stage is used to send the transformed file to Figshare and optionally send an email to `vtul-figshare-hrfeed-g@vt.edu` as evidenced by the _existence_ of `uniqdeptmsg.txt`.

## Testing locally

- Clone the Repository
- Download the input files into the repository directory
  - `aws s3 cp s3://vtlib-figshare-hrdata/figdata.xml ./hrdata.xml`
  - `aws s3 cp s3://vtlib-figshare-studentdata/student_export_20210125.csv ./studentdata.csv`
- Change the `is_dev` variable in `figshareFeedProcessor.py` to a non-zero value. (This isn't being properly used right now. Feel free to make changes)
- Run the Python script - `python3 figshareFeedProcessor.py`
- An `hrfeed.xml` file should be generated in addition to a `uniqdeptmsg.txt` if there are any changes in the departments

Note that in order to facilitate the testing of a particular failed job run, the input and the output files for a particular run can be downloaded from the "Job Artifacts" section of a job log. Jobs logs can be found from the left sidebar -> CI / CD -> Pipelines. `fetch_input_files` will contain the input files as artifacts and `process_files` should contain the output files.
