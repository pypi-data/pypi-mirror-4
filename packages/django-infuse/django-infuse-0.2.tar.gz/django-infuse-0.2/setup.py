from setuptools import setup, find_packages

version = '0.2'

setup(name='django-infuse',
    version=version,
    description="A series of class based view mixins.",
    long_description=open("README.md", "r").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        ],
    keywords='',
    author='Kansas State University Web Team',
    author_email='omeweb@k-state.edu',
    url='http://github.com/kstateome/django-infuse',
    license='MIT',
    packages=find_packages(),
    install_requires = [],
    include_package_data=True,
    zip_safe=False,
)
