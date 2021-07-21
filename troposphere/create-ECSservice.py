
from os import name
from typing import DefaultDict
from troposphere import ecs
from troposphere import Ref, GetAtt, Template, Parameter, ImportValue, Join, Output, Export, Sub
template = Template()

template.set_version("2010-09-09")
template.set_description(
    "CloudFormation template created from troposphere python library.This stack creates ECS Service")

####################
# Parameters
####################
ProjectName_param = template.add_parameter(Parameter(
    "ProjectName",
    Description="Project Name",
    Default= "nodesource-test2",
    Type="String",
))



####################
# ECS Service
####################

ECSService = template.add_resource(ecs.Service(
    'ECSService',
    #ServiceName='nodesource-test-service',
    ServiceName=Join("",[Ref(ProjectName_param),"-service"]),

    #Cluster=GetAtt(ECSCluster, 'Arn'),
    Cluster=ImportValue("create-ECS-ASG-EC2-nodesource-ECSclusterARN"),
    LoadBalancers=[
        ecs.LoadBalancer(
            TargetGroupArn=ImportValue("create-taskdef-ALB-nodesource-LoadBalancerTargetGroupARN"),
            ContainerName='nsolid',
            ContainerPort=8888
        )
    ],
    DesiredCount=3,
    LaunchType='EC2',
    TaskDefinition=ImportValue("create-taskdef-ALB-nodesource-TaskDefinitionARN"),
    #DeploymentConfiguration={ "MaximumPercent": 200, "MinimumHealthyPercent": 100, "DeploymentCircuitBreaker": { "Enable": False, "Rollback": False } },
    
    DeploymentConfiguration=ecs.DeploymentConfiguration(
        MaximumPercent=200,
        MinimumHealthyPercent=100,
        DeploymentCircuitBreaker = ecs.DeploymentCircuitBreaker(
            Enable= False,
            Rollback = False
        )
    ),
    #Role='arn:aws:iam::123456789123:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS',
    
    PlacementStrategies=[
        ecs.PlacementStrategy(
            Type='spread',
            Field='attribute:ecs.availability-zone'
        ),
        ecs.PlacementStrategy(
            Type='spread',
            Field='instanceId'
        )
    ],
    HealthCheckGracePeriodSeconds=0,
    SchedulingStrategy='REPLICA'
))


with open('create-ECSservice.yaml', 'w') as f:
    f.write(template.to_yaml())

