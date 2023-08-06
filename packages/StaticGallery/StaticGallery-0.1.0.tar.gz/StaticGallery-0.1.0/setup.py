import os

from distutils.core import setup


CONFIG_PATH = os.path.expanduser('~/.staticgallery')


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


setup(
    name='StaticGallery',
    version='0.1.0',
    author='Javier Aguirre',
    author_email='contacto@javaguirre.net',
    scripts=['bin/staticgallery'],
    packages=['static_gallery'],
    package_data=get_package_data('static_gallery'),
    data_files=[(CONFIG_PATH, ['data/config.cfg']),
                ('/'.join([CONFIG_PATH, 'site']), [])
                ],
    url='https://github.com/javaguirre/staticgallery',
    license='LICENSE.txt',
    description='Static gallery generation using Jinja2 ',
    long_description=open('README.txt').read(),
    install_requires=['Jinja2 == 2.6',
                      'PIL == 1.1.7']
)
