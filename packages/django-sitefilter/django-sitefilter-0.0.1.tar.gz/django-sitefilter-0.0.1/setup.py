from setuptools import setup, find_packages

setup(
    name='django-sitefilter',
    version='0.0.1',
    description='Django app adding a global filter limiting admin content to selected site.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    license='BSD',
    url='http://github.com/praekelt/django-sitefilter',
    packages = find_packages(),
    dependency_links = [
    ],
    install_requires=[
        'django',
    ],
    tests_require=[
        'django-setuptest',
    ],
    test_suite="setuptest.setuptest.SetupTestSuite",
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
