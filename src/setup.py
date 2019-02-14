# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from setuptools import setup

def get_file_conts(file):
    with open(file, "r") as f:
        contents = f.read()
    
    return contents

setup(
    name="effekt",
    version="0.0.1",
    description="Event Driven Programming framework.",
    long_description=get_file_conts("../README.md"),
    long_description_content_type="text/markdown",
    url="http://github.com/monolix/effekt",
    author="Monolix",
    author_email="monolix.team@gmail.com",
    license="MIT",
    packages=["effekt"],
    zip_safe=False
)
