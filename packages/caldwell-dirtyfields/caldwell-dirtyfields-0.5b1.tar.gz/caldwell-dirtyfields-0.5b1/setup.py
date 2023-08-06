from setuptools import setup, find_packages


def listify(filename):
    return filter(None, open(filename, 'r').read().split('\n'))


setup(
    name="caldwell-dirtyfields",
    version=__import__('dirtyfields').get_version().replace(' ', '-'),
    url='http://github.com/smn/django-dirtyfields',
    license='BSD',
    description="Tracking dirty fields on a Django model instance",
    long_description=open('README.rst', 'r').read(),
    author='Simon de Haan',
    packages=find_packages(),
    install_requires=listify('requirements.pip'),
    classifiers=listify('CLASSIFIERS.txt')
)
