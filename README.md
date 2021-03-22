# Figshare HRData Processing

Repository containing scripts to process HRdata for Figshare

## Pipeline Structure

The pipeline is divided into two stages with one job each. Look at the [CI file](.gitlab-ci.yml) for reference.
- build (stage: `build`)
  This stage builds the container image used to run the script. It uses a Python image from DockerHub as the base file and installs the dependencies from `requirements.txt`. It only runs with `pushed` changes to `Dockerfile` and `requirements.txt`. Look at the [Dockerfile](Dockerfile) to see the build steps
- process_files (stage: `python_script`)
  This stage contains James' Python script.

## Artifacts

The `process_files` stage stores the input files and output files as artifacts. The artifacts are set to expire after 3 days, and the artifacts from the latest job is always stored. Artifacts for each job run can be accessed from the sidebar in the job log.
