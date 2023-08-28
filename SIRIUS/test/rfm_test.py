#import itertools
#import os
#import json

import reframe as rfm
import reframe.utility.sanity as sn

test_folders = ['Si63Ge']

@sanity_function
def load_json(filename):
    '''This will load a json data from a file.'''
    raw_data = sn.extractsingle(r'(?s).+', filename).evaluate()
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError as e:
        raise SanityError('failed to parse JSON file') from e

@sanity_function
def energy_diff(filename, data_ref):
    ''' Return the difference between obtained and reference total energies'''
    parsed_output = load_json(filename)
    return sn.abs(parsed_output['ground_state']['energy']['total'] -
                       data_ref['ground_state']['energy']['total'])

@sanity_function
def stress_diff(filename, data_ref):
    ''' Return the difference between obtained and reference stress tensor components'''
    parsed_output = load_json(filename)
    if 'stress' in parsed_output['ground_state'] and 'stress' in data_ref['ground_state']:
        return sn.sum(sn.abs(parsed_output['ground_state']['stress'][i][j] -
                             data_ref['ground_state']['stress'][i][j]) for i in [0, 1, 2] for j in [0, 1, 2])
    else:
        return sn.abs(0)

@sanity_function
def forces_diff(filename, data_ref):
    ''' Return the difference between obtained and reference atomic forces'''
    parsed_output = load_json(filename)
    if 'forces' in parsed_output['ground_state'] and 'forces' in data_ref['ground_state']:
        na = parsed_output['ground_state']['num_atoms'].evaluate()
        return sn.sum(sn.abs(parsed_output['ground_state']['forces'][i][j] -
                             data_ref['ground_state']['forces'][i][j]) for i in range(na) for j in [0, 1, 2])
    else:
        return sn.abs(0)

@rfm.simple_test
class sirius_scf_base_test(rfm.RunOnlyRegressionTest):
    valid_systems = ['hohgant:gpu']
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    container_image = variable(str, value='NULL')
    executable = 'sirius.scf'
    executable_opts = ['--output=output.json']
    strict_check = False
    maintainers = ['antonk']

    def __init__(self, num_ranks, test_folder):
        super().__init__()

        self.num_tasks = num_ranks

        self.sourcesdir = './' + test_folder

        data_ref = load_json('output_ref.json')

        fout = 'output.json'

        self.sanity_patterns = sn.all([
            sn.assert_found(r'converged after', self.stdout, msg="Calculation didn't converge"),
            sn.assert_lt(energy_diff(fout, data_ref), 1e-5, msg="Total energy is different"),
            #sn.assert_lt(stress_diff(fout, data_ref), 1e-5, msg="Stress tensor is different"),
            #sn.assert_lt(forces_diff(fout, data_ref), 1e-5, msg="Atomic forces are different")
        ])

    @run_after('init')
    def skip_if_null_image(self):
        self.skip_if(self.container_image == 'NULL', 'no container image was given')

    @run_after('init')
    def setup_test(self):
        self.descr = 'Sirius SCF check'
        #self.env_vars = {
        #    'MPICH_OFI_STARTUP_CONNECT': 1,
        #    'OMP_NUM_THREADS': 4,
        #    'OMP_PLACES': 'cores',
        #    'OMP_PROC_BIND': 'close'
        #}

        if self.current_system.name in {'hohgant'}:
            self.num_tasks_per_node = 4
            self.num_cpus_per_task = 16
            self.num_tasks_per_core = 1
            self.variables = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task)
            }

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.container_image
        self.container_platform.with_mpi = False
        command = f'{self.executable} {" ".join(self.executable_opts)}'
        self.container_platform.pull_image = False
        self.container_platform.command = command

    @run_before('run')
    def set_cpu_binding(self):
         #self.job.launcher.options = ['--cpu-bind=cores', ' --hint=nomultithread']
         #
        self.job.launcher.options = [' --hint=nomultithread']
        if self.current_system.name in {'hohgant'}:
            self.job.launcher.options += ['--mpi=pmi2']

#@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
#class sirius_scf_serial(sirius_scf_base_test):
#    def __init__(self, test_folder):
#        super().__init__(1, test_folder)
#        self.tags = {'serial'}
#
#
@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
class sirius_scf_serial_parallel_k(sirius_scf_base_test):
    def __init__(self, test_folder):
        super().__init__(4, test_folder)
        self.tags = {'parallel_k'}


#@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
#class sirius_scf_serial_parallel_band_22(sirius_scf_base_test):
#    def __init__(self, test_folder):
#        super().__init__(4, test_folder)
#        self.tags = {'parallel_band'}
#        self.executable_opts.append('--mpi_grid=2:2')
#
#
#@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
#class sirius_scf_serial_parallel_band_12(sirius_scf_base_test):
#    def __init__(self, test_folder):
#        super().__init__(2, test_folder)
#        self.tags = {'parallel_band'}
#        self.executable_opts.append('--mpi_grid=1:2')
#
#
#@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
#class sirius_scf_serial_parallel_band_21(sirius_scf_base_test):
#    def __init__(self, test_folder):
#        super().__init__(2, test_folder)
#        self.tags = {'parallel_band'}
#        self.executable_opts.append('--mpi_grid=2:1')

