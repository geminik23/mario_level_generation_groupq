# GroupQ Level Generator
This code is developed and tested with Python 3.7


## requirements
The only thrid-party library used in this program is numpy.

To install,

```bash
pip3 install -r requirements.txt
```

## How to run?
To run the generator, type with config file. The configure file is require to run.

```bash
python3 main.py config.ini
```

## Configuration file

``` ini
[Params]
block_unit_size=2 
num_levels=10 

[InputPath]
original = ./levels/original
something = ./levels/something

[OutputPath]
;path = /home/geminik23/workspace/__java__/ecs7002p-marioai/levels/groupq/s5
path = ./levels/groupq

```

1. [Params]
*  block_unit_size : The size of block consisted of tiles.
*  num_levels : The number of levels to be generated

2. [InputPath]
*  {name} : Folder paths to be learned. Multiple variables are possible. And the name will be ignored.

3. [OutputPath]
*  path : The folder path to be generated.

## Paper
[Mario AI: A Level Generation Framework](Mario%20AI_%20A%20Level%20Generation%20Framework.docx.pdf)
