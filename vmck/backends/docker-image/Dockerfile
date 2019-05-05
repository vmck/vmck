FROM ubuntu:18.04

ENV SSH_PUBKEY "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzIw+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoPkcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NOTd0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcWyLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQ== vagrant insecure public key"

RUN set -e && \
  apt-get update && \
  apt-get install -y openssh-server && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
  mkdir /var/run/sshd && \
  sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config && \
  adduser ubuntu --disabled-password --gecos '' && \
  mkdir ~ubuntu/.ssh && \
  cd ~ubuntu/.ssh && \
  echo "$SSH_PUBKEY" > authorized_keys && \
  chmod 700 . && \
  chmod 600 authorized_keys && \
  chown ubuntu: . authorized_keys && \
  echo "done!"

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
