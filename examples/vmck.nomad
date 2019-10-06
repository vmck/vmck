job "vmck" {
  datacenters = ["dc1"]
  type = "service"

  group "imghost" {
    task "nginx" {
      constraint {
        attribute = "${meta.volumes}"
        operator  = "is_set"
      }
      driver = "docker"
      config {
        image = "nginx:mainline"
        volumes = [
          "${meta.volumes}/vmck-images:/usr/share/nginx/html",
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
            static = 10001
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
      constraint {
        attribute = "${meta.volumes}"
        operator  = "is_set"
      }
      driver = "docker"
      config {
        image = "vmck/vmck:0.4.4"
        hostname = "${attr.unique.hostname}"
        dns_servers = ["${attr.unique.network.ip-address}"]
        volumes = [
          "${meta.volumes}/vmck:/opt/vmck/data",
        ]
        port_map {
          http = 8000
        }
      }
      template {
        data = <<-EOF
          SECRET_KEY = "TODO:ChangeME!!!"
          HOSTNAME = "*"
          SSH_USERNAME = "vagrant"
          CONSUL_URL = "http://consul.service.consul:8500"
          NOMAD_URL = "http://nomad.service.consul:4646"
          VMCK_URL = 'http://{{ env "NOMAD_ADDR_http" }}'
          BACKEND = "qemu"
          QEMU_CPU_MHZ = 3000
          EOF
          destination = "local/vmck.env"
          env = true
      }
      template {
        data = <<-EOF
          {{- range service "vmck-imghost" -}}
            QEMU_IMAGE_PATH_PREFIX = "http://{{.Address}}:{{.Port}}"
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
            static = 10000
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
