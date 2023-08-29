import json

import reframe as rfm
import reframe.utility.sanity as sn


class sirius_scf_base_test(rfm.RunOnlyRegressionTest):
    test_folder = parameter(['Si63Ge'])
    container_image = variable(str, value='NULL')
    valid_systems = ['hohgant:gpu']
    valid_prog_environs = ['builtin']
    container_platform = 'Sarus'
    executable = 'sirius.scf'
    executable_opts = ['--output=output.json']
    strict_check = False
    maintainers = ['antonk']
    data_ref = 'output_ref.json'
    fout = 'output.json'
    num_tasks = 4

    @run_after('init')
    def skip_if_null_image(self):
        self.skip_if(self.container_image == 'NULL',
                     'no container image was given')

    @run_after('init')
    def setup_test(self):
        self.descr = 'Sirius SCF check'
        #self.env_vars = {
        #    'MPICH_OFI_STARTUP_CONNECT': 1,
        #    'OMP_PLACES': 'cores',
        #    'OMP_PROC_BIND': 'close'
        #}

        if self.current_system.name in {'hohgant'}:
            self.num_tasks_per_node = 4
            self.num_cpus_per_task = 16
            self.num_tasks_per_core = 1
            self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task)
            }
        self.sourcesdir = './' + self.test_folder

    @run_after('setup')
    def setup_container_platform(self):
        self.container_platform.image = self.container_image
        self.container_platform.with_mpi = False
        command = f'{self.executable} {" ".join(self.executable_opts)}'
        self.container_platform.pull_image = False
        self.container_platform.command = command

    @run_before('run')
    def set_cpu_binding(self):
        self.job.launcher.options = [' --hint=nomultithread']
        if self.current_system.name in {'hohgant'}:
            self.job.launcher.options += ['--mpi=pmi2']

    @run_before('sanity')
    def load_json_data(self):
        with open(self.fout) as f:
            try:
                self.output_data = json.load(f)
            except json.JSONDecodeError as e:
                raise SanityError(
                    f'failed to parse JSON file {self.fout}') from e

        with open(self.data_ref) as f:
            try:
                self.reference_data = json.load(f)
            except json.JSONDecodeError as e:
                raise SanityError(
                    f'failed to parse JSON file {self.data_ref}') from e

    @deferrable
    def energy_diff(self):
        ''' Return the difference between obtained and reference total energies'''
        return sn.abs(self.output_data['ground_state']['energy']['total'] -
                      self.reference_data['ground_state']['energy']['total'])

    @deferrable
    def stress_diff(self):
        ''' Return the difference between obtained and reference stress tensor components'''
        if ('stress' in self.output_data['ground_state'] and
            'stress' in self.reference_data['ground_state']):
            return sn.sum(
                sn.abs(self.output_data['ground_state']['stress'][i][j] -
                       self.reference_data['ground_state']['stress'][i][j])
                for i in [0, 1, 2] for j in [0, 1, 2]
            )
        else:
            return sn.abs(0)

    @deferrable
    def forces_diff(self):
        ''' Return the difference between obtained and reference atomic forces'''
        if ('forces' in self.output_data['ground_state'] and
            'forces' in self.reference_data['ground_state']):
            na = self.output_data['ground_state']['num_atoms']
            return sn.sum(
                sn.abs(self.output_data['ground_state']['forces'][i][j] -
                       self.reference_data['ground_state']['forces'][i][j])
                for i in range(na) for j in [0, 1, 2]
            )
        else:
            return sn.abs(0)

    @sanity_function
    def assert_success(self):
        return sn.all([
            sn.assert_found(r'converged after', self.stdout,
                            msg="Calculation didn't converge"),
            sn.assert_lt(self.energy_diff(), 1e-5,
                         msg="Total energy is different"),
            sn.assert_lt(self.stress_diff(), 1e-5,
                         msg="Stress tensor is different"),
            sn.assert_lt(self.forces_diff(), 1e-5,
                         msg="Atomic forces are different")
        ])


@rfm.simple_test
class sirius_scf_serial(sirius_scf_base_test):
    tags = {'serial'}


#@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
#class sirius_scf_serial(sirius_scf_base_test):
#    def __init__(self, test_folder):
#        super().__init__(1, test_folder)
#        self.tags = {'serial'}
#
#
#@rfm.parameterized_test(*([test_folder] for test_folder in test_folders))
#class sirius_scf_serial_parallel_k(sirius_scf_base_test):
#    def __init__(self, test_folder):
#        super().__init__(4, test_folder)
#        self.tags = {'parallel_k'}


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

