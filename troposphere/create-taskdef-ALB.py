from os import name
from typing import DefaultDict
from troposphere import ImportValue, Join, ec2, elasticloadbalancingv2, ecs
from troposphere import Ref, GetAtt, Template, Parameter, ImportValue, Join, Output, Export, Sub

template = Template()

template.set_version("2010-09-09")
template.set_description(
    "CloudFormation template created from troposphere python library.This stack creates ALB and task definition ")

####################
# Parameters
####################
ProjectName_param = template.add_parameter(Parameter(
    "ProjectName",
    Description="Project Name",
    Default= "nodesource-test2",
    Type="String",
))

ECRurl_param = template.add_parameter(Parameter(
    "ECRurl",
    Description="URL of the public repository (ECR)",
    Default= "public.ecr.aws/m5z1k1h8/nsolid-test",
    Type="String",
))


####################
# Application Load Balancer
####################
ElasticLoadBalancingV2LoadBalancer = template.add_resource(elasticloadbalancingv2.LoadBalancer(
    'ElasticLoadBalancingV2LoadBalancer',
    #Name='nodesource-test-loadbalancer',
    Name=Join("",[Ref(ProjectName_param),"-loadbalancer"]),
    Scheme='internet-facing',
    Type='application',
    Subnets=[
        ImportValue("createvpc-testing-nodesource-subnet1id"),
        ImportValue("createvpc-testing-nodesource-subnet2id"),
        ImportValue("createvpc-testing-nodesource-subnet3id")
    ],
    SecurityGroups=[
        ImportValue("createvpc-testing-nodesource-SecurityGroupALBid")
    ],
    IpAddressType='ipv4',
    LoadBalancerAttributes=[
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='access_logs.s3.enabled',
            Value='false'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='idle_timeout.timeout_seconds',
            Value='60'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='deletion_protection.enabled',
            Value='false'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='routing.http2.enabled',
            Value='true'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='routing.http.drop_invalid_header_fields.enabled',
            Value='false'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='routing.http.desync_mitigation_mode',
            Value='defensive'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='waf.fail_open.enabled',
            Value='false'
        ),
        elasticloadbalancingv2.LoadBalancerAttributes(
            Key='routing.http.x_amzn_tls_version_and_cipher_suite.enabled',
            Value='false'
        )
    ]
))

ElasticLoadBalancingV2TargetGroup = template.add_resource(elasticloadbalancingv2.TargetGroup(
    'ElasticLoadBalancingV2TargetGroup',
    #Name='nodesource-test-targetgroup',
    Name=Join("",[Ref(ProjectName_param),"targetgroup"]),
    HealthCheckIntervalSeconds=30,
    HealthCheckPath='/',
    Port=8888,
    Protocol='HTTP',
    HealthCheckPort='traffic-port',
    HealthCheckProtocol='HTTP',
    HealthCheckTimeoutSeconds=5,
    UnhealthyThresholdCount=2,
    TargetType='instance',
    Matcher=elasticloadbalancingv2.Matcher(
        HttpCode='200'
    ),
    HealthyThresholdCount=5,
    VpcId=ImportValue("createvpc-testing-nodesource-vpcid"),
    HealthCheckEnabled=True,
    TargetGroupAttributes=[
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='stickiness.enabled',
            Value='false'
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='deregistration_delay.timeout_seconds',
            Value='300'
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='stickiness.app_cookie.cookie_name',
            Value=''
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='stickiness.type',
            Value='lb_cookie'
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='stickiness.lb_cookie.duration_seconds',
            Value='86400'
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='slow_start.duration_seconds',
            Value='0'
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='stickiness.app_cookie.duration_seconds',
            Value='86400'
        ),
        elasticloadbalancingv2.TargetGroupAttribute(
            Key='load_balancing.algorithm.type',
            Value='round_robin'
        )
    ],
    # Targets=[
    #     elasticloadbalancingv2.TargetDescription(
    #         Id='i-0b38f24219c792d1a',
    #         Port=32768
    #     ),
    #     elasticloadbalancingv2.TargetDescription(
    #         Id='i-0f8c79d3a610a53eb',
    #         Port=32768
    #     ),
    #     elasticloadbalancingv2.TargetDescription(
    #         Id='i-0c0160cb91371f3dd',
    #         Port=32768
    #     )
    # ]
))




### Listener Rules

ElasticLoadBalancingV2Listener = template.add_resource(elasticloadbalancingv2.Listener(
    'ElasticLoadBalancingV2Listener',
    LoadBalancerArn=Ref(ElasticLoadBalancingV2LoadBalancer),
    Port=80,
    Protocol='HTTP',
    DefaultActions=[
        elasticloadbalancingv2.Action(
            Type="forward", 
            TargetGroupArn=Ref(ElasticLoadBalancingV2TargetGroup)),
            # elasticloadbalancingv2.FixedResponseConfig(
            #     {
            #     "MessageBody": "You Are not Authorized to get this path, please validate the instructions. NodeSource.com | Technical test ",
            #     "StatusCode": '503',
            #     "ContentType": 'text/plain'   
            #     }
            # )

    ],
    # DefaultActions=[
    #     elasticloadbalancingv2.Action(
    #         FixedResponseConfig={
    #             "MessageBody": "You Are not Authorized to get this path, please validate the instructions. NodeSource.com | Technical test ",
    #             "StatusCode": '503',
    #             "ContentType": 'text/plain'
    #         },
    #         Order=1,
    #         Type='fixed-response'
    #     )
    # ]
))

