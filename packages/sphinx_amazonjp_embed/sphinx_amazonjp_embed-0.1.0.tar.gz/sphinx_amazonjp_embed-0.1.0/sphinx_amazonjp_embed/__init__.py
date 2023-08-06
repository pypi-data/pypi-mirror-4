#-*- coding:utf-8 -*-
u'''
embedding twitter's tweet in sphinx

usage:

First of all, add `sphinx_tweet_embed` to sphinx extension list in conf.py

.. code-block:: python

   extensions = ['sphinx_amazonjp_embed']


then set amazonjp_affiliate_id in conf.py

.. code-block:: python

   amazonjp_affiliate_id = 'xxxxx-XX'


next, use `amazonjp` directive.

.. code-block:: rst

   .. amazonjp:: http://www.amazon.co.jp/dp/477415539X


finally, build your sphinx project.


.. code-block:: sh

   $ make html

'''

__version__ = '0.1.0'
__author__ = '@shomah4a'
__license__ = 'LGPLv3'



def setup(app):

    from . import amazonjp

    app.add_javascript('http://platform.twitter.com/widgets.js')

    app.add_node(amazonjp.amazonjp,
                 html=(amazonjp.visit, amazonjp.depart))
    app.add_directive('amazonjp', amazonjp.AmazonJPDirective)

    app.add_config_value('amazonjp_affiliate_id', None, 'html')

