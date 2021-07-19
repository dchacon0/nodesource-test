from troposphere import ec2, ecs, ecr, elasticloadbalancingv2
from troposphere import Ref, GetAtt, Template

template = Template()

template.add_version("2010-09-09")

EC2VPC = template.add_resource(ec2.VPC(
    'EC2VPC',
    CidrBlock='192.168.20.0/24',
    EnableDnsSupport=True,
    EnableDnsHostnames=True,
    InstanceTenancy='default',
    Tags=[
        {
            "Key": 'aws:cloudformation:logical-id',
            "Value": 'Vpc'
        },
        {
            "Key": 'aws:cloudformation:stack-name',
            "Value": 'EC2ContainerService-nsolid-cluster'
        },
        {
            "Key": 'aws:cloudformation:stack-id',
            "Value": 'arn:aws:cloudformation:us-east-1:698090330670:stack/EC2ContainerService-nsolid-cluster/1143d690-e823-11eb-9b62-0ab0f473fdd5'
        }
    ]
))

EC2SecurityGroup = template.add_resource(ec2.SecurityGroup(
    'EC2SecurityGroup',
    GroupDescription='ECS Allowed Ports',
    GroupName='EC2ContainerService-nsolid-cluster-EcsSecurityGroup-27ZAOBH1Z7JP',
    Tags=[
        {
            "Key": 'aws:cloudformation:stack-name',
            "Value": 'EC2ContainerService-nsolid-cluster'
        },
        {
            "Key": 'aws:cloudformation:stack-id',
            "Value": 'arn:aws:cloudformation:us-east-1:698090330670:stack/EC2ContainerService-nsolid-cluster/1143d690-e823-11eb-9b62-0ab0f473fdd5'
        },
        {
            "Key": 'aws:cloudformation:logical-id',
            "Value": 'EcsSecurityGroup'
        }
    ],
    VpcId=Ref(EC2VPC),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            FromPort=80,
            IpProtocol='tcp',
            ToPort=80
        ),
        ec2.SecurityGroupRule(
            SourceSecurityGroupId=Ref(EC2SecurityGroup2),
            SourceSecurityGroupOwnerId='698090330670',
            Description='LoadBalancer',
            IpProtocol='-1'
        ),
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            Description='temp',
            FromPort=32768,
            IpProtocol='tcp',
            ToPort=32768
        )
    ],
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            IpProtocol='-1'
        )
    ]
))

