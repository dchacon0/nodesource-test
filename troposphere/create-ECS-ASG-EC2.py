# ECS Capacity provider should be attached manually, becaouse its not yet possible to get ARN from AutoScalingGroup using attributes (https://github.com/aws-cloudformation/cloudformation-coverage-roadmap/issues/548)

from os import name
from typing import DefaultDict
from troposphere import autoscaling, autoscalingplans, iam, ecs
from troposphere.iam import InstanceProfile, PolicyType, Role
from troposphere import Ref, GetAtt, Template, Join, Parameter, ImportValue, Base64
from troposphere.policies import (
    AutoScalingReplacingUpdate,
    AutoScalingRollingUpdate,
    UpdatePolicy,
)
 

template = Template()

template.set_version("2010-09-09")
template.set_description(
    "CloudFormation template created from troposphere python library.This stack creates the ECS Cluster , ASG and their respective components in EC2")

####################
# Parameters
####################
ProjectName_param = template.add_parameter(Parameter(
    "ProjectName",
    Description="Project Name",
    Default= "nodesource-test2",
    Type="String",
))

ECSClusterName_param = template.add_parameter(Parameter(
    "ECSClusterName",
    Description="ECS Cluster Name",
    Default= "nodesource-test2",
    Type="String",
))


####################
# ECS Cluster
####################
ECSCluster = template.add_resource(ecs.Cluster(
    'ECSCluster',
    ClusterName=Ref(ECSClusterName_param),
    # ClusterSettings=[
    #     {
    #         "Name": 'containerInsights',
    #         "Value": 'disabled'
    #     }
    # ]
    # CapacityProviders=[
    #     'nodesource-test-capacityprovider'
    # ]
    
))

## Its not yet possible to get ARN from AutoScalingGroup using attributes (https://github.com/aws-cloudformation/cloudformation-coverage-roadmap/issues/548)
""" ECSCapacityProvider = template.add_resource(ecs.CapacityProvider(
    'ECSCapacityProvider',
    Name='nodesource-test-capacityprovider',
    AutoScalingGroupProvider={
        "AutoScalingGroupArn": 'arn:aws:autoscaling:us-east-1:1234567890123:autoScalingGroup:df0c7b13-30d6-4b8a-837e-a6aa47ec00dc:autoScalingGroupName/EC2ContainerService-nodesource-test-EcsInstanceAsg-1GX2MZ6673X3K',
        "ManagedTerminationProtection": 'ENABLED',
        "ManagedScaling": {
            'MaximumScalingStepSize': 10000,
            'MinimumScalingStepSize': 1,
            'Status': 'ENABLED',
            'TargetCapacity': 80
        }
    }
))

ECSCapacityProviderAssociation = template.add_resource(ecs.ClusterCapacityProviderAssociations(
    'ECSCapacityProviderAssociation',
    Name='nodesource-test-capacityprovider',
    AutoScalingGroupProvider={
        "AutoScalingGroupArn": 'arn:aws:autoscaling:us-east-1:1234567890123:autoScalingGroup:df0c7b13-30d6-4b8a-837e-a6aa47ec00dc:autoScalingGroupName/EC2ContainerService-nodesource-test-EcsInstanceAsg-1GX2MZ6673X3K',
        "ManagedTerminationProtection": 'ENABLED',
        "ManagedScaling": {
            'MaximumScalingStepSize': 10000,
            'MinimumScalingStepSize': 1,
            'Status': 'ENABLED',
            'TargetCapacity': 80
        }
    }
))
 """

####################
# IAM Roles
####################


