FROM python:3.7-stretch

ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /opt/vmck

RUN set -e \
 && apt-get update -qq \
 && apt-get install -qqy qemu-utils cloud-image-utils qemu-kvm \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && pip install --user pipenv

COPY setup.py Pipfile Pipfile.lock ./
RUN pipenv install

ADD vmck ./vmck
ADD contrib ./contrib
ADD manage.py runvmck Readme.md ./

VOLUME /opt/vmck/data
EXPOSE 8000
CMD ./runvmck
