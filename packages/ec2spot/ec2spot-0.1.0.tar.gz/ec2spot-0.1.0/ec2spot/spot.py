import boto.ec2
import logging as logger
import time
"""
Dinesh Weerapurage
11/20/2012

This class requiers you to create ~/.boto file with AWS credentials

For example: ~/.boto may look like,

[Credentials]
aws_access_key_id =
aws_secret_access_key =

[Boto]
debug = 0
num_retries = 10
"""


class SpotInstanceRequest(object):

    def __init__(self):
        regions = boto.ec2.regions()
        self.region = None
        """
        selecting us-east as my default region
        """
        for r in regions:
            if str(r) == 'RegionInfo:us-east-1':
                self.region = r
        if self.region is None:
            raise Exception("Invalid region")
        self.conn = self.region.connect()

        self.script = """#!/bin/bash
set -e -x
apt-get update
apt-get install -y emacs
"""

    """
    Some useful image-id:
    Amazon Fedora = ami-84db39ed
    Amazon Ubuntu = ami-3b4ff252
    """
    def spot_request(self, price='0.003', image_id='ami-91d066f8', key_name='DjangoTutorial', instance_type='t1.micro'):
        self.spot = self.conn.request_spot_instances(price,
                                                     image_id=image_id,
                                                     availability_zone_group=self.region,
                                                     key_name=key_name,
                                                     instance_type=instance_type,
                                                     user_data=self.script)

    """
    Check every 5 seconds whether current request is active. If all requests are in "cancelled" state exit
    """
    def status(self, req_id=None):
        while True:
            fcancel = False
            fopen = False
            spots = self.conn.get_all_spot_instance_requests()
            for i in spots:
                logger.debug(i.state)
                if str(i.state) == "cancelled":
                    continue
                fcancel = True
                print "#",
                logger.debug("!")
                if str(i.state) == "open":
                    fopen = True

            # only cancelled requests available, exit loop
            if fcancel is False:
                break

            # no open requests, exit loop
            if fopen is False:
                break

            time.sleep(20)

    def cancel(self, req_id=None):
        spots = self.conn.get_all_spot_instance_requests()
        for i in spots:
            self.conn.cancel_spot_instance_requests([i.id])

    """
    Get ec2 instances and public_dns_name of running instances
    """
    def reservations(self):
        reservations = self.conn.get_all_instances()
        for i in reservations:
            reservation = i
            instance = reservation.instances[0]
            print instance.state
            if str(instance.state) == "running":
                print instance.public_dns_name

    """
    Terminate all instances
    """
    def stop_instance(self):
        reservations = self.conn.get_all_instances()
        for i in reservations:
            reservation = i
            logger.debug("stop instance %s" % str(i))
            instance = reservation.instances[0]
            instance.terminate()

    """
    Get request status and instance status
    """
    def get_status(self):
        self.status()
        self.reservations()

    """
    Cancel both request and instance
    """
    def stop(self):
        self.stop_instance()
        time.sleep(5)
        self.cancel()


