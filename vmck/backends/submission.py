from django.conf import settings

manager_script = ''' \
#!/bin/bash -ex
trap "vagrant destroy -f" EXIT
curl -X GET ${DOWNLOAD_ARCHIVE_URL} > submission.zip
curl -X GET ${DOWNLOAD_SCRIPT_URL} > checker.sh
vagrant up
vagrant ssh -- < checker.sh > result.out
data="$(base64 result.out)"
echo "{\\"token\\": \\"${SUBMISSION_ID}\\",\
       \\"output\\": \\"${data}\\"}" > data.json
curl -X POST "http://${INTERFACE_ADDRESS}/done/" -d @data.json \
     --header "Content-Type: application/json"
'''

vagrantfile = ''' \
Vagrant.configure("2") do |config|
    config.vm.box = 'base'

    if Vagrant.has_plugin?('vagrant-env')
        config.env.enable
    end

    config.nfs.functional = false
    config.vm.provision 'shell', inline: 'mv /vagrant/submission.zip .; \
                                            unzip submission.zip; \
                                            chown -R vagrant:vagrant .'
    config.vm.provider :vmck do |vmck|
        vmck.vmck_url = ENV['VMCK_URL']
    end
end
'''


def task(job, options):
    return {
        'name': 'submission-handler',
        'driver': 'docker',
        'config': {
            'image': 'vmck/vagrant-vmck:submission',
            'volumes': [
                "local/submission.sh:/src/submission.sh",
                "local/Vagrantfile:/src/Vagrantfile",
            ],
            'command': '/bin/bash',
            'args': ['/src/submission.sh'],
            'force_pull': True,
        },
        'env': {
            'DOWNLOAD_ARCHIVE_URL': options['env']['archive'],
            'DOWNLOAD_SCRIPT_URL': options['env']['script'],
            'VMCK_URL': settings.VMCK_URL,
            'INTERFACE_ADDRESS': options['env']['interface_address'],
            'VMCK_JOB_ID': str(job.id),
            'SUBMISSION_ID': options['env']['id']
        },
        'templates': [
            {
                "DestPath": "local/submission.sh",
                "EmbeddedTmpl": manager_script,
            },
            {
                "DestPath": "local/Vagrantfile",
                "EmbeddedTmpl": vagrantfile,
            },
        ],
        'resources': {
            'MemoryMB': options['env']['memory'],
            'CPU': options['env']['cpu_mhz'],
        },
    }