IAMRole = template.add_resource(iam.Role(
    'IAMRole',
    Path='/',
    #RoleName='containerInstanceECSRole-nsolid-lab',
    RoleName=Join("",["containerInstanceECSRole-",Ref(ECSClusterName_param)]),
    AssumeRolePolicyDocument={"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]},
    MaxSessionDuration=3600,
    PermissionsBoundary='arn:aws:iam::1234567890123:policy/ScopePermissions', ## Change this parameter #todo
    ManagedPolicyArns=["arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"],
    Description='Allows EC2 instances to call AWS services on your behalf.',
    Tags=[
        {
            "Key": 'Name',
            "Value": 'AmazonEC2ContainerServiceforEC2Role-nsolid-lab'
        }
    ]
))

IAMRole2 = template.add_resource(iam.Role(
    'IAMRole2',
    Path='/',
    #RoleName='ecsAutoscaleRole',
    RoleName=Join("",["ecsAutoscaleRole-",Ref(ECSClusterName_param)]),
    AssumeRolePolicyDocument={"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]},
    MaxSessionDuration=3600,
    PermissionsBoundary='arn:aws:iam::1234567890123:policy/ScopePermissions',
    ManagedPolicyArns=["arn:aws:iam::aws:policy/service-role/AmazonEC2SpotFleetAutoscaleRole","arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceAutoscaleRole"],
    Description='Allows EC2 instances to call AWS services on your behalf.',
    Tags=[
        {
            "Key": 'Name',
            "Value": Join("",["ecsAutoscaleRole-",Ref(ECSClusterName_param)])
        }
    ]
))

IAMServiceLinkedRole = template.add_resource(iam.ServiceLinkedRole(
    'IAMServiceLinkedRole',
    AWSServiceName='ecs.amazonaws.com',
    Description='Role to enable Amazon ECS to manage your cluster.'
))


EC2InstanceProfile = template.add_resource(
    InstanceProfile(
        "EC2InstanceProfile",
        Path="/",
        Roles=[Ref(IAMRole)],
        
    )
    
)
####################
# Auto Scaling Group
####################

AutoScalingLaunchConfiguration = template.add_resource(autoscaling.LaunchConfiguration(
    'AutoScalingLaunchConfiguration',
    #LaunchConfigurationName='EC2ContainerService-nodesource-test-EcsInstance',
    LaunchConfigurationName=Join("",["EC2ContainerService-",Ref(ECSClusterName_param),"-EcsInstance"]),
    ImageId='ami-091aa67fccd794d5f', ## Replace here with the most updated AMi for ECS
    #KeyName='nsolid-lab',
    SecurityGroups=[
        ImportValue("create-network-nodesource-SecurityGroupEC2id") #Replace with the output of the SecurityGroup id
    ],
    #UserData='IyEvYmluL2Jhc2gKZWNobyBFQ1NfQ0xVU1RFUj1ub2Rlc291cmNlLXRlc3QgPj4gL2V0Yy9lY3MvZWNzLmNvbmZpZztlY2hvIEVDU19CQUNLRU5EX0hPU1Q9ID4+IC9ldGMvZWNzL2Vjcy5jb25maWc7',
    UserData=Base64(
        Join(
            "",
            [
                "#!/bin/bash\n",
                "echo ECS_CLUSTER=",
                Ref(ECSClusterName_param),
                ">>/etc/ecs/ecs.config",
                "\n",
                "echo ECS_BACKEND_HOST= >> /etc/ecs/ecs.config;",
                "\n",
            ],
        )
    ),
    
    InstanceType='t3.medium',
    BlockDeviceMappings=[
        autoscaling.BlockDeviceMapping(
            DeviceName='/dev/xvda',
            Ebs=autoscaling.EBSBlockDevice(
                VolumeSize=30,
                VolumeType='gp2'
            )
        )
    ],
    InstanceMonitoring=True,
    #IamInstanceProfile='arn:aws:iam::1234567890123:instance-profile/containerInstanceECSRole-nsolid-lab',
    IamInstanceProfile=GetAtt(EC2InstanceProfile, "Arn"),
    EbsOptimized=False,
    AssociatePublicIpAddress=True
))

AutoScalingAutoScalingGroup = template.add_resource(autoscaling.AutoScalingGroup(
    'AutoScalingAutoScalingGroup',
    #AutoScalingGroupName='EC2ContainerService-nodesource-test-EcsInstanceAsg',
    AutoScalingGroupName=Join("",["EC2ContainerService-",Ref(ECSClusterName_param),"-EcsInstanceAsg"]),
    LaunchConfigurationName=Ref(AutoScalingLaunchConfiguration),
    MinSize=0,
    MaxSize=3,
    DesiredCapacity=3,
    Cooldown=300,
    AvailabilityZones=[
        ImportValue("create-network-nodesource-subnet1AZ"),
        ImportValue("create-network-nodesource-subnet2AZ"),
        ImportValue("create-network-nodesource-subnet3AZ")
    ],
    HealthCheckType='EC2',

    UpdatePolicy=UpdatePolicy(
        AutoScalingReplacingUpdate=AutoScalingReplacingUpdate(
            WillReplace=True,
        ),
        AutoScalingRollingUpdate=AutoScalingRollingUpdate(
            PauseTime="PT5M",
            MinInstancesInService="1",
            MaxBatchSize="1",
            WaitOnResourceSignals=True,
        ),
    ),    
    HealthCheckGracePeriod=0,
    VPCZoneIdentifier=[
        ImportValue("create-network-nodesource-subnet1id"),
        ImportValue("create-network-nodesource-subnet2id"),
        ImportValue("create-network-nodesource-subnet3id")
    ],
    TerminationPolicies=[
        'Default'
    ],
    #ServiceLinkedRoleARN='arn:aws:iam::1234567890123:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling',
    Tags=[
        {
            "Key": 'Name',
            "Value": Join("",["EC2ContainerService-",Ref(ECSClusterName_param),"-EcsInstanceAsg"]),
            "PropagateAtLaunch": True
        }
    ],
    
    NewInstancesProtectedFromScaleIn=False
))

# AutoScalingScalingPolicy = template.add_resource(autoscaling.ScalingPolicy(
#     'AutoScalingScalingPolicy',
#     AutoScalingGroupName=Ref(AutoScalingAutoScalingGroup),
#     PolicyType='TargetTrackingScaling',
#     EstimatedInstanceWarmup=300,
   
    # TargetTrackingConfiguration=autoscaling.TargetTrackingConfiguration(
    #     CustomizedMetricSpecification=autoscaling.MetricDimension(
    #         MetricName='CapacityProviderReservation',
    #         Namespace='AWS/ECS/ManagedScaling',
    #         Dimensions=[
    #             {
    #                 "Name": 'CapacityProviderName',
    #                 #"Value": 'nodesource-test-capacityprovider'
    #                 "Value": Join("", [Ref(ECSClusterName_param),"capacityprovider"])
    #             },
    #             {
    #                 "Name": 'ClusterName',
    #                 "Value": Ref(ECSClusterName_param)
    #             }
    #         ],
    #         Statistic='Average'
    #     ),
    #     TargetValue=80,
    #     DisableScaleIn=False
    
# ))

# AutoScalingPlansScalingPlan = template.add_resource(autoscalingplans.ScalingPlan(
#     'AutoScalingPlansScalingPlan',
#     ApplicationSource={
#         "TagFilters": [
#             {
#                 'Key': 'AWSAutoScalingConsole-autoscaling-0',
#                 'Values': [
#                     'EC2ContainerService-nodesource-test-EcsInstanceAsg'
#                 ]
#             }
#         ]
#     },
#     ScalingInstructions=[
#         {
#             "ServiceNamespace": 'autoscaling',
#             "ResourceId": 'autoScalingGroup/EC2ContainerService-nodesource-test-EcsInstanceAsg',
#             "ScalableDimension": 'autoscaling:autoScalingGroup:DesiredCapacity',
#             "MinCapacity": 0,
#             "MaxCapacity": 3,
#             "TargetTrackingConfigurations": [
#                 {
#                     'CustomizedScalingMetricSpecification': {
#                         'MetricName': 'CapacityProviderReservation',
#                         'Namespace': 'AWS/ECS/ManagedScaling',
#                         'Dimensions': [
#                             {
#                                 "Name": 'CapacityProviderName',
#                                 #"Value": 'nodesource-test-capacityprovider'
#                                 "Value": Join("", [Ref(ECSClusterName_param),"capacityprovider"])
#                             },
#                             {
#                                 "Name": 'ClusterName',
#                                 "Value": Ref(ECSClusterName_param)
#                             }
#                         ],
#                         'Statistic': 'Average'
#                     },
#                     'TargetValue': 80,
#                     'DisableScaleIn': False,
#                     'EstimatedInstanceWarmup': 300
#                 }
#             ],
#             "ScalingPolicyUpdateBehavior": 'KeepExternalPolicies',
#             "DisableDynamicScaling": False
#         }
#     ]
# ))


#print(template.to_yaml())
with open('create-ECS-ASG-EC2.yaml', 'w') as f:
    f.write(template.to_yaml())


