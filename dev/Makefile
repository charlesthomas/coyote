pip = /usr/bin/pip
pythondev = /usr/include/python2.7/Python.h
ffi = /usr/include/x86_64-linux-gnu/ffi.h
rabbit = /usr/sbin/rabbitmq-server

all: reqs $(rabbit)

reqs: $(pip) $(pythondev) $(ffi)
	pip install -r /coyote/dev/requirements.txt

$(pip):
	apt-get install -y python-pip

$(ffi):
	apt-get install -y libffi-dev

$(pythondev):
	apt-get install -y python-dev

$(rabbit):
	apt-get install -y rabbitmq-server
	/usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management
	service rabbitmq-server restart
