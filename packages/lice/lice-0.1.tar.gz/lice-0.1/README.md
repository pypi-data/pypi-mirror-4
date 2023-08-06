# lice

Lice generates license files. No more hunting down licenses from other projects.


## Installation

    easy_install lice

or

    pip install lice


## Overview

Generate a BSD-3 license, the default:

    $ lice
    Copyright (c) 2013, Jeremy Carbaugh

    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    ...

Generate an MIT license:

    $ lice mit
    The MIT License (MIT)
    Copyright (c) 2013 Jeremy Carbaugh

    Permission is hereby granted, free of charge, to any person obtaining a copy
    ...

Generate a BSD-3 license, specifying the year and organization to be used:

    $ lice -y 2012 -o "Sunlight Foundation"
    Copyright (c) 2012, Sunlight Foundation

    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    ...

If organization is not specified, lice will first attempt to use `git config` to find your name. If not found, it will use the value of the $USER environment variable. If the project name is not specified, the name of the current directory is used. Year will default to the current year.

You can see what variables are available to you for any of the licenses:

    $ lice --vars mit
    The mit license template contains the following variables:
      year
      organization


## Usage

    usage: lice [-h] [-o ORGANIZATION] [-p PROJECT] [-t TEMPLATE_PATH] [-y YEAR]
                [--vars] [license]

    positional arguments:
      license               the license to generate, one of: apache, bsd2, bsd3,
                            cddl, cc0, epl, gpl2, gpl3, lgpl, mit, mpl

    optional arguments:
      -h, --help            show this help message and exit
      -o ORGANIZATION, --org ORGANIZATION
                            organization, defaults to .gitconfig or
                            os.environ["USER"]
      -p PROJECT, --proj PROJECT
                            name of project, defaults to name of current directory
      -t TEMPLATE_PATH, --template TEMPLATE_PATH
                            path to license template file
      -y YEAR, --year YEAR  copyright year
      --vars                list template variables for specified license
