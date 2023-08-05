from ec2spot.spot import SpotInstanceRequest
import logging as logger

class Axis2CTestInstance(SpotInstanceRequest):
    def __init__(self):
        self.price = "0.007"
        self.instance = "m1.small"
        self.key = "DjangoTutorial"
        self.axis2c_src = "http://people.apache.org/~dinesh/axis2c/1.7.0/RC6/axis2c-src-1.7.0.tar.gz"
        logger.basicConfig(filename='ec2.log', level=logger.DEBUG, format='%(asctime)s %(message)s',
                           datefmt='%m/%d/%Y %I:%M:%S %p')

        super(Axis2CTestInstance, self).__init__()

    def spot_request(self):
        self.config_script()
        logger.debug(self.script)
        self.spot = self.conn.request_spot_instances(self.price,
                                                     image_id=self.image,
                                                     availability_zone_group=self.region,
                                                     key_name=self.key,
                                                     instance_type=self.instance,
                                                     user_data=self.script)


    def  config_script(self):
        self.script = """#!/bin/bash
set -e -x
echo "From: dinesh@apache.org" >> /tmp/mail.tmp
echo "To: xydinesh@gmail.com" >> /tmp/mail.tmp

# %s update
%s install -y %s &> /tmp/apt.log
cat /tmp/mail.tmp > /tmp/sendmail.txt
echo "Subject: apt log" >> /tmp/sendmail.txt
cat /tmp/apt.log >> /tmp/sendmail.txt
sendmail -ti   < /tmp/sendmail.txt

cd /tmp
wget %s -o /tmp/wget.log
cat /tmp/mail.tmp > /tmp/sendmail.txt
echo "Subject: wget log" >> /tmp/sendmail.txt
cat /tmp/wget.log >> /tmp/sendmail.txt
sendmail -ti < /tmp/sendmail.txt

tar xvfz axis2c-src-1.7.0.tar.gz
cd axis2c-src-1.7.0
./configure --prefix $PWD/deploy &> /tmp/axis2.log
cat /tmp/mail.tmp > /tmp/sendmail.txt
echo "Subject: config log" >> /tmp/sendmail.txt
cat /tmp/axis2.log >> /tmp/sendmail.txt
sendmail -ti < /tmp/sendmail.txt

make &> /tmp/make.log
cat /tmp/mail.tmp > /tmp/sendmail.txt
echo "Subject: make log" >> /tmp/sendmail.txt
cat /tmp/make.log >> /tmp/sendmail.txt
sendmail -ti < /tmp/sendmail.txt

make install > /tmp/make.install.log
cat /tmp/mail.tmp > /tmp/sendmail.txt
echo "Subject: make install log" >> /tmp/sendmail.txt
cat /tmp/make.install.log >> /tmp/sendmail.txt
sendmail -ti < /tmp/sendmail.txt
""" % (self.install_cmd, self.install_cmd, " ".join(self.packages), self.axis2c_src)


class Axis2CTestUbuntu(Axis2CTestInstance):
    def __init__(self):
        self.image = "ami-3b4ff252"
        self.packages = ["gcc", "g++", "make", "autoconf", "python-dev", "git", "subversion", "libapr1",
                         "libapr1-dev", "libaprutil1", "emacs", "autoconf", "automake", "libxml2", "libtool",
                         "libxml2-dev", "zlibc", "apache2-mpm-worker", "sendmail", "pkg-config"]
        self.install_cmd = "apt-get"
        super(Axis2CTestUbuntu, self).__init__()


class Axis2CTestFedora(Axis2CTestInstance):
    def __init__(self):
        self.image = "ami-84db39ed"
        # amazon image x64
        self.image = "ami-1624987f" 
        self.packages = ["gcc", "gcc-c++", "subversion",  "apr", "apr-devel", "apr-util", "httpd", "httpd-devel",
                         "emacs", "autoconf", "automake", "libxml2", "libtool", "libxml2-devel", "zlib", "zlib-devel",
                         "sendmail", "make"]
        self.install_cmd = "yum"
        super(Axis2CTestFedora, self).__init__()
