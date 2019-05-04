def ssh_args(remote, args):
    yield 'ssh'

    vars = {
        'Port': str(remote['port']),
        'User': remote['username'],
        'UserKnownHostsFile': '/dev/null',
        'StrictHostKeyChecking': 'no',
        'PasswordAuthentication': 'no',
        'IdentityFile': remote['identity_file'],
        'IdentitiesOnly': 'yes',
        'LogLevel': 'FATAL',
    }

    for name, value in vars.items():
        yield from ('-o', f'{name}={value}')

    yield remote['host']
    yield '--'
    yield from args
