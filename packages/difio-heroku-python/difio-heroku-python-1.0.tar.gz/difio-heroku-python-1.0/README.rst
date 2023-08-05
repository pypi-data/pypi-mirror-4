Difio registration agent for Heroku / Python applications.

It compiles a list of locally installed Python packages and sends it to
<http://www.dif.io>.


Installing on your Heroku application
--------------------------------------

Create an account at <http://www.dif.io>

Create a Python application on Heroku

Add a dependency in your requirements.txt file

::

    echo 'difio-heroku-python' >> requirements.txt

Set the following environment variables on Heroku

::

    heroku config:set DIFIO_USER_ID=YourUserID
    heroku config:set DIFIO_APP_NAME=MyApplication
    heroku config:set DIFIO_APP_URL=http://myapp.herokuapp.com

Then push your application to Heroku

::

    git push heroku master

That's it, you can now check your application statistics at
<http://www.dif.io>
