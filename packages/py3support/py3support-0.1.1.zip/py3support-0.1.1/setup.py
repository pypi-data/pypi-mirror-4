from setuptools import setup


setup(
    name='py3support',
    version='0.1.1',
    scripts=['bin/py3support'],
    install_requires=['docopt', 'requests'],
    url='https://github.com/coagulant/py3support',
    license='MIT',
    author='Ilya Baryshev',
    author_email='baryhsev@gmail.com',
    description='Check which of your dependencies already support python 3',
    long_description=open('README.rst').read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    )
)
