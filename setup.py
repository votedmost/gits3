import setuptools


setuptools.setup(name='gits3',
                 version='1.0.0',
                 description='Git push over S3',
                 long_description=open('README').read().strip(),
                 author='Abdelhalim Ragab',
                 author_email='abdelhalim@gmail.com',
                 url='https://github.com/votedmost/gits3/',
                 packages=['gits3'],
                 install_requires=['dulwich'],
                 license='GPLv2',
                 zip_safe=False, )
