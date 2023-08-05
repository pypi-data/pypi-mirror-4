Difio registration agent for CloudControl / Python applications.

It compiles a list of locally installed Python packages and sends it to
<http://www.dif.io>.


Installing on your CloudControl application
--------------------------------------

Create an account at <http://www.dif.io>

Create a Python application on CloudControl

Add a dependency in your `requirements.txt` file

::

    echo 'difio-cloudcontrol-python' >> requirements.txt

Set the following environment variables on Heroku

::

    cctlapp config:set DIFIO_USER_ID=YourUserID
    heroku config:set DIFIO_APP_NAME=MyApplication
    heroku config:set DIFIO_APP_URL=http://myapp.cloudcontrolled.com

Then commit, push and deploy your application to CloudControl

::

    git commit -a -m "added dependency on Difio"
    cctrlapp myapp push
    cctrlapp myapp deploy


Execute the registration script to submit the information to Difio

::

    cctrlapp myapp run /srv/www/.heroku/venv/bin/difio-cctrl-python
    Running `/srv/www/.heroku/venv/bin/difio-cctrl-python` attached to terminal... up, run.1
    Success, registered/updated application 8370e3be-6e54-462d-9ca9-224301c29a1d

That's it, you can now check your application statistics at
<http://www.dif.io>


Updating your requirements.txt
------------------------------

Whenever you change your `requirements.txt` file to include new
dependencies or upgrade/downgrade package versions you should
re-submit the information to Difio. 

::

    cctrlapp myapp run /srv/www/.heroku/venv/bin/difio-cctrl-python
