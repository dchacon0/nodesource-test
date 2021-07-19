# nodesource-test


## Build image

```sh
docker network create docker_nsolid
docker build -t nsolid-example .
docker run -d --name nsolid-example -e 'NSOLID_APPNAME=example' -e 'NSOLID_COMMAND=console:9001' -e 'NSOLID_DATA=console:9002' -e 'NSOLID_BULK=console:9003' --network docker_nsolid -p 8888:8888 nsolid-example
```



## Push Image to ECR

Please get the "registry_alias" from ECR registry and replace it in the ECR  URL 

```sh
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

### Authenticat docker to ECR

```sh
registry_alias="m5z1k1h8"
docker tag nsolid-example:latest public.ecr.aws/${registry_alias}/nsolid-test
docker push public.ecr.aws/${registry_alias}/nsolid-test

```






