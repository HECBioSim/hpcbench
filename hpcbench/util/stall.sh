jobid=$1
jobstatus="test"
while [ "$jobstatus" != "" ]
do
  sleep 10
  sentence="$(squeue -j $jobid)"
  exit_status=$?
  if [ $exit_status -eq 1 ]
  then
    exit
    break
  fi
  stringarray=($sentence)
  jobstatus=(${stringarray[12]})
done