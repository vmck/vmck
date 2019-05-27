FROM python:3.7-stretch

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /opt/vmck

COPY setup.py Pipfile Pipfile.lock ./

RUN set -e \
 && pip install --user pipenv \
 && pipenv install

VOLUME /opt/vmck/data
EXPOSE 8000

CMD ./runvmck

ADD vmck ./vmck
ADD manage.py runvmck ./
