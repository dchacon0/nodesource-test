# About this repository
This repo has all the scrips required to acomplish the following task:

Create a troposphere (https://github.com/cloudtoolstroposphere) script to launch an
ECS cluster, Application Load Balancer and an Auto ScalingGroup that serve two
random Node.js (You may use N|Solid images) microserviceswhich images are pulled
from ECR. Listeners should route traffic from the /service1 and /service2 URLs to
the defined container ports. It is a plus if you add anAnsible playbook that is in charge of
controlling the version of the ECS agent installed on theserver.

## How to use this repo
> Keep in mind that the ECR is created using troposphere, so once it gets created you can validate the output of the cloud formation stack.
> Remember you have to set AWS enviroment variables with the proper authentication values in order to execute the AWSCLi commands

1. **Prepare the Docker image**
    ```sh
    docker build -t nsolid-example .
    ```
2. **Create the ECR Repository**
    ```sh
    python3 create-ecr.py # troposphere script that create cloudformation file with name "create-ecr.yaml"
    aws --region us-east-1  cloudformation create-stack --stack-name \
    create-ecr-nodesource \
    --parameters ParameterKey=RepositoryName,ParameterValue=nsolid-test \
    --template-body file://create-ecr.yaml # Remember you should have configured the AWSCLI authentication 
    ```
3. **Push the Docker Image to ECR**

    *Validate that the container is properly working*  **(Optional)***
    ```sh
    docker network create docker_nsolid
    docker build -t nsolid-example .
    docker run -d --name nsolid-example -e 'NSOLID_APPNAME=example' -e 'NSOLID_COMMAND=console:9001' -e 'NSOLID_DATA=console:9002' -e 'NSOLID_BULK=console:9003' --network docker_nsolid -p 8888:8888 nsolid-example
    ```
    *Authenticate docker with AWS ECR*
    ```sh
    aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
    ```
    *Push Docker image to ECR*
    Please get the "registry_alias" from ECR registry and replace it in the ECR  URL 
    ```sh
    registry_alias=$(aws ecr-public  describe-registries  --region us-east-1 --query 'registries[*].aliases[*].name' --output text)
    docker tag nsolid-example:latest public.ecr.aws/${registry_alias}nsolid-test/
    docker push public.ecr.aws/${registry_alias}/nsolid-test
    ```

4. **Its time to create all the other infraestrucuture**

    *Creating VPC Networks and Security Groups*
    ```sh
    python3 create-network.py
    aws --region us-east-1  cloudformation \
    create-stack --stack-name create-network \
    --parameters ParameterKey=ProjectName,ParameterValue=nodesource-test \
    --template-body file://create-network.yaml
    ```
    *Creating AutoScaling Group, ECS Instances (EC2) and ECS Cluster*
    ```sh
    python3 create-ECS-ASG-EC2.py
    aws --region us-east-1  cloudformation create-stack --stack-name create-ECS-ASG.EC2 --template-body file://create-ECS-ASG-EC2.yaml --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
    ```
    *Creating ECS Task Definition and ALB (Aplication Load Balancer)*
    ```sh
    python3 create-taskdef-ALB.py
    aws --region us-east-1  cloudformation create-stack --stack-name create-taskdef-ALB --template-body file://create-taskdef-ALB.yaml --parameters ParameterKey=ECRurl,ParameterValue=public.ecr.aws/${registry_alias}/nsolid-test
    ```
    *Creating ECS Service*
    ```sh
    python3 create-ECSservice.py
    aws --region us-east-1  cloudformation create-stack --stack-name create-ECSservice --template-body file://create-ECSservice.yaml
    ```




