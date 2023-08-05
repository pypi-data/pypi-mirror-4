PREFIX=$(cd "$(dirname "$0")"; pwd)

python $PREFIX/misc/boot/css_js.py 

sudo supervisorctl stop ${PWD##*/}_$USER:*

PROGRAM=$PREFIX/misc/boot/dev.py

ps x -u $USER|ack $PROGRAM|awk  '{print $1}'|xargs kill -9
ps x -u $USER|ack 'jitter'|awk  '{print $1}'|xargs kill -9 

jitter $PREFIX/coffee $PREFIX/js &
python $PROGRAM 

