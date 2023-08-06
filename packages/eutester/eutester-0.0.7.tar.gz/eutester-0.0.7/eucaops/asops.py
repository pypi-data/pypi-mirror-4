# Software License Agreement (BSD License)
#
# Copyright (c) 2009-2013, Eucalyptus Systems, Inc.
# All rights reserved.
#
# Redistribution and use of this software in source and binary forms, with or
# without modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above
#   copyright notice, this list of conditions and the
#   following disclaimer.
#
#   Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the
#   following disclaimer in the documentation and/or other
#   materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: tony@eucalyptus.com
from eutester import Eutester
import re
import copy
import boto.ec2.autoscale
from boto.ec2.autoscale import ScalingPolicy
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.regioninfo import RegionInfo

ASRegionData = {
    'us-east-1': 'autoscaling.us-east-1.amazonaws.com',
    'us-west-1': 'autoscaling.us-west-1.amazonaws.com',
    'us-west-2': 'autoscaling.us-west-2.amazonaws.com',
    'eu-west-1': 'autoscaling.eu-west-1.amazonaws.com',
    'ap-northeast-1': 'autoscaling.ap-northeast-1.amazonaws.com',
    'ap-southeast-1': 'autoscaling.ap-southeast-1.amazonaws.com',
    'ap-southeast-2': 'autoscaling.ap-southeast-2.amazonaws.com',
    'sa-east-1': 'autoscaling.sa-east-1.amazonaws.com'}


