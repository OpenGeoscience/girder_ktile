import subprocess
from distutils.core import setup
from pip.req import parse_requirements


def get_gdal_version():
    cmd = subprocess.Popen(['gdal-config', '--version'], stdout=subprocess.PIPE)
    cmd_out, cmd_err = cmd.communicate()
    return cmd_out

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

gdal_version = get_gdal_version()
reqs.append('GDAL=={}'.format(gdal_version))

setup(name='girder_ktile',
      version='0.0.1',
      description='A Girder Plugin to server geospatial tiles',
      author='Doruk Ozturk',
      author_email='doruk.ozturk@kitware.com',
      url='https://github.com/OpenGeoscience/girder_ktile',
      install_requires=reqs)
