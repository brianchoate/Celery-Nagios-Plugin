#! /usr/bin/python

"""
check_celery.py
~~~~~~~~~

This is a monitoring plugin for Nagios NRPE. If required,
ensure a copy of this is placed in the following directory on the host machine:
    /usr/local/nagios/libexec/
"""
import sys
import requests
from optparse import OptionParser


def getOptions():
    arguments = OptionParser()
    arguments.add_option("--host", dest="host",
                         help="Host rabbitmq is running on",
                         type="string", default="localhost")
    arguments.add_option("--port", dest="port",
                         help="RabbitMQ API port",
                         type="string", default="55672")

    return arguments.parse_args()[0]


if __name__ == '__main__':

    options = getOptions()
    api_path = "api/workers"

    response = requests.get("%s:%d/%s"
                            % (options.host,
                               int(options.port),
                               api_path))

    try:
        response.raise_for_status()
    except Exception as e:
        print "Status Critical, celerymon API not reachable"
        sys.exit(2)

    try:
        content = response.json()
    except Exception as e:
        check_api.unknown_error("%s health check response was malformed: %s"
                                % (check_api.options.action, e))

    if len(content) == 0:
        print "Status Ok, nothing in celery queue at the moment"
        sys.exit(0)

    errormessage = 'Failed workers: '
    successmessage = 'Succesful workers: '

    for workername in content:
        worker = content[workername]
        status = worker["status"]

        if status is not True:
            failed = True
            errormessage = '{} {},'.format(errormessage, workername)
        else:
            successmessage = '{} {},'.format(successmessage, workername)

    if failed:
        print errormessage
        sys.exit(2)

    print "Celery health check successful"
    sys.exit(0)
