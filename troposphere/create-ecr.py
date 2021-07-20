from os import name
from typing import DefaultDict
from troposphere import URLSuffix, ecr
from troposphere import Ref, GetAtt, Template, Parameter, Output, Export, Sub

template = Template()

template.set_version("2010-09-09")
template.set_description(
    "CloudFormation template created from troposphere python library.This stack create a ECR Public Repository")

RepositoryName = template.add_parameter(Parameter(
    "RepositoryName",
    Description="ECR Repository Name",
    Default= "nodesource-test-2",
    Type="String",
))

ECRPublicRepository = template.add_resource(ecr.PublicRepository(
    'ECRPublicRepository',
    RepositoryName=Ref(RepositoryName),
    RepositoryCatalogData={
        "UsageText": '',
        "AboutText": ''
    }
))

####################
# Outputs
####################

ECRname_output = template.add_output(
    Output(
        "ECRname",
        Description="Name of the ECR Repository",
        Value=Ref(ECRPublicRepository),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-ecr-name"))
    )
)

ECRarn_output = template.add_output(
    Output(
        "ECRarn",
        Description="ARN of the ECR Repository",
        Value=GetAtt(ECRPublicRepository, "Arn"),
        Export =  Export(Sub("${AWS::StackName}-" + "nodesource-ecr-arn"))
    )
)


#print(template.to_yaml())
with open('create-ecr.yaml', 'w') as f:
    f.write(template.to_yaml())