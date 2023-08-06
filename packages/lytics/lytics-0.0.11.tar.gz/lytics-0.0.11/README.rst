Lytics Data Tool
==================

.. container:: lead

    A tool for sending data to Lytics.io and managing an account.  Provides the ability to upload data from databases, csv files, tail events from log files, send single events.   Api management provides ability to create users/accounts/queries.

Installation
---------------------
::

    pip install lytics

    # if you don't have Pip install it
    curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py
    # or apt-get install python-pip on debian

Data collection
---------------------
This allows collection of 2 general types of data

1.  Event data:  a user visits, views, clicks.  You can upload log files, other user events.

2.  Entity Data:   Information about a user, company, etc.

examples::
    
    # start an interactive command line to type in name=value pairs for collection
    # sends one request per line
    lytics --aid=123456 --key=myapikey collect

    # tail a file, sending each new line as a lytics.io data point
    tail -F myfile.log | lytics --aid=123456 --key=mysecret collect

    # write to stdout
    myapp | lytics --aid=123456 --key=mysecret collect

    # or the same
    lytics --aid=123456 --key=mysecret collect < myapp

Read from A database.  Because lytics handles *Entity* Data you may often want to read from a database and upload info to be added to event level data from javascript or mobile tags::
    
    # read from a database table using .sql in `myscript.sql` and send one entry per row
    lytics --dbuser=username --dbpwd=pwd --dbhost=localhost \
        --db=mydbname --aid=123456 --key=SECRET \
        DB upload < myscript.sql 


Management Api
---------------------
Manage your queries (analysis)::

    
    # sync the qry.txt files to the api
    lytics setconfig key yourkey
    lytics query sync < qry.lql


Configuration Options
-----------------------
You can pass parameters such as *aid* (accountid) or *key* (apikey) on the command line or create environment variables for them.  

Create a *.lytics* file in current folder with these values::

    # Set the aid setting permanently to 123456 in current folder
    export LIOAID=123456

    # api key
    export LIOKEY=myapikey
    
    # load them
    . .lytics
    
    lytics query sync < qry.lql  # does not require key



