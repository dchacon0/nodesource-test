from os import name
from typing import DefaultDict
from troposphere import Export, GetAtt, Sub, ec2
from troposphere import Ref, Parameter, Template, Output, Join

template = Template()

template.set_version("2010-09-09")
template.set_description(
    "CloudFormation template created from troposphere python library.This stack creates a VPC network with three subnets and therir respective components")


####################
# Parameters
####################
ProjectName_param = template.add_parameter(Parameter(
    "ProjectName",
    Description="Project Name",
    Default= "nodesource-test",
    Type="String",
))

VPCcidrblock_param = template.add_parameter(Parameter(
    "CIDRBlock",
    Description="CIDR Block for the VPC Network ",
    Default= "192.168.21.0/24",
    Type="String",
))

SubnetCIDR1_param = template.add_parameter(Parameter(
        "SubnetCIDR1",
        ConstraintDescription=("must be a valid IP CIDR range of the form x.x.x.x/x."),
        Description="IP Address range for the  Subnet 1 ",
        Default="192.168.21.0/26",
        Type="String",
    )
)


SubnetCIDR2_param = template.add_parameter(Parameter(
        "SubnetCIDR2",
        ConstraintDescription=("must be a valid IP CIDR range of the form x.x.x.x/x."),
        Description="IP Address range for the  Subnet 2 ",
        Default="192.168.21.64/26",
        Type="String",
    )
)


SubnetCIDR3_param = template.add_parameter(Parameter(
        "SubnetCIDR3",
        ConstraintDescription=("must be a valid IP CIDR range of the form x.x.x.x/x."),
        Description="IP Address range for the Subnet 3 ",
        Default="192.168.21.128/26",
        Type="String",
    )
)

####################
# Creating VPC 
####################
EC2VPC = template.add_resource(ec2.VPC(
    'EC2VPC',
    CidrBlock=Ref(VPCcidrblock_param),
    EnableDnsSupport=True,
    EnableDnsHostnames=True,
    InstanceTenancy='default',
    Tags=[
        {
            "Key": 'Name',
            "Value": Ref(ProjectName_param),
        }
    ]
))

EC2Subnet1 = template.add_resource(ec2.Subnet(
    'EC2Subnet',
    AvailabilityZone='us-east-1c',
    CidrBlock= Ref(SubnetCIDR1_param),
    VpcId=Ref(EC2VPC),
    MapPublicIpOnLaunch=True
))

EC2Subnet2 = template.add_resource(ec2.Subnet(
    'EC2Subnet2',
    AvailabilityZone='us-east-1b',
    CidrBlock=Ref(SubnetCIDR2_param),
    VpcId=Ref(EC2VPC),
    MapPublicIpOnLaunch=True
))

EC2Subnet3 = template.add_resource(ec2.Subnet(
    'EC2Subnet3',
    AvailabilityZone='us-east-1a',
    CidrBlock=Ref(SubnetCIDR3_param),
    VpcId=Ref(EC2VPC),
    MapPublicIpOnLaunch=True
))



EC2RouteTable = template.add_resource(ec2.RouteTable(
    'EC2RouteTable',
    VpcId=Ref(EC2VPC),
    Tags=[
        {
            "Key": 'Name',
            "Value": Ref(ProjectName_param)
        }
    ]
))

EC2InternetGateway = template.add_resource(ec2.InternetGateway(
    'EC2InternetGateway',
    Tags=[
        {
            "Key": 'Name',
            "Value": Ref(ProjectName_param)
        }
    ]
))


EC2Route = template.add_resource(ec2.Route(
    'EC2Route',
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=Ref(EC2InternetGateway),
    RouteTableId=Ref(EC2RouteTable)
))

EC2SubnetRouteTableAssociation = template.add_resource(ec2.SubnetRouteTableAssociation(
    'EC2SubnetRouteTableAssociation',
    RouteTableId=Ref(EC2RouteTable),
    SubnetId=Ref(EC2Subnet1)
))

EC2SubnetRouteTableAssociation2 = template.add_resource(ec2.SubnetRouteTableAssociation(
    'EC2SubnetRouteTableAssociation2',
    RouteTableId=Ref(EC2RouteTable),
    SubnetId=Ref(EC2Subnet2)
))

