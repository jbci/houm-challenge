# OPTIONS >
# 
# -n :: app name, obligatory
# -t :: create templates folder {0,1}
# -s :: create static folder {0,1}
# -m :: create media folder {0,1}
# -u :: create urls.py file {0,1}
# -i :: define project name o main folder
#
# how to run?
#
# ./startapp.sh -n NAME -t 1 -s 0 -i mi_web
#

project_name=$(pwd|awk -F'/' '{print $NF}')
templates=1
static=1
media=0
urls=1
DEBUG=1

while getopts n:t:s:m:u:i:d: option
do
case "${option}"
in
  n) app=${OPTARG};;
  t) templates=${OPTARG};;
  s) static=${OPTARG};;
  m) media=${OPTARG};;
  u) urls=${OPTARG};;
  i) project_name=${OPTARG};;
  d) DEBUG=${OPTARG};
esac
done


echo "DEBUG FLAG : <${DEBUG}>"
echo "Creando apps en ${project_name}"
install_file="./${project_name}/settings/installed.py"

echo "Creating <"$app"> folder"

if [ $DEBUG -eq 0 ]
then
    mkdir -p ./apps/$app
fi

echo "Creating app inside the folder <./apps/"$app">"

if [ $DEBUG -eq 0 ]
then
    python manage.py startapp $app ./apps/$app
fi


echo "Template value <${templates}>"
if [ $templates -eq 1 ]
then
    echo "Creating templates"
    if [ $DEBUG -eq 0 ]
    then
        mkdir -p ./apps/$app/templates
        mkdir -p ./apps/$app/templates/$app
    fi
fi

echo "Static creation value <${static}>"
if [ $static -eq 1 ]
then
    echo "Creating static folder"
    if [ $DEBUG -eq 0 ]
    then
        mkdir -p ./apps/$app/static
        mkdir -p ./apps/$app/static/$app
    fi
fi

echo "Media creation value <${media}>"
if [ $media -eq 1 ];
then
    echo "Creating media folder"
    if [ $DEBUG -eq 0 ]
    then
        mkdir -p ./apps/$app/media
    fi
fi


echo "URLS creation value <${urls}>"
if [ $urls -eq 1 ];
then
    echo "Creating urls file"
    if [ $DEBUG -eq 0 ]
    then
        touch ./apps/$app/urls.py
    fi
fi

echo "Agregando app a INSTALLED_APPS -> apps.${app}"


if [ $DEBUG -eq 0 ]
then
    sed -i "/]/i\    \"apps."$app"\"," $install_file
fi

