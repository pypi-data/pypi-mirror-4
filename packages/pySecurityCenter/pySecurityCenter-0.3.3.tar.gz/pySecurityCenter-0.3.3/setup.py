from distutils.core import setup
import sys

# These are the requirements for pySecurityCenter
requirements = ['poster',]

if sys.version_info < (2, 6, 0) or sys.version_info > (3, 0, 0):
    requirements.append('simplejson')
    

setup(
    name='pySecurityCenter',
    version='0.3.3',
    description='Security Center 4 API Module',
    author='Steven McGrath',
    author_email='smcgrath@tenable.com',
    url='https://github.com/SteveMcGrath/pySecurityCenter',
    py_modules=['securitycenter'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
