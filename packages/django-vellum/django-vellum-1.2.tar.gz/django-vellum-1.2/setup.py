from setuptools import setup, find_packages

setup(
    name='django-vellum',
    packages=find_packages(),
    version='1.2',
    description='A web log for Django.',
    author='Peter Hogg',
    author_email='peter@havenaut.net',
    url='https://github.com/pigmonkey/django-vellum',
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
    ],
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['django-inlineobjects',
                      'django-simplesearch',
                      'django-taggit',
                      'django-taggit-templatetags',
                      'django-markup',
                      'Markdown'],
)
