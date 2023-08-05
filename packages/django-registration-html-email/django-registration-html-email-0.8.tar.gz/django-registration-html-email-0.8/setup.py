from distutils.core import setup
import os

from registration_html_email import get_version


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('registration_html_email'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[13:] # Strip "registration_html_email/" or "registration_html_email\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-registration-html-email',
      version=get_version().replace(' ', '-'),
      description='An extensible user-registration application for Django, with html emails (django-registration simple fork)',
      author='Diego Cebrian',
      author_email='dcebrian@serincas.com',
      url='https://bitbucket.org/hisie/django-registration-html-mail',
      download_url='https://bitbucket.org/hisie/django-registration-html-mail/get/tip.tar.gz',
      package_dir={'registration_html_email': 'registration_html_email'},
      packages=packages,
      package_data={'registration_html_email': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
