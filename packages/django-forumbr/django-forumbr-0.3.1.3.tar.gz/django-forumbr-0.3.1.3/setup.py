# -*- coding:utf-8 -*-
import sys
import setuptools

setuptools.setup(
    name="django-forumbr",
    version="0.3.1.3",
    packages=[
        "forum",
        "forum.templatetags",
    ],

    install_requires=[
        "django",
        "PIL",
        "south",
        "postmarkup",
        "textile",
        "markdown",
        "docutils",
        "html5lib"
    ],

    author="Italo Maia",
    author_email="italo.maia@gmail.com",
    url="https://bitbucket.org/italomaia/django-forumbr",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Simple and complete django forum solution",
    keywords="django forum python",
    include_package_data=True,
)
