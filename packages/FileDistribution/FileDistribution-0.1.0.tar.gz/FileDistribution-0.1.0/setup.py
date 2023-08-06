from setuptools import setup, find_packages

setup(
    name='FileDistribution',
    version='0.1.0',
    author='Adam Kubica',
    author_email='caffecoder@kaizen-step.com',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries',
        ],
    scripts=[],
    url='http://github.org/caffecoder/fdist-python',
    license='MIT',
    description='Simple file distribution library.',
    long_description='Simple library that allows organize distribution of files within hex based tree.',
    install_requires=[],
    platforms=['darwin','linux2','freebsd7'],
)
