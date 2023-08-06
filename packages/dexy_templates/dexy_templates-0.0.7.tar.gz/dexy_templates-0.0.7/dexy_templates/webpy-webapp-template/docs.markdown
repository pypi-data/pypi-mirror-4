# Refreshing Documentation: An Introduction to Dexy

by Ana Nelson

More information about Dexy is available at http://dexy.it. You can follow the project @dexyit on twitter or the author @ananelson. Dexy is open source software to make you and your docs awesome. Check it out!

## Setup and Teardown

We want to take screenshots of a running web app. To do this, we will need the web app to be started with a fresh database, and then we want the server to be stopped after we are finished. Here is how we configure dexy to run a setup script, then take screenshots, then run a teardown script:

{{ d['dexy.yaml|idio']['screenshots'] }}

Note that the setup script has several file extensions listed beneath it. Here are the files present in the directory when the setup script runs:

{{ d['setup.sh|idio|shint|pyg']['info'] }}

We create a new database file and load the sql schema into it:

{{ d['setup.sh|idio|shint|pyg']['load-sql'] }}

Here is the sql:

{{ d['schema.sql|pyg'] }}

Now we are ready to start the server. We use `nohup` so the server will keep running after this script exits, and we make sure the server is running as expected:

{{ d['setup.sh|idio|shint|pyg']['start-server'] }}

After the screenshots are finished, we call our teardown script which kills the server:


{{ d['teardown.sh|idio|shint|pyg']['kill'] }}

Finally we confirm that the process was killed:

{{ d['teardown.sh|idio|shint|pyg']['check-killed'] }}

## Casper JS Screenshots

We will use Casper JS to create screenshots. First we need to set up a casper instance:

{{ d['screenshots.js|idio']['setup'] }}

To start with we take a screenshot of the app's home page:

{{ d['screenshots.js|idio']['initial'] }}

Here is what the site's home page looks like:

![screenshot](index.png)

Here is the HTML for the home page:

{{ d['templates/index.html|pyg'] }}

The form for adding a new TODO is created in the Index class:

{{ d['todo.py|idio']['index-class'] }}

The GET method renders the form and displays the main page:

{{ d['todo.py|idio']['index-get'] }}

Next we want to add a TODO:

{{ d['screenshots.js|idio']['add-todo'] }}

![screenshot](add.png)

The POST method handles creating a new TODO object:

{{ d['todo.py|idio']['index-post'] }}

Here is how the todo app looks with this new todo added:

![screenshot](added.png)

Now we want to delete this TODO:

{{ d['screenshots.js|idio']['delete-todo'] }}

Here is the code which deletes TODOs:

{{ d['todo.py|idio']['delete-class'] }}

We confirm that the TODO is deleted:

![screenshot](deleted.png)

## Source

Here is the source of this document:

{{ d['docs.markdown|pyg'] }}
