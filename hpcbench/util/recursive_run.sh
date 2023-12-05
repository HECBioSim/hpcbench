if [ -z ${1+x} ]; then echo 'Usage: recursive_run.sh command "filename"'; exit 1; fi
currdir=$(pwd)
PATH="$(echo "$PATH" | sed -E 's/(^|:)[^\/][^:]*//g')" # find is weird ok
echo "This will run your command ($1) on the following files:"
find $currdir -mindepth 0 -name "$2" -type f
read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    find $currdir -mindepth 0 -name "$2" -type f -execdir $1 {} \;
fi
