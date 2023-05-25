# Collection of HPC container Docker recipes

This repository provides a common framework to build, test and deploy container images at CSCS using Docker. The
repository is organised as a collection of folders. Each folder contains one or more of the Dockerfiles describing
the build process of the containerized application plus optional files needed for testing.

# How it works?
CI/CD middleware at CSCS defines and runs pipelines for each of the applications. Each pipeline consists of three
stages:
```yml
stages:
  - build
  - run
  - deploy
```
and each stage can define multiple jobs that GitLab runner will execute. Please have a look at CI
[template file](ci/common.yml) for the definition of basic templates for each of the stages.

# Writing your ci.yml file
You need to tell GitLab runner how to build and deploy containerized application starting from a Docker recipe.
This is done by providing a `ci.yml` file for your application that defines the logic of buidling, testing and deploying
the container image. The full documentation for GitLab ci.yml keywords is available [here](https://docs.gitlab.com/ee/ci/yaml/).
Let's start with this simple example for `ci.yml`:
```yml
# This is a mandatory statement which enables the definition of common templates.
include:
  - local: '/ci/common.yml'

# Define the name of the job that will be displayed 
build app image:
  extends: .build-image
  variables:
    CSCS_REBUILD_POLICY: always
    DOCKERFILE: SIRIUS/gcc-mkl/Dockerfile
    NAME_TAG: 'sirius-develop'
    DOCKER_BUILD_ARGS: '["CUDA_ARCH=80"]'
```


# Adding new Docker recipes
New recipes are added via a pull request to the `main` branch. Each PR must contain:
 - one or more of the Dockerfiles
 - ci.yml script that drives the CI/CD pipeline
 - `README.md` description file of the container image(s)
