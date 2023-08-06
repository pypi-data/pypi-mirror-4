from setuptools import setup, find_packages

requires = []
dep_links = []

for dep in open('requirements.txt').read().split("\n"):
    if dep.startswith('git+'):
        dep_links.append(dep)
    else:
        requires.append(dep)

setup(
    name='django-kindling',
    version="0.1.1",
    description='Create nice new Django projects.',
    long_description=open('README.rst').read(),
    url='https://github.com/radiosilence/django-kindling',
    author='James Cleveland',
    author_email='jc@blackflags.co.uk',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=requires,
    dependency_links=dep_links,
    entry_points = {
        'console_scripts': [
            'kindling = kindling.kindling:main',
        ]
    }
)