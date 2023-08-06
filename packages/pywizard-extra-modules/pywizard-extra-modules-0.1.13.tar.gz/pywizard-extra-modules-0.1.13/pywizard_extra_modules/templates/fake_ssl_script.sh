openssl genrsa -out {{ path }}/{{ keyname }} 1024
echo "openssl req -config $TEMPFILE -new -key {{ path }}/{{ keyname }} -out {{ path }}/{{ csrname }}"
openssl req -config {{ path }}/ssl.conf -new -key {{ path }}/{{ keyname }} -out {{ path }}/{{ csrname }}
openssl x509 -req -days 1024 -in {{ path }}/{{ csrname }} -signkey {{ path }}/{{ keyname }} -out {{ path }}/{{ crtname}}
