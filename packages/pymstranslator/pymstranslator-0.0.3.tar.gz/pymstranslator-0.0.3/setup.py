from distutils.core import setup

setup(
    name='pymstranslator',
    description='Python module for interfacing with Microsoft(r) Translator',
    long_description=open('README.rst').read(),
    version='0.0.3',
    packages=['mstranslator', 'mstranslator/endpoints'],
    author='Monwara LLC',
    author_email='branko@monwara.com',
    url='https://bitbucket.org/monwara/pymstranslator',
    download_url='https://bitbucket.org/monwara/pymstranslator/downloads',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
)


