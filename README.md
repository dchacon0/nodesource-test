# nodesource technical test

This repo has all the scrips required to acomplish the following task:

    1. Create a troposphere (https://github.com/cloudtools/troposphere) script to launch an
    ECS cluster, Application Load Balancer and an Auto Scaling Group that serve two
    random Node.js (You may use N|Solid images) microservices which images are pulled
    from ECR. Listeners should route traffic from the /service1 and /service2 URLs to
    the defined container ports. It is a plus if you add an Ansible playbook that is in charge of
    controlling the version of the ECS agent installed on the server.


## Build Docker Image 

```sh
docker network create docker_nsolid
docker build -t nsolid-example .
docker run -d --name nsolid-example -e 'NSOLID_APPNAME=example' -e 'NSOLID_COMMAND=console:9001' -e 'NSOLID_DATA=console:9002' -e 'NSOLID_BULK=console:9003' --network docker_nsolid -p 8888:8888 nsolid-example
```

## ECR
Keep in mind that the ECR is created using troposphere, so once it gets created you can validate the output of the cloud formation stack.

### Authenticat docker to ECR
```sh
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```
### Push Docker image to ECR
Please get the "registry_alias" from ECR registry and replace it in the ECR  URL 
```sh
registry_alias="m5z1k1h8"
docker tag nsolid-example:latest public.ecr.aws/${registry_alias}/nsolid-test
docker push public.ecr.aws/${registry_alias}/nsolid-test

```






