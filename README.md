# Collection of HPC container Docker recipes

This repository provides a common framework to build, test and deploy Docker container images at CSCS. The repository is organised as a collection of folders where each folder contains one or more of the Dockerfiles describing the build process of the containerized application and optional files needed for testing.

# How it works?

![cb](contbuild.svg)

This repository is registered at CSCS CI/CD service and is using build farm infrastructure to run pipelines for any of the applications. For each pipeline three stages are defined:
```yml
stages:
  - build
  - run
  - deploy
```
and each stage can define multiple jobs that GitLab runner will execute. The pipeline is triggered by the pull-request to the `main` branch of repository (1). Then CI/CD middleware triggers the rebuild of all changed Dockerfiles on the build farm (2). In case of success build farm stores the resulting container in the temporaty location inside CSCS container registry (3). After that the optinal `run` stage is executed on the HPC platform to test the container (4) and finally the container is pushed to a persistent location in the container registry. Please have a look at [CI/CD template file](ci/common.yml) for the definition of basic templates for each of the stages.

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
    VERSION_TAG: '1.0'
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

If the build stage is successful, the final image is pushed to  `$CSCS_REGISTRY/contbuild/apps/public/$ARCH/$APP:$VERSION_TAG`. At the moment `CSCS_REGISTRY` variable points to https://jfrog.svc.cscs.ch/artifactory.

Run `sarus pull https://jfrog.svc.cscs.ch/artifactory/contbuild/apps/public/a100/myappname:1.0` from the compute or login node to pull the example image to your local working directory.

# Writing your ci.yml file
We use GitLab runner to defined and execute the logic of the pipelines. The full documentation for GitLab ci.yml keywords is available [here](https://docs.gitlab.com/ee/ci/yaml/). Our [CI/CD template file](ci/common.yml) defines the following templates to build, test and deploy images.

### .build-image
Template for building images.
* stage: build
* variables:
  - DOCKERFILE - name of the Dockerfile
  - DOCKER_BUILD_ARGS - (optional) list of the docker build arguments passed to `docker build` command via `--build-arg` argument

Example:
```yml
build nvhpc cuda qe71 image:
  extends: .build-image
  variables:
    DOCKERFILE: QuantumESPRESSO/nvhpc/cuda/Dockerfile
    DOCKER_BUILD_ARGS: '["CUDA_ARCH=80", "QE_VERSION=qe-7.1"]'
```

### .run-reframe-test
Template for running ReFrame tests.
* stage: run
* variables:
  - REFRAME_COMMAND - full ReFrame command to run a test of containerized application. ReFrame command will be executed from the root folder of the repository (from `./container-recipes`).

Use `-S my_image_name_var="$BASE_IMAGE"` argment of ReFrame to set `my_image_name_var` variable of the test to point to the container URL. Inside Python test the following line will be relevant
```Python
my_image_name_var = variable(str, value='NULL')
```
Example:
```yml
test-image-cpu:
  extends: .run-reframe-test
  variables:
    REFRAME_COMMAND: 'reframe -S container_image="$BASE_IMAGE" -C cscs-reframe-tests/config/cscs.py -c QuantumESPRESSO/rfm_test/qe_check.py --system=hohgant:cpu --skip-performance-check --report-junit=report.xml -r'
```

| :warning:  Waring: this part of documentation is subjected to change|
|---------------------------------------------------------------------|

### .run-test-hohgant-cpu
* Template for running Slurm CPU jobs on TDS cluster  
* stage: run
* variables:
  - USE_MPI: - ('YES'/'NO') use MPI hook to inject Cray's optimised mpich library into container
  - SLURM_JOB_NUM_NODES - number of nodes for the slurm job
  - SLURM_CPUS_PER_TASK - number of CPU cores per MPI rank
  - SLURM_NTASKS - total number of MPI ranks
* script:
  - command1
  - command2
  - ...

Section `script` defines the list of commands that will be executed in a batch submission script. Execution starts from the root folder of the project. Example:
```yaml
run sirius develop hohgant cpu mpi-hook:
 extends: .run-test-hohgant-cpu
  needs: ["build sirius-develop image"]
  variables:
    USE_MPI: 'YES'
    SLURM_JOB_NUM_NODES: 1
    SLURM_CPUS_PER_TASK: 8
    OMP_NUM_THREADS: $SLURM_CPUS_PER_TASK
    SLURM_NTASKS: 16
  script:
    - cd SIRIUS/test/Si63Ge
    - sirius.scf --control.mpi_grid_dims=2:2 --control.std_evp_solver_name=scalapack --control.gen_evp_solver_name=scalapack --test_against=output_ref.json
```

### .run-test-hohgant-gpu
Same as before but for the GPU partition.

### .deploy-image-jfrog
Deploy image at persistent location in container registry.
* stage: deploy
* variables: 
  - APP - name of the application (no capitals and no special symbols)
  - ARCH - container's target architecture (can be one of a00, zen2, zen3)
  - VERSION_TAG: version of the application

Example:
```yaml
deploy qe72 image:
  extends: .deploy-image-jfrog
  variables:
    APP: 'quantumespresso'
    ARCH: 'a100'
    VERSION_TAG: '7.2'
```