ElasticLoadBalancingV2ListenerRule = template.add_resource(elasticloadbalancingv2.ListenerRule(
    'ElasticLoadBalancingV2ListenerRule',
    Priority='1',
    ListenerArn=Ref(ElasticLoadBalancingV2Listener),
    Conditions=[
        elasticloadbalancingv2.Condition(
            Field='path-pattern',
            Values=[
                '/service1'
            ]
        )
    ],
    Actions=[elasticloadbalancingv2.Action(Type="forward", TargetGroupArn=Ref(ElasticLoadBalancingV2TargetGroup))],
    # Actions=[
    #     elasticloadbalancingv2.Action(
    #         Type='forward',
    #         TargetGroupArn=Ref(ElasticLoadBalancingV2TargetGroup),
    #         Order=1,
    #         ForwardConfig={
    #             "TargetGroups": [
    #                 {
    #                     'TargetGroupArn': "${!Ref ElasticLoadBalancingV2TargetGroup}",
    #                     'Weight': 1
    #                 }
    #             ],
    #             "TargetGroupStickinessConfig": {
    #                 'Enabled': False
    #             }
    #         }
    #     )
    # ]
))

ElasticLoadBalancingV2ListenerRule2 = template.add_resource(elasticloadbalancingv2.ListenerRule(
    'ElasticLoadBalancingV2ListenerRule2',
    Priority='2',
    ListenerArn=Ref(ElasticLoadBalancingV2Listener),
    Conditions=[
        elasticloadbalancingv2.Condition(
            Field='path-pattern',
            Values=[
                '/service2'
            ]
        )
    ],
    Actions=[elasticloadbalancingv2.Action(Type="forward", TargetGroupArn=Ref(ElasticLoadBalancingV2TargetGroup))],
    # Actions=[
    #     elasticloadbalancingv2.Action(
    #         Type='forward',
    #         TargetGroupArn=Ref(ElasticLoadBalancingV2TargetGroup),
    #         Order=1,
    #         ForwardConfig={
    #             "TargetGroups": [
    #                 {
    #                     'TargetGroupArn': "${!Ref ElasticLoadBalancingV2TargetGroup}",
    #                     'Weight': 1
    #                 }
    #             ],
    #             "TargetGroupStickinessConfig": {
    #                 'Enabled': False
    #             }
    #         }
    #     )
    # ]
))

####################
# Task Definition
####################

ECSTaskDefinition = template.add_resource(ecs.TaskDefinition(
    'ECSTaskDefinition',
    ContainerDefinitions=[
        ecs.ContainerDefinition(
            Environment=[
                ecs.Environment(
                    Name='NSOLID_APPNAME',
                    Value='nodesource-technical-test'
                ),
                ecs.Environment(
                    Name='NSOLID_COMMAND',
                    Value='console:9001'
                ),
                ecs.Environment(
                    Name='NSOLID_DATA',
                    Value='console:9002'
                ),
                ecs.Environment(
                    Name='NSOLID_BULK',
                    Value='console:9003'
                )
            ],
            Essential=True,
            Image=Ref(ECRurl_param),
            Name='nsolid',
            PortMappings=[
                ecs.PortMapping(
                    ContainerPort=8888,
                    HostPort=0,
                    Protocol='tcp'
                )
            ]
        )
    ],
    Family='nsolid',
    NetworkMode='bridge',
    RequiresCompatibilities=[
        'EC2'
    ],
    Cpu='512',
    Memory='256'
))


####################
# Outputs
####################

LoadBalancerTargetGroupARN_output = template.add_output(
    Output(
        "LoadBalancerTargetGroupARN",
        Description="Target Group ARN",
        Value=Ref(ElasticLoadBalancingV2TargetGroup),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-LoadBalancerTargetGroupARN"))
    )
)


LoadBalancerARN_output = template.add_output(
    Output(
        "LoadBalancerARN",
        Description="LoadBalancer ARN",
        Value=Ref(ElasticLoadBalancingV2LoadBalancer),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-LoadBalancerARN"))
    )
)

TaskDefinitionARN_output = template.add_output(
    Output(
        "TaskDefinitionARN",
        Description="TaskDefinition ARN",
        Value=Ref(ECSTaskDefinition),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-TaskDefinitionARN"))
    )
)



#print(template.to_yaml())
with open('create-taskdef-ALB.yaml', 'w') as f:
    f.write(template.to_yaml())

