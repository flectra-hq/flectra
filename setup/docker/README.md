Continuous Integration and Docker Image Generation
==================================================


Intro
-----

This directory contains all the tools needed for optimized continuous integration testing 
and direct deployment of docker images for development, test and production use.

On every push or merge into core flectra repository some gitlab-ci jobs will be executed
to test the changes and generate new docker images. The details are described in the 
following chapters.  

Goal
----

All code changes should be tested automatically in an acceptable duration and the revision 
should be available with a few steps to run it as a docker container for manual testing. 
 
Docker Image Inheritance
------------------------

There are some base docker images which are used for better performance 
(and less waiting time for developers). Based on that images other images are generated.

The following image are deployed in gitlab registry for flectra: 

| Image        | Tag         | Base Image         | Trigger   | Content 
|--------------|-------------|--------------------|-----------|------------
|  base/ubuntu | latest      | ubuntu:xenial      | scheduler | all required linux and python package to run flectra (ubuntu based) 
|  base/debian | latest      | debian:jessie      | scheduler | all required linux and python package to run flectra (debian based)
|  ubuntu      | **_build_** | base/ubuntu:latest | branch    | full flectra installation and can be used for runbot like testing (ubuntu based)
|  debian      | **_build_** | base/debian:latest | branch    | full flectra installation and can be used for runbot like testing (debian based)
|  ubuntu      | **_tag_**   | base/ubuntu:latest | tag       | full flectra installation for use in production (ubuntu based)
|  debian      | **_tag_**   | base/debian:latest | tag       | full flectra installation for use in production (debian based)

some additional images for testing and building are used as services:

- **postgres:9-alpine**: latest PostgreSQL 9.x image for running tests  
- **postgres:10-alpine**: latest PostgreSQL 10.x image for running tests
- **docker:dind**: Special image containing docker to build and push images  
 
Stages
------

The whole CI and docker process is split in four parts (called stages):

1. unittest: the jobs of this stage will validate the changes 
2. build: at this stage the docker images are generated
3. integrationtest: these jobs will validate the flectra installation of docker images generated in previous stage
4. deploy: these jobs will deploy the docker images with flectra for production use (tagged wit git tag and as latest)   

Only when all jobs of one stage are successful done, the next stage is started.

Jobs
----

### Stage: unittest

The following jobs are started on every push or merge of code:

- **test:pg9_base**: Run test of base module against PostgreSQL 9.x database
- **test:pg9_all**: Run test of all modules against PostgreSQL 9.x database
- **test:pg10_base**: Run test of base module against PostgreSQL 10.x database
- **test:pg9_all**: Run test of all modules against PostgreSQL 10.x database

### Stage: build

The following jobs are only started by gitlab scheduler:

-**build:base_ubuntu**: Build and push base ubuntu image containing all linux and python requirements
-**build:base_debian**: Build and push base debian image containing all linux and python requirements

The following jobs are started on push for a branch:

-**build:flectra_ubuntu**: Build and push image with installed flectra, tagged with commit id (ubuntu based)
-**build:flectra_debian**: Build and push image with installed flectra, tagged with commit id (debian based)

### Stage: integrationtest

The following jobs are started on push for a branch:

- **itest:ubuntu_pg9**: Run test of all modules against PostgreSQL 9.x database with flectra included in docker image (ubuntu based)
- **itest:ubuntu_pg10**: Run test of all modules against PostgreSQL 10.x database with flectra included in docker image (ubuntu based)
- **itest:debian_pg9**: Run test of all modules against PostgreSQL 9.x database with flectra included in docker image (debian based)
- **itest:debian_pg10**: Run test of all modules against PostgreSQL 10.x database with flectra included in docker image (debian based)

### Stage: deploy

The following jobs are started on push for tag:

- **deploy:flectra_ubuntu**: Generate docker image tagged with git tag (=flectra version) and as latest (ubuntu based)
- **deploy:flectra_debian**: Generate docker image tagged with git tag (=flectra version) and as latest (debian based)
