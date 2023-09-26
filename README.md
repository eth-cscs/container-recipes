# Collection of HPC container Docker recipes

This repository provides a common framework to build, test and deploy Docker container images at CSCS. The repository is organised as a collection of folders where each folder contains one or more of the Dockerfiles describing the build process of the containerized application and optional files needed for testing.

# How it works?

![cb](contbuild.svg)

This repository is registered at CSCS CI/CD service and is using build farm infrastructure to run pipelines for any of the applications. For each pipeline three stages are defined:
```yml
stages:
  - build
  - test
  - deploy
```
and each stage can define multiple jobs that GitLab runner will execute. The pipeline is triggered by the pull-request to the `main` branch of repository (1). Then CI/CD middleware triggers the rebuild of all changed Dockerfiles on the build farm (2). In case of success build farm stores the resulting container in the temporary location inside CSCS container registry (3). After that the optional `test` stage is executed on the HPC platform to test the container (4) and finally the container is pushed to a persistent location in the container registry. Please have a look at [CI/CD template file](ci/common.yml) for the definition of basic templates for each of the stages.

| :exclamation:  Important: at the moment build farm runs on AMD zen2 architecture |
|-|


# How to add new Dockerfile recipe to the collection?
New recipes are added via pull request to the `main` branch. Each PR must contain:
 - one or more of the Dockerfiles
 - `ci.yml` - script that defines the CI/CD pipeline
 - `README.md` - short description of the application and Dockerfile(s)

The PR will be reviewed and a new pipeline will be added to the project. Minimalistic `ci.yml` should contain the following:
```yml
include:
  - local: '/ci/common.yml'

build my image:
  extends: .build-image
  variables:
    DOCKERFILE: myapp/Dockerfile
    DOCKER_BUILD_ARGS: '["VAR=value"]'

deploy my image:
  extends: .deploy-image-jfrog
  needs: ["build my image"]
  variables:
    APP: 'myappname'
    ARCH: 'a100'
    VERSION: '1.0'
```

with the the following directory structure for `myapp`: 
```
container-recipes/
| ci/
| myapp/
| | Dockerfile
| | ci.yml
| | README.md
```

## Comments
The example pipeline above uses two stages - `build my image` and `deploy my image`. You can avoid deployment stage, but then your container will be stored in a temporary location in CSCS container registry and cleaned up at any time without notice. More information about variables used in each stage is available in the [next section](#writing-your-ciyml-file). 

If the build stage is successful, the final image is pushed to  `$CSCS_REGISTRY/contbuild/apps/public/$ARCH/$APP:$VERSION`. At the moment `CSCS_REGISTRY` variable points to https://jfrog.svc.cscs.ch/artifactory.

Run `sarus pull https://jfrog.svc.cscs.ch/artifactory/contbuild/apps/public/a100/myappname:1.0` from the compute or login node to pull application's image to your local working directory.

# Writing your ci.yml file
We use GitLab runner to define and execute logic of the pipelines. The full documentation for GitLab `ci.yml` keywords is available [here](https://docs.gitlab.com/ee/ci/yaml/). On top of it [CSCS middleware](https://gitlab.com/cscs-ci/ci-testing/containerised_ci_doc) defines several variables to configure slurm and container engine runners. On top of both our [CI/CD template file](ci/common.yml) defines the following templates to build, test and deploy images.

### .build-image
Template for building images. Main variables:
```yaml
stage: build
variables:
  # name of the Dockerfile
  - DOCKERFILE: string
  # (optional) list of arguments passed to `docker build`
  # command via `--build-arg` argument
  - DOCKER_BUILD_ARGS: string of the parameters list, for example '["VAR=value"]'
```
Example:
```yml
build nvhpc cuda qe71 image:
  extends: .build-image
  variables:
    DOCKERFILE: QuantumESPRESSO/nvhpc/cuda/Dockerfile
    DOCKER_BUILD_ARGS: '["CUDA_ARCH=80", "QE_VERSION=qe-7.1"]'
```

### .run-reframe-test-cpu, .run-reframe-test-100
Templates for running ReFrame tests on cpu or a100 architectures. Reframe templates do not take any arguments, however a global variable `REFRAME_ARGS` that defines ReFrame arguments to pass container image name and name of the test must be defined. For example:
```yaml
# global variable definition
variables:
  REFRAME_ARGS: '-S myapp_image="$BASE_IMAGE" -c cscs-reframe-tests/checks/apps/myapp/myapp_check.py'
```

Then the ReFrame test stage is defined simply as:
```yaml
test myapp a100:
  needs: ["build my image"]
  extends: .run-reframe-test-a100
```
ReFrame command will be executed by a gitlab runner from the root folder of the repository (from `./container-recipes`). Inside Python test the following line will be relevant
```Python
myapp_image = variable(str, value='NULL')
```

### .run-test-hohgant-cpu, .run-test-hohgant-a100
Template for running Slurm jobs on a cpu or a100 partition of a TDS cluster. Main variables:  
```yaml
stage: run
variables:
  # ('YES'/'NO') use MPI hook to inject Cray's optimised mpich library into container
  - USE_MPI: string
  # number of nodes for the slurm job (-N argument of srun)
  - SLURM_JOB_NUM_NODES: integer
  # number of CPU cores per MPI rank (-c argument of srun)
  - SLURM_CPUS_PER_TASK: integer
  # total number of MPI ranks (-b argument of srun)
  - SLURM_NTASKS: integer
# a set of commands that will be executed inside sbatch submission script
script:
  - command1
  - command2
  - ...
```
Execution starts from the root folder of the project. Example:
```yaml
run myapp cpu:
  extends: .run-test-hohgant-cpu
  needs: ["build myapp"]
  variables:
    USE_MPI: 'YES'
    SLURM_JOB_NUM_NODES: 1
    SLURM_CPUS_PER_TASK: 8
    OMP_NUM_THREADS: $SLURM_CPUS_PER_TASK
    SLURM_NTASKS: 16
  script:
    - cd myapp/test
    # run myapp inside container on 16 MPI ranks with 8 threads/rank
    - /path/to/myapp [optional arguments]
```

### .deploy-image-jfrog
Deploy image at persistent location in container registry. Main variables:
```yaml
stage: deploy
variables: 
  # name of the application (no capitals and no special symbols)
  - APP: string
  # container's target architecture (can be one of a100, zen2, zen3)
  - ARCH: string
  # version of the application
  - VERSION: string
```
Example:
```yaml
deploy myapp:
  extends: .deploy-image-jfrog
  variables:
    APP: 'myapp'
    ARCH: 'a100'
    VERSION: '1.0'
```