from pathlib import Path
from django.conf import settings
from vmck import vms

mock_vm_sh = (Path(__file__).parent / 'mock_vm.sh').resolve()


class MockBackend:
    def task_group(self):
        vm_port = vms.random_port()

        mock_vm_task = {
            'name': 'vm',
            'driver': 'docker',
            'config': {
                'image': 'mgax/vmck-mock-vm',
                'port_map': [
                    {'ssh': 22},
                ],
            },
            'resources': {
                'networks': [
                    {
                        'ReservedPorts': [
                            {'label': 'ssh', 'value': vm_port},
                        ],
                    },
                ],
            },
        }

        return {
            'Name': 'test',
            'Tasks': [
                mock_vm_task,
                vms.control_task(vm_port),
            ],
            'RestartPolicy': {
                'Attempts': 0,
            },
        }
