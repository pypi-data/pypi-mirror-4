#!/usr/bin/env python
#
#
# Description:  This script encompasses test cases/modules concerning instance specific behavior and
#               features for Eucalyptus.  The test cases/modules that are executed can be 
#               found in the script under the "tests" list.

import unittest
import time
from boto.ec2.address import Address
from eucaops import Eucaops
from eutester.eutestcase import EutesterTestCase
from eutester.euvolume import EuVolume
import os
import re
import random


class InstanceBasics(EutesterTestCase):
    def __init__(self, extra_args= None):
        self.setuptestcase()
        self.setup_parser()
        if extra_args:
            for arg in extra_args:
                self.parser.add_argument(arg)
        self.get_args()
        # Setup basic eutester object
        self.tester = Eucaops( credpath=self.args.credpath)
        self.tester.poll_count = 120

        ### Add and authorize a group for the instance
        self.group = self.tester.add_group(group_name="group-" + str(time.time()))
        self.tester.authorize_group_by_name(group_name=self.group.name )
        self.tester.authorize_group_by_name(group_name=self.group.name, port=-1, protocol="icmp" )
        ### Generate a keypair for the instance
        self.keypair = self.tester.add_keypair( "keypair-" + str(time.time()))
        self.keypath = '%s/%s.pem' % (os.curdir, self.keypair.name)
        self.image = self.args.emi
        if not self.image:
            self.image = self.tester.get_emi(root_device_type="instance-store")
        self.address = None
        self.volume = None
        self.private_addressing = False
        zones = self.tester.ec2.get_all_zones()
        self.zone = random.choice(zones).name
        self.reservation = None

    def clean_method(self):
        if self.reservation:
            self.assertTrue(self.tester.terminate_instances(self.reservation), "Unable to terminate instance(s)")
        if self.address:
            assert isinstance(self.address,Address)
            self.tester.release_address(self.address)
        if self.volume:
            self.tester.delete_volume(self.volume)
        self.tester.delete_group(self.group)
        self.tester.delete_keypair(self.keypair)
        os.remove(self.keypath)


    def BasicInstanceChecks(self, zone = None):
        """
        This case was developed to run through a series of basic instance tests.
             The tests are as follows:
                   - execute run_instances command
                   - make sure that public DNS name and private IP aren't the same
                       (This is for Managed/Managed-NOVLAN networking modes)
                   - test to see if instance is ping-able
                   - test to make sure that instance is accessible via ssh
                       (ssh into instance and run basic ls command)
             If any of these tests fail, the test case will error out, logging the results.
        """
        if zone is None:
            zone = self.zone
        if not self.reservation:
            self.reservation = self.tester.run_instance(self.image, keypair=self.keypair.name, group=self.group.name, zone=zone)
        for instance in self.reservation.instances:
            self.assertTrue( self.tester.wait_for_reservation(self.reservation) ,'Instance did not go to running')
            self.assertNotEqual( instance.public_dns_name, instance.private_ip_address, 'Public and private IP are the same')
            self.assertTrue( self.tester.ping(instance.public_dns_name), 'Could not ping instance')
            self.assertFalse( instance.found("ls -1 /dev/" + instance.rootfs_device + "2",  "No such file or directory"),  'Did not find ephemeral storage at ' + instance.rootfs_device + "2")
        return self.reservation

    def ElasticIps(self, zone = None):
        """
       This case was developed to test elastic IPs in Eucalyptus. This test case does
       not test instances that are launched using private-addressing option.
       The test case executes the following tests:
           - allocates an IP, associates the IP to the instance, then pings the instance.
           - disassociates the allocated IP, then pings the instance.
           - releases the allocated IP address
       If any of the tests fail, the test case will error out, logging the results.
        """
        if zone is None:
            zone = self.zone
        if not self.reservation:
            self.reservation = self.tester.run_instance(keypair=self.keypair.name, group=self.group.name,zone=zone)
        for instance in self.reservation.instances:
            self.address = self.tester.allocate_address()
            self.assertTrue(self.address,'Unable to allocate address')
            self.tester.associate_address(instance, self.address)
            instance.update()
            self.assertTrue( self.tester.ping(instance.public_dns_name), "Could not ping instance with new IP")
            self.tester.disassociate_address_from_instance(instance)
            self.tester.release_address(self.address)
            self.address = None
            instance.update()
            self.assertTrue( self.tester.ping(instance.public_dns_name), "Could not ping after dissassociate")
        return self.reservation

    def MaxSmallInstances(self, available_small=None,zone = None):
        """
        This case was developed to test the maximum number of m1.small vm types a configured
        cloud can run.  The test runs the maximum number of m1.small vm types allowed, then
        tests to see if all the instances reached a running state.  If there is a failure,
        the test case errors out; logging the results.
        """
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
        if available_small is None:
            available_small = self.tester.get_available_vms()
        if zone is None:
            zone = self.zone
        self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name,min=available_small, max=available_small, zone=zone)
        self.assertTrue( self.tester.wait_for_reservation(self.reservation) ,'Not all instances  went to running')
        return self.reservation

    def LargestInstance(self, zone = None):
        """
        This case was developed to test the maximum number of c1.xlarge vm types a configured
        cloud can run.  The test runs the maximum number of c1.xlarge vm types allowed, then
        tests to see if all the instances reached a running state.  If there is a failure,
        the test case errors out; logging the results.
        """
        if zone is None:
            zone = self.zone
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
        self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name,type="c1.xlarge",zone=zone)
        self.assertTrue( self.tester.wait_for_reservation(self.reservation) ,'Not all instances  went to running')
        return self.reservation

    def MetaData(self, zone=None):
        """
        This case was developed to test the metadata service of an instance for consistency.
        The following meta-data attributes are tested:
           - public-keys/0/openssh-key
           - security-groups
           - instance-id
           - local-ipv4
           - public-ipv4
           - ami-id
           - ami-launch-index
           - reservation-id
           - placement/availability-zone
           - kernel-id
           - public-hostname
           - local-hostname
           - hostname
           - ramdisk-id
           - instance-type
           - any bad metadata that shouldn't be present.
        Missing nodes
         ['block-device-mapping/',  'ami-manifest-path']
        If any of these tests fail, the test case will error out; logging the results.
        """
        if zone is None:
            zone = self.zone
        if not self.reservation:
            self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name, zone=zone)
        for instance in self.reservation.instances:
            ## Need to verify  the public key (could just be checking for a string of a certain length)
            self.assertTrue(re.match(instance.get_metadata("public-keys/0/openssh-key")[0].split('eucalyptus.')[-1], self.keypair.name), 'Incorrect public key in metadata')
            self.assertTrue(re.match(instance.get_metadata("security-groups")[0], self.group.name), 'Incorrect security group in metadata')
            # Need to validate block device mapping
            #self.assertTrue(re.search(instance_ssh.get_metadata("block-device-mapping/")[0], "")) 
            self.assertTrue(re.match(instance.get_metadata("instance-id")[0], instance.id), 'Incorrect instance id in metadata')
            self.assertTrue(re.match(instance.get_metadata("local-ipv4")[0] , instance.private_ip_address), 'Incorrect private ip in metadata')
            self.assertTrue(re.match(instance.get_metadata("public-ipv4")[0] , instance.ip_address), 'Incorrect public ip in metadata')
            self.assertTrue(re.match(instance.get_metadata("ami-id")[0], instance.image_id), 'Incorrect ami id in metadata')
            self.assertTrue(re.match(instance.get_metadata("ami-launch-index")[0], instance.ami_launch_index), 'Incorrect launch index in metadata')
            self.assertTrue(re.match(instance.get_metadata("reservation-id")[0], self.reservation.id), 'Incorrect reservation in metadata')
            self.assertTrue(re.match(instance.get_metadata("placement/availability-zone")[0], instance.placement), 'Incorrect availability-zone in metadata')
            self.assertTrue(re.match(instance.get_metadata("kernel-id")[0], instance.kernel),  'Incorrect kernel id in metadata')
            self.assertTrue(re.match(instance.get_metadata("public-hostname")[0], instance.public_dns_name), 'Incorrect public host name in metadata')
            self.assertTrue(re.match(instance.get_metadata("local-hostname")[0], instance.private_dns_name), 'Incorrect private host name in metadata')
            self.assertTrue(re.match(instance.get_metadata("hostname")[0], instance.dns_name), 'Incorrect host name in metadata')
            self.assertTrue(re.match(instance.get_metadata("ramdisk-id")[0], instance.ramdisk ), 'Incorrect ramdisk in metadata') #instance-type
            self.assertTrue(re.match(instance.get_metadata("instance-type")[0], instance.instance_type ), 'Incorrect instance type in metadata')
            BAD_META_DATA_KEYS = ['foobar']
            for key in BAD_META_DATA_KEYS:
                self.assertTrue(re.search("Not Found", "".join(instance.get_metadata(key))), 'No fail message on invalid meta-data node')
        return self.reservation

    def DNSResolveCheck(self, zone=None):
        """
        This case was developed to test DNS resolution information for public/private DNS
        names and IP addresses.  The tested DNS resolution behavior is expected to follow
        AWS EC2.  The following tests are ran using the associated meta-data attributes:
           - check to see if Eucalyptus Dynamic DNS is configured
           - nslookup on hostname; checks to see if it matches local-ipv4
           - nslookup on local-hostname; check to see if it matches local-ipv4
           - nslookup on local-ipv4; check to see if it matches local-hostname
           - nslookup on public-hostname; check to see if it matches local-ipv4
           - nslookup on public-ipv4; check to see if it matches public-host
        If any of these tests fail, the test case will error out; logging the results.
        """
        if zone is None:
            zone = self.zone
        if not self.reservation:
            self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name, zone=zone)
        for instance in self.reservation.instances:

            # Test to see if Dynamic DNS has been configured # 
            if re.match("internal", instance.private_dns_name.split('eucalyptus.')[-1]):
                # Per AWS standard, resolution should have private hostname or private IP as a valid response
                # Perform DNS resolution against private IP and private DNS name
                # Check to see if nslookup was able to resolve
                self.assertTrue(re.search('answer\:', instance.sys("nslookup " +  instance.get_metadata("hostname")[0])[3]), "DNS lookup failed for hostname.")
                # Since nslookup was able to resolve, now check to see if nslookup on local-hostname returns local-ipv4 address
                self.assertTrue(re.search(instance.get_metadata("local-ipv4")[0], instance.sys("nslookup " + instance.get_metadata("hostname")[0])[5]), "Incorrect DNS resolution for hostname.")
                # Check to see if nslookup was able to resolve
                self.assertTrue(re.search('answer\:', instance.sys("nslookup " +  instance.get_metadata("local-hostname")[0])[3]), "DNS lookup failed for private hostname.")
                # Since nslookup was able to resolve, now check to see if nslookup on local-hostname returns local-ipv4 address
                self.assertTrue(re.search(instance.get_metadata("local-ipv4")[0], instance.sys("nslookup " + instance.get_metadata("local-hostname")[0])[5]), "Incorrect DNS resolution for private hostname.")
                # Check to see if nslookup was able to resolve
                self.assertTrue(re.search('answer\:', instance.sys("nslookup " +  instance.get_metadata("local-ipv4")[0])[3]), "DNS lookup failed for private IP address.")
                # Since nslookup was able to resolve, now check to see if nslookup on local-ipv4 address returns local-hostname
                self.assertTrue(re.search(instance.get_metadata("local-hostname")[0], instance.sys("nslookup " +  instance.get_metadata("local-ipv4")[0])[4]), "Incorrect DNS resolution for private IP address")
                # Perform DNS resolution against public IP and public DNS name
                # Check to see if nslookup was able to resolve
                self.assertTrue(re.search('answer\:', instance.sys("nslookup " +  instance.get_metadata("public-hostname")[0])[3]), "DNS lookup failed for public-hostname.")
                # Since nslookup was able to resolve, now check to see if nslookup on public-hostname returns local-ipv4 address
                self.assertTrue(re.search(instance.get_metadata("local-ipv4")[0], instance.sys("nslookup " + instance.get_metadata("public-hostname")[0])[5]), "Incorrect DNS resolution for public-hostname.")
                # Check to see if nslookup was able to resolve
                self.assertTrue(re.search('answer\:', instance.sys("nslookup " +  instance.get_metadata("public-ipv4")[0])[3]), "DNS lookup failed for public IP address.")
                # Since nslookup was able to resolve, now check to see if nslookup on public-ipv4 address returns public-hostname
                self.assertTrue(re.search(instance.get_metadata("public-hostname")[0], instance.sys("nslookup " +  instance.get_metadata("public-ipv4")[0])[4]), "Incorrect DNS resolution for public IP address")

        return self.reservation

    def DNSCheck(self, zone=None):
        """
        This case was developed to test to make sure Eucalyptus Dynamic DNS reports correct
        information for public/private IP address and DNS names passed to meta-data service.
        The following tests are ran using the associated meta-data attributes:
           - check to see if Eucalyptus Dynamic DNS is configured
           - check to see if local-ipv4 and local-hostname are not the same
           - check to see if public-ipv4 and public-hostname are not the same
        If any of these tests fail, the test case will error out; logging the results.
        """
        if zone is None:
            zone = self.zone
        if not self.reservation:
            self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name, zone=zone)
        for instance in self.reservation.instances:

            # Test to see if Dynamic DNS has been configured # 
            if re.match("internal", instance.private_dns_name.split('eucalyptus.')[-1]):
                # Make sure that private_ip_address is not the same as local-hostname
                self.assertFalse(re.match(instance.private_ip_address, instance.private_dns_name), 'local-ipv4 and local-hostname are the same with DNS on')
                # Make sure that ip_address is not the same as public-hostname
                self.assertFalse(re.match(instance.ip_address, instance.public_dns_name), 'public-ipv4 and public-hostname are the same with DNS on')

        return self.reservation

    def Reboot(self, zone=None):
        """
        This case was developed to test IP connectivity and volume attachment after
        instance reboot.  The following tests are done for this test case:
                   - creates a 1 gig EBS volume, then attach volume
                   - reboot instance
                   - attempts to connect to instance via ssh
                   - checks to see if EBS volume is attached
                   - detaches volume
                   - deletes volume
        If any of these tests fail, the test case will error out; logging the results.
        """
        if zone is None:
            zone = self.zone
        if not self.reservation:
            self.reservation = self.tester.run_instance(self.image, keypair=self.keypair.name, group=self.group.name, zone=zone)
        for instance in self.reservation.instances:
            ### Create 1GB volume in first AZ
            self.volume = self.tester.create_volume(instance.placement, 1)
            self.volume_device = instance.attach_volume(self.volume)
            ### Reboot instance
            instance.reboot_instance_and_verify(waitconnect=20)
            instance.detach_euvolume(self.volume)
            self.tester.delete_volume(self.volume)
            self.volume = None
        return self.reservation

    def run_terminate(self):
        reservation = None
        try:
            reservation = self.tester.run_instance(image=self.image,zone=self.zone, keypair=self.keypair.name, group=self.group.name)
            self.tester.terminate_instances(reservation)
            return 0
        except Exception, e:
            if reservation:
                self.tester.terminate_instances(reservation)
            return 1

    def Churn(self,image_id=None):
        """
        This case was developed to test robustness of Eucalyptus by starting instances,
        stopping them before they are running, and increase the time to terminate on each
        iteration.  This test case leverages the BasicInstanceChecks test case. The
        following steps are ran:
            - runs BasicInstanceChecks test case 5 times, 10 second apart.
            - While each test is running, run and terminate instances with a 10sec sleep in between.
            - When a test finishes, rerun BasicInstanceChecks test case.
        If any of these tests fail, the test case will error out; logging the results.
        """
        if not image_id:
            image_id = self.image
        from eutester.process_manager import ProcessManager
        process_manager = ProcessManager()
        ### Increase time to terminate by step seconds on each iteration
        step = 1
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
            ## Run through count iterations of test
        count = self.tester.get_available_vms("m1.small") / 2

        ## Start asynchronous activity
        ## Run 5 basic instance check instances 10s apart
        process_ids =[]
        for i in xrange(count):
            self.tester.debug("Starting Thread " + str(i) +" in " + str(step))
            self.tester.sleep(step)
            tester = Eucaops( credpath=self.args.credpath)
            process_ids.append(process_manager.run_method_as_process(tester.run_instance,image=image_id, is_reachable=False))

        ### While the other tests are running, run and terminate count instances with a 10s sleep in between
        for i in xrange(count):
            self.reservation = self.image.run()
            self.tester.debug("Sleeping for " + str(step) + " seconds before terminating instances")
            self.tester.sleep(step)
            for instance in self.reservation.instances:
                instance.terminate()
                self.assertTrue(self.tester.wait_for_instance(instance, "terminated"), "Instance did not go to terminated")

        results = []
        ### Block until the script returns a result
        for id in process_ids:
            results.append(process_manager.wait_for_process(id))

        process_ids =[]
        for return_value in results:
            if isinstance(return_value, Exception):
                raise result
            else:
                process_ids.append(process_manager.run_method_as_process(self.tester.terminate_instances,return_value))

        for id in process_ids:
            results.append(process_manager.wait_for_process(id))

    def PrivateIPAddressing(self, zone = None):
        """
        This case was developed to test instances that are launched with private-addressing
        set to True.  The tests executed are as follows:
            - run an instance with private-addressing set to True
            - allocate/associate/disassociate/release an Elastic IP to that instance
            - check to see if the instance went back to private addressing
        If any of these tests fail, the test case will error out; logging the results.
        """
        if zone is None:
            zone = self.zone
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
        self.reservation = self.tester.run_instance(keypair=self.keypair.name, group=self.group.name, private_addressing=True, zone=zone)
        for instance in self.reservation.instances:
            address = self.tester.allocate_address()
            self.assertTrue(address,'Unable to allocate address')
            self.tester.associate_address(instance, address)
            self.tester.sleep(30)
            instance.update()
            self.assertTrue( self.tester.ping(instance.public_dns_name), "Could not ping instance with new IP")
            address.disassociate()
            self.tester.sleep(30)
            instance.update()
            self.assertFalse( self.tester.ping(instance.public_dns_name), "Was able to ping instance that should have only had a private IP")
            address.release()
            if instance.public_dns_name != instance.private_dns_name:
                self.fail("Instance received a new public IP: " + instance.public_dns_name)
        return self.reservation

    def ReuseAddresses(self, zone = None):
        """
        This case was developed to test when you run instances in a series, and make sure
        they get the same address.  The test launches an instance, checks the IP information,
        then terminates the instance. This test is launched 5 times in a row.  If there
        is an error, the test case will error out; logging the results.
        """
        prev_address = None
        if zone is None:
            zone = self.zone
            ### Run the test 5 times in a row
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
        for i in xrange(5):
            self.reservation = self.tester.run_instance(keypair=self.keypair.name, group=self.group.name, zone=zone)
            for instance in self.reservation.instances:
                if prev_address is not None:
                    self.assertTrue(re.search(str(prev_address) ,str(instance.public_dns_name)), str(prev_address) +" Address did not get reused but rather  " + str(instance.public_dns_name))
                prev_address = instance.public_dns_name
            self.tester.terminate_instances(self.reservation)

if __name__ == "__main__":
    testcase = InstanceBasics()
    ### Either use the list of tests passed from config/command line to determine what subset of tests to run
    list = testcase.args.tests or [ "BasicInstanceChecks",  "ElasticIps", "MaxSmallInstances" , "LargestInstance",
                                    "MetaData", "Reboot","PrivateIPAddressing"]
    ### Convert test suite methods to EutesterUnitTest objects
    unit_list = [ ]
    for test in list:
        unit_list.append( testcase.create_testunit_by_name(test) )
    ### Run the EutesterUnitTest objects

    result = testcase.run_test_case_list(unit_list,clean_on_exit=True)
    exit(result)


