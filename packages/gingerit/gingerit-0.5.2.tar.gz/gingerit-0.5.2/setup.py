from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='gingerit',
    version='0.5.2',
    author='Tim Kleinschmidt',
    author_email='tim.kleinschmidt@gmail.com',
    packages=find_packages(),
    url='https://github.com/Azd325/gingerit',
    license='BSD',
    description='Correcting spelling and grammar mistakes based on the context of complete sentences. Wrapper around the gingersoftware.com API',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    install_requires=requirements
)
