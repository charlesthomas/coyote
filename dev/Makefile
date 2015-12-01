pip = /usr/bin/pip
rabbit = /usr/sbin/rabbitmq-server

.PHONY: rabbitmq reqs

all: reqs $(rabbit)

rabbitmq: $(rabbit)

reqs: $(pip)
	pip install -r requirements.txt

$(pip):
	apt-get install -y python-pip

$(rabbit):
	apt-get install -y rabbitmq-server
	/usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management
	service rabbitmq-server restart
