from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from shutil import copy
from .base_settings import base_dir
import subprocess


def homepage(request):
    if request.method == 'POST'and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            fs.save(request.FILES['file'].name, request.FILES['file'])
            zp = ZipFile(fs.path(request.FILES['file'].name))
            with TemporaryDirectory() as tmp_dir:
                print(tmp_dir)
                zp.extractall(tmp_dir)
                copy(base_dir / 'vagrant-files' / 'Vagrantfile', tmp_dir)
                proc = subprocess.Popen('docker run --env VMCK_URL=http://127.0.0.1:8000 --network="host" -it --rm --volume $(pwd):/homework  vmck/vagrant-vmck:latest /bin/bash -c "cd /homework; vagrant up; vagrant destroy -f"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=tmp_dir)  # noqa: E501
                while proc.poll() is None:
                    print(''.join(proc.stdout.readline().decode('utf-8').strip()))  # noqa: E501
    else:
        form = UploadFileForm()

    return render(request, 'vmck/homepage.html', {'form': form})
