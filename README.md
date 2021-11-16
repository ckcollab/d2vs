# d2vs

diablo 2 vision system

## installation

First do this... (swap in your version of CUDA)

```bash
$ conda install pytorch torchvision cudatoolkit=10.1 -c pytorch
```

Then this..

```bash
$ pip install d2vs
```

_NOTE: this can run via CPU, but via GPU is far superior. You must install CUDA and the appropriate python jazz
to get that working, for me with CUDA10.1:_

```bash
$ >conda install torch torchvision cudatoolkit=10.1 -c pytorch
```

# development

## setup

```bash
$ git clone ...
$ pip install -r requirements.dev.txt
```

## running tests

```bash
$ pytest
```

## distributing

```bash
$ python setup.py sdist bdist_wheel
$ twine upload dist/*
```
