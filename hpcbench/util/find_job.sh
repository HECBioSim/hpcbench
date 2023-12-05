if [ -z ${1+x} ]; then echo 'Usage: find_job.sh jobid'; exit 1; fi
find . -mindepth 0 -name "*$1*" -type f
