#download ez_setup.py from http://peak.telecommunity.com/dist/ez_setup.py
#import ez_setup
#ez_setup.use_setuptools()
from setuptools  import setup
setup(name="Akamu",
      version="0.6",
      description="An Akara module for managing the use of an RDF dataset, a "+
                  "XML/RDF filesystem, and XSLT extension functions within a "+
                  "web application",
      package_dir = {
        'akamu': 'lib',
      },
      packages=[
        "akamu",
        "akamu.protocol",
        "akamu.wheezy",
        "akamu.security",
        "akamu.xslt",
        "akamu.demo",
        "akamu.util",
        "akamu.diglot",
        "akamu.config",
      ],
      install_requires = [
        'python-memcached',
        'akara',
        'amara',
        'wheezy.http==0.1.236',
        'wheezy.core==0.1.70',
        'wheezy.caching==0.1.55',
        'webob',
        'httpagentparser',
#        'httplib2'
      ],
      zip_safe=False
)