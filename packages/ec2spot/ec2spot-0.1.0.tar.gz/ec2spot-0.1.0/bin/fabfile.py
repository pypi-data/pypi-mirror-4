from ec2spot.axis2c import Axis2CTestUbuntu
from fabric.api import *
import sys
import logging as logger
import time


def stop():
    s = Axis2CTestUbuntu()
    s.stop_instance()
    s.cancel()
    time.sleep(20)
    s.status()
    s.reservations()


def start():
    s = Axis2CTestUbuntu()
    s.status()
    s.spot_request()
    s.reservations()
    time.sleep(20)
    s.status()
    time.sleep(10)
    s.reservations()


def status():
    s = Axis2CTestUbuntu()
    s.reservations()
    s.status()