EC2SecurityGroup2 = template.add_resource(ec2.SecurityGroup(
    'EC2SecurityGroup2',
    GroupDescription=GetAtt(ElasticLoadBalancingV2LoadBalancer, 'LoadBalancerName'),
    GroupName=GetAtt(ElasticLoadBalancingV2LoadBalancer, 'LoadBalancerName'),
    VpcId=Ref(EC2VPC),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            CidrIp='0.0.0.0/0',
            FromPort=80,
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

EC2Subnet = template.add_resource(ec2.Subnet(
    'EC2Subnet',
    AvailabilityZone='us-east-1a',
    CidrBlock='192.168.20.0/26',
    VpcId=Ref(EC2VPC),
    MapPublicIpOnLaunch=True
))

EC2Subnet2 = template.add_resource(ec2.Subnet(
    'EC2Subnet2',
    AvailabilityZone=GetAtt(EC2Instance2, 'AvailabilityZone'),
    CidrBlock='192.168.20.128/26',
    VpcId=Ref(EC2VPC),
    MapPublicIpOnLaunch=True
))

EC2Subnet3 = template.add_resource(ec2.Subnet(
    'EC2Subnet3',
    AvailabilityZone=GetAtt(EC2Instance, 'AvailabilityZone'),
    CidrBlock='192.168.20.64/26',
    VpcId=Ref(EC2VPC),
    MapPublicIpOnLaunch=True
))

ECSCluster = template.add_resource(ecs.Cluster(
    'ECSCluster',
    ClusterName='nsolid-cluster',
    ClusterSettings=[
        {
            "Name": 'containerInsights',
            "Value": 'disabled'
        }
    ]
))

ECSService = template.add_resource(ecs.Service(
    'ECSService',
    ServiceName='nsolid-service',
    Cluster=GetAtt(ECSCluster, 'Arn'),
    LoadBalancers=[
        ecs.LoadBalancer(
            TargetGroupArn='arn:aws:elasticloadbalancing:us-east-1:698090330670:targetgroup/nsolid-loadbalancer-targetgroup/3eec76aa46b2ea50',
            ContainerName='nsolid',
            ContainerPort=8888
        )
    ],
    DesiredCount=2,
    LaunchType='EC2',
    TaskDefinition='arn:aws:ecs:us-east-1:698090330670:task-definition/nsolid:1',
    DeploymentConfiguration=ecs.DeploymentConfiguration(
        MaximumPercent=200,
        MinimumHealthyPercent=100,
        DeploymentCircuitBreaker={
            "Enable": False,
            "Rollback": False
        }
    ),
    Role='arn:aws:iam::698090330670:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS',
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

EC2Instance = template.add_resource(ec2.Instance(
    'EC2Instance',
    ImageId='ami-091aa67fccd794d5f',
    InstanceType='t3.medium',
    KeyName='nsolid-lab',
    AvailabilityZone='us-east-1b',
    Tenancy='default',
    SubnetId='subnet-03f8dd86588800f7f',
    EbsOptimized=False,
    SecurityGroupIds=[
        Ref(EC2SecurityGroup)
    ],
    SourceDestCheck=True,
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName='/dev/xvda',
            Ebs=ec2.EBSBlockDevice(
                Encrypted=False,
                VolumeSize=30,
                SnapshotId='snap-0868b2fb07685ff38',
                VolumeType='gp2',
                DeleteOnTermination=True
            )
        )
    ],
    UserData='IyEvYmluL2Jhc2gKZWNobyBFQ1NfQ0xVU1RFUj1uc29saWQtY2x1c3RlciA+PiAvZXRjL2Vjcy9lY3MuY29uZmlnO2VjaG8gRUNTX0JBQ0tFTkRfSE9TVD0gPj4gL2V0Yy9lY3MvZWNzLmNvbmZpZzs=',
    IamInstanceProfile='containerInstanceECSRole-nsolid-lab',
    Monitoring=True,
    Tags=[
        {
            "Key": 'aws:cloudformation:stack-id',
            "Value": 'arn:aws:cloudformation:us-east-1:698090330670:stack/EC2ContainerService-nsolid-cluster/1143d690-e823-11eb-9b62-0ab0f473fdd5'
        },
        {
            "Key": 'aws:autoscaling:groupName',
            "Value": 'EC2ContainerService-nsolid-cluster-EcsInstanceAsg-1GGLMOL1TTHWI'
        },
        {
            "Key": 'Name',
            "Value": 'ECS Instance - EC2ContainerService-nsolid-cluster'
        },
        {
            "Key": 'aws:cloudformation:stack-name',
            "Value": 'EC2ContainerService-nsolid-cluster'
        },
        {
            "Key": 'aws:cloudformation:logical-id',
            "Value": 'EcsInstanceAsg'
        },
        {
            "Key": 'Description',
            "Value": 'This instance is the part of the Auto Scaling group which was created through ECS Console'
        }
    ],
    HibernationOptions={
        "Configured": False
    },
    CpuOptions={
        "CoreCount": 1,
        "ThreadsPerCore": 2
    },
    EnclaveOptions={
        "Enabled": False
    }
))

EC2Instance2 = template.add_resource(ec2.Instance(
    'EC2Instance2',
    ImageId='ami-091aa67fccd794d5f',
    InstanceType='t3.medium',
    KeyName='nsolid-lab',
    AvailabilityZone='us-east-1c',
    Tenancy='default',
    SubnetId='subnet-0a96b22438746f5c1',
    EbsOptimized=False,
    SecurityGroupIds=[
        Ref(EC2SecurityGroup)
    ],
    SourceDestCheck=True,
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName='/dev/xvda',
            Ebs=ec2.EBSBlockDevice(
                Encrypted=False,
                VolumeSize=30,
                SnapshotId='snap-0868b2fb07685ff38',
                VolumeType='gp2',
                DeleteOnTermination=True
            )
        )
    ],
    UserData='IyEvYmluL2Jhc2gKZWNobyBFQ1NfQ0xVU1RFUj1uc29saWQtY2x1c3RlciA+PiAvZXRjL2Vjcy9lY3MuY29uZmlnO2VjaG8gRUNTX0JBQ0tFTkRfSE9TVD0gPj4gL2V0Yy9lY3MvZWNzLmNvbmZpZzs=',
    IamInstanceProfile='containerInstanceECSRole-nsolid-lab',
    Monitoring=True,
    Tags=[
        {
            "Key": 'Description',
            "Value": 'This instance is the part of the Auto Scaling group which was created through ECS Console'
        },
        {
            "Key": 'aws:cloudformation:logical-id',
            "Value": 'EcsInstanceAsg'
        },
        {
            "Key": 'aws:autoscaling:groupName',
            "Value": 'EC2ContainerService-nsolid-cluster-EcsInstanceAsg-1GGLMOL1TTHWI'
        },
        {
            "Key": 'aws:cloudformation:stack-id',
            "Value": 'arn:aws:cloudformation:us-east-1:698090330670:stack/EC2ContainerService-nsolid-cluster/1143d690-e823-11eb-9b62-0ab0f473fdd5'
        },
        {
            "Key": 'aws:cloudformation:stack-name',
            "Value": 'EC2ContainerService-nsolid-cluster'
        },
        {
            "Key": 'Name',
            "Value": 'ECS Instance - EC2ContainerService-nsolid-cluster'
        }
    ],
    HibernationOptions={
        "Configured": False
    },
    CpuOptions={
        "CoreCount": 1,
        "ThreadsPerCore": 2
    },
    EnclaveOptions={
        "Enabled": False
    }
))

EC2VolumeAttachment = template.add_resource(ec2.VolumeAttachment(
    'EC2VolumeAttachment',
    VolumeId='vol-0ee2e697d564a8e9f',
    InstanceId=Ref(EC2Instance2),
    Device='/dev/xvda'
))