EC2SubnetRouteTableAssociation3 = template.add_resource(ec2.SubnetRouteTableAssociation(
    'EC2SubnetRouteTableAssociation3',
    RouteTableId=Ref(EC2RouteTable),
    SubnetId=Ref(EC2Subnet3)
))



EC2VPCGatewayAttachment = template.add_resource(ec2.VPCGatewayAttachment(
    'EC2VPCGatewayAttachment',
    InternetGatewayId=Ref(EC2InternetGateway),
    VpcId=Ref(EC2VPC)
))


####################
# Security Groups
####################


SecurityGroup_ALB = template.add_resource(ec2.SecurityGroup(
    'SecurityGroupALB',
    GroupDescription='Loadbalancer SG for nsolid cluster',
    GroupName=Join("", [Ref(ProjectName_param),"LoadBalancer-SG"]),
    Tags=[
        {
            "Key": 'Name',
            "Value": Join("", [Ref(ProjectName_param),"LoadBalancer-SG"])
        }
    ],    
    VpcId=Ref(EC2VPC),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            FromPort=80,
            Description='HTTP Traffic',
            IpProtocol='tcp',
            ToPort=80
        )
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            IpProtocol='-1'
        )
    ]
))


SecurityGroup_EC2 = template.add_resource(ec2.SecurityGroup(
    'SecurityGroupEC2',
    GroupDescription='ECS Allowed Ports',
    GroupName=Join("", [Ref(ProjectName_param),"EC2ForECSService-SG"]),
    Tags=[
        {
            "Key": 'Name',
            "Value": Join("", [Ref(ProjectName_param),"EC2ForECSService-SG"])
        }
    ],
    VpcId=Ref(EC2VPC),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            CidrIp=Ref(VPCcidrblock_param),
            Description='Internal Network',
            IpProtocol='-1'
        )
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            IpProtocol='-1'
        )
    ]
))


####################
# Outputs
####################

SubnetOneID_output = template.add_output(
    Output(
        "SubnetOneID",
        Description="SubnetId of the subnet 1",
        Value=Ref(EC2Subnet1),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet1id"))
    )
)

SubnetOneAZ_output = template.add_output(
    Output(
        "SubnetOneAZ",
        Description="AvalaibilityZone of the subnet 1",
        Value=GetAtt(EC2Subnet1, "AvailabilityZone"),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet1AZ"))
    )
)


SubnetTwoID_output = template.add_output(
    Output(
        "SubnetTwoID",
        Description="SubnetId of the subnet 2",
        Value=Ref(EC2Subnet2),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet2id"))
    )
)

SubnetTwoAZ_output = template.add_output(
    Output(
        "SubnetTwoAZ",
        Description="AvalaibilityZone of the subnet 2",
        Value=GetAtt(EC2Subnet2, "AvailabilityZone"),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet2AZ"))
    )
)


SubnetThreeID_output = template.add_output(
    Output(
        "SubnetThreeID",
        Description="SubnetId of the subnet 3",
        Value=Ref(EC2Subnet3),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet3id"))
    )
)
SubnetThreeAZ_output = template.add_output(
    Output(
        "SubnetThreeAZ",
        Description="AvalaibilityZone of the subnet 3",
        Value=GetAtt(EC2Subnet3, "AvailabilityZone"),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet3AZ"))
    )
)



VPCId_output = template.add_output(
    Output(
        "VPCId",
        Description="VPCId of the newly created VPC",
        Value=Ref(EC2VPC),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-vpcid"))
    )
)


SecurityGroupEC2id_output = template.add_output(
    Output(
        "SecurityGroupECid",
        Description="Security Group Id for EC2",
        Value=Ref(SecurityGroup_EC2),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-SecurityGroupEC2id"))
    )
)

SecurityGroupALBid_output = template.add_output(
    Output(
        "SecurityGroupALBid",
        Description="Security Group Id for ALB",
        Value=Ref(SecurityGroup_ALB),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-SecurityGroupALBid"))
    )
)



#print(template.to_yaml())
with open('network_nodesource-test.yaml', 'w') as f:
    f.write(template.to_yaml())


