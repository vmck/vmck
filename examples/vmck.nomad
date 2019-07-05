# TODO: remove hardcoded values
#       add configurationa like in https://github.com/liquidinvestigations/node/blob/master/templates/drone.nomad
job "vmck" {
  datacenters = ["dc1"]
  type = "service"

  group "vmck" {
    task "vmck" {
      driver = "docker"
      config {
        image = "vmck/vmck"
        volumes = [
          "/opt/vmck/data:/opt/vmck/data", # TODO: add setting for host volume
        ]
        port_map {
          http = 8000
        }
        labels {
          liquid_task = "vmck"
        }
      }
      template {
	      # TODO: add setting for CONSUL_URL and NOMAD_URL
        data = <<-EOF
        SECRET_KEY = "TODO:ChangeME!!!"
        HOSTNAME = "*"
        SSH_USERNAME = "vagrant"
        CONSUL_URL = "10.66.60.1:8500"
        NOMAD_URL = "10.66.60.1:4646"
        BACKEND = "qemu"
        QEMU_CPU_MHZ = 3000
        EOF
        destination = "local/vmck.env"
        env = true
      }
      template {
        data = <<-EOF
        {{- range service "vmck-imghost" -}}
          QEMU_IMAGE_URL = "http://{{.Address}}:{{.Port}}/cluster-master.qcow2.tar.gz"
        {{- end }}
        EOF
        destination = "local/vmck-imghost.env"
        env = true
      }
      resources {
        memory = 450
        cpu = 350
        network {
          port "http" {
            static = 9995
          }
        }
      }
      service {
        name = "vmck"
        port = "http"
        check {
          name = "vmck alive on http"
          initial_status = "critical"
          type = "http"
          path = "/v0/"
	        # TODO: add setting for interval and timeout
	        interval = "5s"
          timeout = "5s"
        }
      }
    }
  }
}
