from os import name
from typing import DefaultDict
from troposphere import Export, Sub, ec2, elasticloadbalancingv2
from troposphere import Ref, Parameter, GetAtt, Template, Output

template = Template()

template.set_version("2010-09-09")
template.set_description(
    "CloudFormation template created from troposphere python library.This stack create a VPC network with three subnets and therir respective components")

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

SubnetTwoID_output = template.add_output(
    Output(
        "SubnetTwoID",
        Description="SubnetId of the subnet 2",
        Value=Ref(EC2Subnet2),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-subnet2id"))
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

VPCId_output = template.add_output(
    Output(
        "VPCId",
        Description="VPCId of the newly created VPC",
        Value=Ref(EC2VPC),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-vpcid"))
    )
)
#print(template.to_yaml())
with open('network_nodesource-test.yaml', 'w') as f:
    f.write(template.to_yaml())


