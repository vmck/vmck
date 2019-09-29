# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "base"

  if Vagrant.has_plugin?('vagrant-env')
    config.env.enable
  end

  config.nfs.functional = false

  config.vm.synced_folder ".", "/opt/vmck", type: "rsync",
      rsync__exclude: [".git/", "data/", "vmck.egg-info/", ".pytest_cache"]

  if ENV['SHUTDOWN']
    config.vm.provision 'shell', inline: "sudo shutdown #{ENV['SHUTDOWN']}"
  end

  config.vm.provision 'shell', path: "ci/wait-cluster.sh"

  config.vm.provider :vmck do |vmck|
    vmck.image_path = 'cluster-master.qcow2.tar.gz'
    vmck.vmck_url = ENV['VMCK_URL']
    vmck.memory = 1024 * 4
    vmck.name = ENV['VMCK_NAME']
    vmck.cpus = 2
  end
end
