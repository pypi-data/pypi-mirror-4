from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='EasyWidgets',
      version=version,
      description="A minimalistic approach to HTML generation and validation with TurboGears",
      long_description="""\
""",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='TurboGears FormEncode TurboGears2',
      author='Rick Copeland',
      author_email='rick446@usa.net',
      url='http://easywidgets.pythonisito.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_data={'ew': [
            'i18n/*/LC_MESSAGES/*.mo',
            'templates/*.html',
            'public/*/*']},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'python-dateutil',
        'formencode',
        'webhelpers',
        'paste'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [easy_widgets.resources]
      # dojo = ew.dojo:register_resources

      [easy_widgets.engines]
      json = ew.render:JsonEngine
      core-ew = ew.render:CoreEngine
      genshi = ew.render:GenshiEngine
      jinja2 = ew.render:Jinja2Engine
      kajiki = ew.render:KajikiEngine
      kajiki-text = ew.render:KajikiTextEngine
      kajiki-html4 = ew.render:KajikiHTML4Engine
      kajiki-html5 = ew.render:KajikiHTML5Engine
      kajiki-xml = ew.render:KajikiXMLEngine

      [paste.filter_factory]
      easy_widgets = ew.middleware:paste_filter_factory

      """,
      )
