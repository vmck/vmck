# TODO: remove hardcoded variabiles
#       add configurationa like in https://github.com/liquidinvestigations/node/blob/master/templates/drone.nomad
job "vmck" {
  datacenters = ["dc1"]
  type = "service"
  
  group "imghost" {
    task "nginx" {
      driver = "docker"
      config {
        image = "nginx:mainline"
        volumes = [
          "/usr/share/vmck-images:/usr/share/nginx/html", # TODO: add setting for host volume
          "local/nginx.conf:/etc/nginx/nginx.conf",
        ]
        port_map {
          http = 80
        }
        labels {
          liquid_task = "vmck-imghost-nginx"
        }
      }
      resources {
        memory = 80
        cpu = 200
        network {
          port "http" {
            static = 10000
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
            worker_connections  1024;
          }

          http {
            include       /etc/nginx/mime.types;
            default_type  application/octet-stream;

            log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                              '$status $body_bytes_sent "$http_referer" '
                              '"$http_user_agent" "$http_x_forwarded_for"';

            access_log  /var/log/nginx/access.log  main;

            sendfile        on;
            sendfile_max_chunk 4m;
            aio threads;
            keepalive_timeout  65;
            server {
              listen       80;
              server_name  _;
              access_log  /dev/stdout  main;
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
	  # TODO: add setting for interval and timeout
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
