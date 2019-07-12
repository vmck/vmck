job "vmck" {
  datacenters = ["dc1"]
  type = "service"

  group "imghost" {
    task "nginx" {
      driver = "docker"
      config {
        image = "nginx:mainline"
        volumes = [
          "/usr/share/vmck-images:/usr/share/nginx/html",
          "local/nginx.conf:/etc/nginx/nginx.conf",
        ]
        port_map {
          http = 80
        }
      }
      resources {
        memory = 80
        cpu = 200
        network {
          port "http" {
            static = 7000
          }
        }
      }
      template {
        data = <<-EOF
          user  nginx;
          worker_processes auto;

          error_log  /var/log/nginx/error.log warn;
          pid        /var/run/nginx.pid;

          events {
            worker_connections 1024;
          }

          http {
            include       /etc/nginx/mime.types;
            default_type  application/octet-stream;

            sendfile on;
            sendfile_max_chunk 4m;
            aio threads;
            keepalive_timeout 65;
            server {
              listen 80;
              server_name  _;
              error_log /dev/stderr info;
              location / {
                root   /usr/share/nginx/html;
                autoindex on;
                proxy_max_temp_file_size 0;
                proxy_buffering off;
              }
              location = /healthcheck {
                stub_status;
              }
            }
          }
        EOF
        destination = "local/nginx.conf"
      }
      service {
        name = "vmck-imghost"
        port = "http"
        check {
          name = "vmck-imghost nginx alive on http"
          initial_status = "critical"
          type = "http"
          path = "/healthcheck"
          interval = "5s"
          timeout = "5s"
        }
      }
    }
  }

  group "vmck" {
    task "vmck" {
      driver = "docker"
      config {
        image = "vmck/vmck"
        volumes = [
          "/opt/vmck/data:/opt/vmck/data",
        ]
        port_map {
          http = 8000
        }
        labels {
          liquid_task = "vmck"
        }
      }
      template {
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
        # TODO: the QEMU_IMAGE_URL has a very sinister form. Please refer to the
        #       following link: https://github.com/vmck/image-builder#building-different-flavors-of-images
        #       That link will explain why the image is named as it is now and how to make your own
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
          interval = "5s"
          timeout = "5s"
        }
      }
    }
  }
}