EC2VolumeAttachment2 = template.add_resource(ec2.VolumeAttachment(
    'EC2VolumeAttachment2',
    VolumeId='vol-0aa020fd0393827c9',
    InstanceId=Ref(EC2Instance),
    Device='/dev/xvda'
))

EC2NetworkInterfaceAttachment = template.add_resource(ec2.NetworkInterfaceAttachment(
    'EC2NetworkInterfaceAttachment',
    NetworkInterfaceId='eni-031d1f7a162fc7540',
    DeviceIndex=0,
    InstanceId=Ref(EC2Instance2),
    DeleteOnTermination=True
))

EC2NetworkInterfaceAttachment2 = template.add_resource(ec2.NetworkInterfaceAttachment(
    'EC2NetworkInterfaceAttachment2',
    NetworkInterfaceId='eni-08d25e339d759e4d1',
    DeviceIndex=0,
    InstanceId=Ref(EC2Instance),
    DeleteOnTermination=True
))

ECRRepository = template.add_resource(ecr.Repository(
    'ECRRepository',
    RepositoryName='nsolid-test',
    LifecyclePolicy=ecr.LifecyclePolicy(
        RegistryId='698090330670'
    )
))

ECRPublicRepository = template.add_resource(ecr.PublicRepository(
    'ECRPublicRepository',
    RepositoryName='nsolid-test',
    RepositoryCatalogData={
        "UsageText": '',
        "AboutText": ''
    }
))

ElasticLoadBalancingV2LoadBalancer = template.add_resource(elasticloadbalancingv2.LoadBalancer(
    'ElasticLoadBalancingV2LoadBalancer',
    Name='nsolid-loadbalancer',
    Scheme='internet-facing',
    Type='application',
    Subnets=[
        'subnet-03f8dd86588800f7f',
        'subnet-0a96b22438746f5c1',
        Ref(EC2Subnet)
    ],
    SecurityGroups=[
        'sg-082170e712cbc4a2a'
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
        )
    ]
))

ElasticLoadBalancingV2Listener = template.add_resource(elasticloadbalancingv2.Listener(
    'ElasticLoadBalancingV2Listener',
    LoadBalancerArn=Ref(ElasticLoadBalancingV2LoadBalancer),
    Port=80,
    Protocol='HTTP',
    DefaultActions=[
        elasticloadbalancingv2.Action(
            FixedResponseConfig={
                "MessageBody": 'Your are not authorized to get this URI',
                "StatusCode": '503',
                "ContentType": 'text/plain'
            },
            Order=1,
            Type='fixed-response'
        )
    ]
))

EC2NetworkInterface = template.add_resource(ec2.NetworkInterface(
    'EC2NetworkInterface',
    Description='ELB app/nsolid-loadbalancer/82992b6c9bcec39a',
    PrivateIpAddress='192.168.20.134',
    PrivateIpAddresses=[
        ec2.PrivateIpAddressSpecification(
            PrivateIpAddress='192.168.20.134',
            Primary=True
        )
    ],
    SubnetId=Ref(EC2Subnet2),
    SourceDestCheck=True,
    GroupSet=[
        Ref(EC2SecurityGroup2)
    ]
))

EC2NetworkInterface2 = template.add_resource(ec2.NetworkInterface(
    'EC2NetworkInterface2',
    Description='ELB app/nsolid-loadbalancer/82992b6c9bcec39a',
    PrivateIpAddress='192.168.20.92',
    PrivateIpAddresses=[
        ec2.PrivateIpAddressSpecification(
            PrivateIpAddress='192.168.20.92',
            Primary=True
        )
    ],
    SubnetId=Ref(EC2Subnet3),
    SourceDestCheck=True,
    GroupSet=[
        Ref(EC2SecurityGroup2)
    ]
))

EC2NetworkInterface3 = template.add_resource(ec2.NetworkInterface(
    'EC2NetworkInterface3',
    Description='ELB app/nsolid-loadbalancer/82992b6c9bcec39a',
    PrivateIpAddress='192.168.20.9',
    PrivateIpAddresses=[
        ec2.PrivateIpAddressSpecification(
            PrivateIpAddress='192.168.20.9',
            Primary=True
        )
    ],
    SubnetId=Ref(EC2Subnet),
    SourceDestCheck=True,
    GroupSet=[
        Ref(EC2SecurityGroup2)
    ]
))

EC2NetworkInterface4 = template.add_resource(ec2.NetworkInterface(
    'EC2NetworkInterface4',
    Description='ELB app/nsolid-loadbalancer/82992b6c9bcec39a',
    PrivateIpAddress='192.168.20.47',
    PrivateIpAddresses=[
        ec2.PrivateIpAddressSpecification(
            PrivateIpAddress='192.168.20.47',
            Primary=True
        )
    ],
    SubnetId=Ref(EC2Subnet),
    SourceDestCheck=True,
    GroupSet=[
        Ref(EC2SecurityGroup2)
    ]
))

print(template.to_yaml())
