from distutils.core import setup

setup(
        name='collectd-csv',
        version='0.5.1',
        author='Ville Petteri Tolonen',
        author_email='petteri.tolonen@gmail.com',
        packages=['CollectD_CSV', 'CollectD_CSV/plugins'],
        scripts=['bin/fetchCSV.py','bin/monitorCSV.py'],
        url='http://pypi.python.org/pypi/collectd-csv',
        license='FreeBSD',
        description='Fetch collectd CSV data matching the given parameters.',
        long_description=open('README.txt').read()
     )

