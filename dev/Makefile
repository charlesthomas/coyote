pip = /usr/bin/pip
pythondev = /usr/include/python2.7/Python.h
rabbit = /usr/sbin/rabbitmq-server

all: reqs $(rabbit)

reqs: $(pip) $(pythondev)
	pip install -r /coyote/dev/requirements.txt

$(pip):
	apt-get install -y python-pip

$(pythondev):
	apt-get install -y python-dev

$(rabbit):
	apt-get install -y rabbitmq-server
