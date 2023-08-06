==
Bo
==
Bo is a chatbot written in Python. It can run either as a standalone program or easily be embedded in your own program.

Bo is distributed under the BSD licence, check LICENCE_ for further information.

Getting your very own copy of Bo
--------------------------------
The easiest way to get Bo running is deploying it on Heroku_:

.. sourcecode:: console

    $ git init bo-heroku
    $ cd bo-heroku/
    $ heroku create --stack cedar
    $ wget "https://bitbucket.org/konikos/bo/raw/tip/requirements.txt"
    $ echo "-e hg+http://bitbucket.org/konikos/bo#egg=bo" >>requirements.txt
    $ echo "worker: bo -c config.yaml" >Procfile
    $ wget -O config.yaml "https://bitbucket.org/konikos/bo/raw/tip/conf/xmpp.yaml"

Edit the created ``config.yaml`` to set your password, possibly add extra plugins, and execute the following to get Bo running:

.. sourcecode:: console

    $ git commit -a -m 'init'
    $ git push heroku master
    $ heroku ps:scale worker=1

If you are having issues running Bo, use ``heroku logs`` to see the output from Bo and ``heroku restart`` to restart it.


Plugins
-------
Plugins add extra functionality to Bo. The provided plugins can be found in ``bo/dist/plugins``.


.. _LICENCE: https://bitbucket.org/konikos/bo/src/tip/LICENCE
.. _Heroku: http://www.heroku.com
