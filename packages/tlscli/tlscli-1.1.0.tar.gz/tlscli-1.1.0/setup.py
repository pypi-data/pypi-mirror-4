from distutils.core import setup
from distutils.command.install import install
from distutils.errors import DistutilsExecError

setup(
    name='tlscli',
    version='1.1.0',
    author='Thomas Girard',
    author_email='thomas.g.girard@free.fr',
    url='https://launchpad.net/tlscli',
    license='New BSD License',
    description='Text User Interface client for CORBA Telecom Log Service.',
    long_description=open('README.txt').read(),
    scripts=['tlscli'],
    data_files=[('share/idl/tlscli',
                 ['idl/TimeBase.idl',
                  'idl/CosEventChannelAdmin.idl',
                  'idl/CosEventComm.idl',
                  'idl/CosNotification.idl',
                  'idl/CosNotifyChannelAdmin.idl',
                  'idl/CosNotifyComm.idl',
                  'idl/CosNotifyFilter.idl',
                  'idl/DsEventLogAdmin.idl',
                  'idl/DsLogAdmin.idl',
                  'idl/DsNotifyLogAdmin.idl'])],
    requires=['dateutil.parser'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ]
)
