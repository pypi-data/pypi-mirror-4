#! /bin/sh

echo '## Python 2'
for FILE in `/bin/ls Cartes/*.py`
do
    echo -n "Testing $FILE... "
    python $FILE
    echo "done."
done
python exemples/exemple3.py

echo '## Python 3'
for FILE in `/bin/ls Cartes/*.py`
do
    echo -n "Testing $FILE... "
    python3 $FILE
    echo "done."
done
python3 exemples/exemple3.py

# eof
