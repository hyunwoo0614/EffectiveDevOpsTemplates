"""Generating CloudFormation template."""

from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
)

from ipaddress import ip_network
from ipify import get_ip

ApplicationPort = "3000"
PublicCidrIp = str(ip_network(get_ip()))

t = Template()

t.add_description("Effective DevOps in AWS: HelloWorld web application")

t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

t.add_resource(ec2.SecurityGroup(
    "SecurityGroup",
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp=PublicCidrIp,
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0",
        ),
    ],
))

ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo curl -sL https://rpm.nodesource.com/setup_8.x | sudo -E bash -",
    "sudo yum install -y wget nodejs --enablerepo=nodesource",
    "wget https://raw.githubusercontent.com/EffectiveDevOpsWithAWS/code-by-chapter/master/Chapter02/helloworld.js -O /home/ec2-user/helloworld.js",
    "wget https://raw.githubusercontent.com/EffectiveDevOpsWithAWS/code-by-chapter/master/Chapter02/helloworld.conf -O /etc/init//helloworld.conf",
    "node /home/ec2-user/helloworld.js"
]))

t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-05b3bcf7f311194b3",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
))

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ]),
))

print(t.to_json())
