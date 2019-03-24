FROM ubuntu:18.04

ENV SSH_PUBKEY "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIM9QBDGxYk2MjJHMa30Ut166/s61Yk1ieTn3aXjAnnvP"

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