class ASops(Eutester):
    def __init__(self, host=None, credpath=None, endpoint=None, aws_access_key_id=None, aws_secret_access_key=None,
                 username="root", region=None, is_secure=False, path='/', port=80, boto_debug=0):
        """
        :param host:
        :param credpath:
        :param endpoint:
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param username:
        :param region:
        :param is_secure:
        :param path:
        :param port:
        :param boto_debug:
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.account_id = None
        self.user_id = None
        super(ASops, self).__init__(credpath=credpath)

        self.setup_as_connection(host=host,
                                 region=region,
                                 endpoint=endpoint,
                                 aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key,
                                 is_secure=is_secure,
                                 path=path,
                                 port=port,
                                 boto_debug=boto_debug)
        self.poll_count = 48
        self.username = username
        self.test_resources = {}
        self.setup_as_resource_trackers()

    def setup_as_connection(self, endpoint=None, aws_access_key_id=None, aws_secret_access_key=None, is_secure=True,
                            host=None, region=None, path="/", port=443, boto_debug=0):
        """
        :param endpoint:
        :param aws_access_key_id:
        :param aws_secret_access_key:
        :param is_secure:
        :param host:
        :param region:
        :param path:
        :param port:
        :param boto_debug:
        :raise:
        """
        as_region = RegionInfo()
        if region:
            self.debug("Check region: " + str(region))
            try:
                if not endpoint:
                    as_region.endpoint = ASRegionData[region]
                else:
                    as_region.endpoint = endpoint
            except KeyError:
                raise Exception('Unknown region: %s' % region)
        else:
            as_region.name = 'eucalyptus'
            if not host:
                if endpoint:
                    as_region.endpoint = endpoint
                else:
                    as_region.endpoint = self.get_as_ip()
        connection_args = {'aws_access_key_id': aws_access_key_id,
                           'aws_secret_access_key': aws_secret_access_key,
                           'is_secure': is_secure,
                           'debug': boto_debug,
                           'port': port,
                           'path': path,
                           'region': as_region}

        if re.search('2.6', boto.__version__):
            connection_args['validate_certs'] = False
        try:
            as_connection_args = copy.copy(connection_args)
            as_connection_args['path'] = path
            as_connection_args['region'] = as_region
            self.debug("Attempting to create auto scale connection to " + as_region.endpoint + ":" + str(port) + path)
            self.autoscale = boto.ec2.autoscale.AutoScaleConnection(**as_connection_args)
        except Exception, e:
            self.critical("Was unable to create auto scale connection because of exception: " + str(e))

        #Source ip on local test machine used to reach instances
        self.as_source_ip = None

    def setup_as_resource_trackers(self):
        """
        Setup keys in the test_resources hash in order to track artifacts created
        """
        self.test_resources["keypairs"] = []
        self.test_resources["security-groups"] = []
        self.test_resources["images"] = []

    def create_launch_config(self, name=None, image_id=None, key_name=None, security_groups=None):
        """
        Creates a new launch configuration with specified attributes.

        :param name: Name of the launch configuration to create. (Required)
        :param image_id: Unique ID of the Amazon Machine Image (AMI) assigned during registration. (Required)
        :param key_name: The name of the EC2 key pair.
        :param security_groups: Names of the security groups with which to associate the EC2 instances.
        """
        lc = LaunchConfiguration(name=name,
                                 image_id=image_id,
                                 key_name=key_name,
                                 security_groups=security_groups)
        self.debug("Creating launch config: " + name)
        self.autoscale.create_launch_configuration(lc)

    def describe_launch_config(self, names=None):
        """
        return a list of launch configs

        :param names: list of names to query (optional) otherwise return all launch configs
        :return:
        """
        return self.autoscale.get_all_launch_configurations(names=names)

    def delete_launch_config(self, launch_config_name):
        self.debug("Deleting launch config: " + launch_config_name)
        self.autoscale.delete_launch_configuration(launch_config_name)

    def create_as_group(self, group_name=None, load_balancers=None, availability_zones=None, launch_config=None,
                        min_size=None, max_size=None, connection=None):
        """
        Create auto scaling group.

        :param group_name: Name of autoscaling group (required).
        :param load_balancers: List of load balancers.
        :param availability_zones: List of availability zones (required).
        :param launch_config: Name of launch configuration (required).
        :param min_size:  Minimum size of group (required).
        :param max_size: Maximum size of group (required).
        :param connection: connection to auto scaling service
        """
        as_group = AutoScalingGroup(group_name=group_name,
                                    load_balancers=load_balancers,
                                    availability_zones=availability_zones,
                                    launch_config=launch_config,
                                    min_size=min_size,
                                    max_size=max_size,
                                    connection=connection)
        self.debug("Creating Auto Scaling group: " + group_name)
        self.autoscale.create_auto_scaling_group(as_group)

    def describe_as_group(self, names=None):
        return self.autoscale.get_all_groups(names=names)

    def delete_as_group(self, names=None, force=None):
        self.debug("Deleting Auto Scaling Group: " + names)
        self.debug("Forcing: " + str(force))
        self.autoscale.delete_auto_scaling_group(name=names, force_delete=force)

    def create_as_policy(self, name=None, adjustment_type=None, as_name=None, scaling_adjustment=None, cooldown=None):
        """
        Create an auto scaling policy

        :param name:
        :param adjustment_type: (ChangeInCapacity, ExactCapacity, PercentChangeInCapacity)
        :param as_name:
        :param scaling_adjustment:
        :param cooldown: (if something gets scaled, the wait in seconds before trying again.)
        """
        scaling_policy = ScalingPolicy(name=name,
                                       adjustment_type=adjustment_type,
                                       as_name=as_name,
                                       scaling_adjustment=scaling_adjustment,
                                       cooldown=cooldown)
        self.debug("Creating Auto Scaling Policy: " + name)
        self.autoscale.create_scaling_policy(scaling_policy)

    def describe_as_policies(self, as_group=None, policy_names=None):
        self.autoscale.get_all_policies(as_group=as_group, policy_names=policy_names)

    def execute_as_policy(self, policy_name=None, as_group=None, honor_cooldown=None):
        self.debug("Executing Auto Scaling Policy: " + policy_name)
        self.autoscale.execute_policy(policy_name=policy_name, as_group=as_group, honor_cooldown=honor_cooldown)

    def delete_as_policy(self, policy_name=None, autoscale_group=None):
        self.debug("Deleting Policy: " + policy_name + " from group: " + autoscale_group)
        self.autoscale.delete_policy(policy_name=policy_name,autoscale_group=autoscale_group)

    def delete_all_autoscaling_groups(self):
        """
        This will attempt to delete all launch configs and all auto scaling groups
        """
        ### clear all ASGs
        for asg in self.describe_as_group():
            self.debug("Found Auto Scaling Group: " + asg.name)
            self.delete_as_group(names=asg.name, force=True)
        if len(self.describe_as_group()) != 0:
            self.debug("Some AS groups remain")
            for asg in self.describe_as_group():
                self.debug("Found Auto Scaling Group: " + asg.name)

    def delete_all_launch_configs(self):
        ### clear all LCs
        """
        Attempt to remove all launch configs
        """
        for lc in self.describe_launch_config():
            self.debug("Found Launch Config:" + lc.name)
            self.delete_launch_config(lc.name)
        if len(self.describe_launch_config()) != 0:
            self.debug("Some Launch Configs Remain")
            for lc in self.describe_launch_config():
                self.debug("Found Launch Config:" + lc.name)

    def get_as_ip(self):
        """Parse the eucarc for the EC2_URL"""
        as_url = self.parse_eucarc("AWS_AUTO_SCALING_URL")
        return as_url.split("/")[2].split(":")[0]

    # def wait_for_group(self, as_group=None, state="Successful", poll_count=None, timeout=480):
    #     """
    #     conn.get_all_activities(ag)
    #     autoscale_group, activity_ids=None
    #      [Activity:Launching a new EC2 instance status:Successful progress:100, ...]
    #     """
    #     if poll_count is not None:
    #         timeout = poll_count * 10
    #     self.debug("Beginning poll loop for group " + as_group + " to go to " + str(state) )
    #     start = time.time()
    #     elapsed = 0
    #     while(elapsed < timeout) and (self.AS.get_all_activities(as_group)[0].status != state):
    #         self.debug( "Auto Scaling Group(" + as_group.id + ") State(" + as_group.state + "), elapsed:" +
    #                     str(elapsed) + "/" + str(timeout))
    #         time.sleep(10)
    #         self.AS.get_all_activities(as_group)
    #         elapsed = int(time.time()- start)
    #         if self.AS.get_all_activities(as_group).status != instance_original_state:
    #             break
    #     self.debug("Instance("+as_group.id+") State("+as_group.state+") time elapsed (" +str(elapsed).split('.')[0]+")")
    #     #self.debug( "Waited a total o" + str( (self.poll_count - poll_count) * 10 ) + " seconds" )
    #     if as_group.state != state:
    #         raise Exception( str(as_group) + " did not enter "+str(state)+" state after elapsed:"+str(elapsed))
    #
    #     self.debug( str(as_group) + ' is now in ' + as_group.state )
    #     return True