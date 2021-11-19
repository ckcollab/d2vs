# d2vs

diablo 2 vision system

## installation

```bash
$ pip install d2vs
```

_NOTE: this can run via CPU, but via GPU is far superior. You must install CUDA and the appropriate python jazz
to get that working, for me with CUDA10.1:_

```bash
$ conda install torch torchvision cudatoolkit=10.1 -c pytorch
```

# usage

<div align="center">

  ![image](https://user-images.githubusercontent.com/2185159/142674287-37311056-5483-4956-b786-b5ffc17bfc69.png)

  _(586_gold.png)_
</div>


```bash
>>> import numpy as np
>>> from d2vs.ocr import OCR
>>> from PIL import Image
>>>
>>> # Initiate OCR
>>> ocr = OCR()
>>>
>>> # Load an Image
>>> img = Image.open("586_gold.png")
>>>
>>> # Scan the image
>>> bounds, text, item_type = ocr.read(np.asarray(img, dtype='uint8'))
>>> print(text)
'586 Gold'
>>> print(item_type)
'Normal'
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
