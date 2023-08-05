from distutils.core import setup

setup(
    name='PyQUIK',
    version='1.0',
    description='Python to QUIK Connector',
    long_description='Wrapper for TRANS2QUIK.dll (version 1.1) library.',
    author='Denis Kolodin',
    author_email='deniskolodin@gmail.com',
    url='https://bitbucket.org/deniskolodin/pyquik',
    packages=['pyquik'],
    package_data={'pyquik': ['TRANS2QUIK.dll']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
    license='BSD',
)
