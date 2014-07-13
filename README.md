Non-Motorized Toolkit
Copyright (c) 2014 Open Technology Group Inc. (A North Carolina Corporation)
Developed under Federal Highway Administration (FHWA) Contracts:
DTFH61-12-P-00147 and DTFH61-14-P-00108

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright notice, 
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright 
      notice, this list of conditions and the following disclaimer 
      in the documentation and/or other materials provided with the distribution.
    * Neither the name of the Open Technology Group, the name of the 
      Federal Highway Administration (FHWA), nor the names of any 
      other contributors may be used to endorse or promote products 
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
Open Technology Group Inc BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF 
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED 
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


### NMTK

Non Motorized Travel Analysis Toolkit

The Non Motorized Travel Analysis Toolkit is a tool that facilitates the 
development and execution of non-motorized transportation models.

## System Requirements

While the NMTK Server/Tool Server(s) may run on systems with less than those
specified in the recommendations below, doing so is likely to result in 
degraded performance.

  * 1 GB Physical memory (on systems running only the NMTK systems.)
  * A Minimum of 2 GB RAM+Swap
  
Note: There are no specific CPU requirements, but it recommended that systems
      running the NMTK Server contain a CPU produced after 2010 .

The NMTK architecture uses an asychnronous processing model that submits "jobs"
for execution in the background, then returns results to the user when those
jobs are complete.  As a result, the lower the system specifications/performance
the longer the user would have to potentially wait from a response.

NMTK compatible tools will vary on computational resources required, refer to
tool documentation for any tool-specific system requirements.

## Version requirements

This document is written to use specific versions of various software components,
it is important to ensure that the versions of software that you are using meets
these minumim requirements (generally, newer versions are acceptable, but might
require additional testing to ensure they are compatible.)  Using an older version
than the recommended version may not result in an immediately visible incompatibility,
but may fail in certain use cases.

- GDAL 1.10 or later
- MapServer 6.1 or later
- Spatialite 3 or later
- mod_wsgi 3.3 or later
- Python 2.7 or later

Note that many of the python components installed in the Virtual Environment
specify required version information, for that reason they are not listed here.

Reference the requirements.txt file in the repository root for details about
python sub-component requirements.

## Installation Instructions

The installation instructions below are tested and work on Ubuntu 14.02 LTS .  Other distributions may require
different packages or steps to satisfy NMTK pre-requisites; and may require different steps to perform installation steps (such as installing celery daemons, Apache configuration files, etc.)

### Pre-Requisites

There are some pre-requisites that should be installed. The assumption in this case is that you are using debian, but 
these pre-reqs (and their install packages) translate easily (try google) to numerous other OSs:

 * apache2
 * python-dev
 * python-setuptools
 * python-virtualenv
 * libapache2-mod-wsgi
 * libxslt-dev libxml2-dev
 * libspatialite5 libspatialite-dev spatialite-bin
 * libgd2-xpm-dev
 * libproj-dev
 * libfreetype6-dev
 * cgi-mapserver
 * libgdal-dev gdal-bin
 * gfortran libopenblas-dev liblapack-dev

You may also need to download, compile, and install (from source) GDAL version 1.10 or greater if your
operating system does not provide a version greater than 1.10.  GDAL v1.10 added
support for CRS values in GeoJSON files - which are a requirement for NMTK.  Also, please note
that when compiling, be sure to provide the --with-python argument.

These directions assume that GDAL was installed from the OS repository.

#### Optional Installs

Currently NMTK does not use these components, but it's likely that some tools and/or the server will in the future.  Strictly speaking they are not a current pre-requisite, but it may be useful to install these:

  * R (follow instructions here: http://cran.r-project.org/bin/linux/ubuntu/README)

### Configuring Swap Space

If your system has less than 2 GB of RAM, it is recommended that you set up
some swap space.  This can be done using the following commands:

  1.  First, compute the number of "blocks" required to allocate swap space 
      of the size you want/need.  Each block is 1MB in size, there are 1024
      MB in 1 GB .  The number of "blocks" will be substituted into the command 
      below in place of "$COUNT"

  2.  Run the commands below to allocate the swap space.

    ```
    sudo dd if=/dev/zero of=/swapfile bs=$((1024*1024) count=$COUNT
    sudo mkswap /swapfile
    # Add a line to the end of /etc/fstab so the swap will be available on boot
    sudo sed -i '$ a /swapfile       none    swap    sw      0       0 ' /etc/fstab
    # Enable the newly allocated swap space
    sudo swapon -a
    ```
    
  3.  Use the command "swapon -s" to verify that the swap file you created is in use.

###Installation Instructions

The installation of this tool is predicated on an understanding of basic systems administration skills, as well
as some knowledge surrounding configuring a web server (such as Apache.)

 1.  Checkout the existing code and change into the root directory of the repository.  It is recommended that 
     you use the commands below to accomplish this task:

  ```
  sudo mkdir -p /var/www/vhosts/$(hostname --fqdn)
  sudo chown $USER /var/www/vhosts/$(hostname --fqdn)
  # If you have an ssh key installed for GIT, use this command
  git clone git@github.com:chander/nmtk.git /var/www/vhosts/$(hostname --fqdn)
  # To download the repo using your userid/password, use this command
  git clone https://github.com/chander/nmtk.git /var/www/vhosts/$(hostname --fqdn)
  ```
  
 2.  Initialize a virtual environment, using a command such as:

  ```
  pushd /var/www/vhosts/$(hostname --fqdn)
  virtualenv venv
  ```

 3.  Activate the virtual environment using the command:

  ```
  source venv/bin/activate
  ```

 4.  Install numpy and pysqlite by hand using requirements.txt (pip gets it wrong for some reason otherwise...):

  ```
  pip install $(cat requirements.txt|grep -i ^numpy)
  pip install --no-install $(grep pysqlite requirements.txt)
  sed -i "s/define=SQLITE_OMIT_LOAD_EXTENSION/#define=SQLITE_OMIT_LOAD_EXTENSION/g" venv/build/pysqlite/setup.cfg
  pip install --no-download pysqlite 
  ```

 5.  Install all the pre-requisite modules:

  ```
  CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install -r requirements.txt
  ```

  ###### Note
  
  Sometimes the GDAL installation will fail because pip gets the bindings, but not the entire 
  GDAL library (which GDAL's setup requires.)  This can be handled using the following procedure:

  ```    
  pip install --no-install $(grep GDAL requirements.txt)
  pushd venv/build/GDAL
  python setup.py build_ext --include-dirs=/usr/include/gdal --library-dirs=/usr/lib/gdal
  pip install --no-download GDAL
  popd
  sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf' # Add the path to gdal libs to system
  sudo ldconfig
  ```
     
 6.  Copy `NMTK_apps/NMTK_apps/local_settings.sample` to `NMTK_apps/NMTK_apps/local_settings.py`,
     edit the file (`NMTK_apps/NMTK_apps/local_settings.py`) per the directions contained
     therein. 

## Validating Your Installation

Once NMTK is installed, it makes sense to do some basic validation to ensure 
things are working properly.  Generally, this is done using a core set of
unit tests that exist in the tests/ subdirectory.  Follow the steps below to run 
the tests, they should all pass.  

The unit tests verify that tool discovery works properly, basic security
is working properly, user account login/logout/creation/passwords work 
properly, file imports work properly, and that jobs can be submitted to 
one of the built-in (umn) tools properly.

'''
  source venv/bin/activate
  pushd tests
  nosetests -v
  popd
'''

Generally, tests will take a few minutes to run, be patient.  If any of the tests
fail it could indicate that your server is mis-configured, or otherwise not working
properly.  A large file import test exists, but is skipped by default, due to 
the fact that in some systems it will require more than the allocated amount of
memory in order to successfully complete.

***     
### Note

> The steps below allow you to manually complete the remainder of the installation.
> However, a script exists (install.sh) that will perform these tasks for you.

> On development sites the install.sh script is typically used to "reset" the server,
> running it on a non-development server (where you have real data) will cause
> the catastrophic loss of data.  You should be cautious as to when/where you run
> install.sh

***

 1.  Install the celery components, a configuration file and init script exists for 
     this in the "celery" directory (celery and apache, respectively), 
     you will need to make several changes:
     
       * Modify celeryd-nmtk.default to contain the path to the NMTK installation.
         this file may then be copied to /etc/default/celeryd-nmtk
       * Copy the celeryd-nmtk.init script to /etc/init.d/celeryd-nmtk
       * Use the appropriate linux commands to ensure that the celery daemon
         is started when the server boots (sudo update-rc.d celeryd-nmtk-dev 
         defaults) 
 
 2.  By default, files for the NMTK server will go in the nmtk_files subdirectory,
     create this directory if it does not exist, and ensure that you have write 
     access to it:
 
  ```
  mkdir nmtk_files
  chown www-data.${USER} nmtk_files
  chmod g+rwxs nmtk_files
  ```
 
 3. Create the initial spatialite database:
     
  ```
  pushd nmtk_files
  spatialite nmtk.sqlite  "SELECT InitSpatialMetaData();"
  # Note: Ignore the "table spatial_ref_sys already exists error"
  chown www-data nmtk.sqlite
  ``` 
     
 5.  Now ensure that the sample fixture data is correct - you need not load this,
     and it will probably go away eventually, but it provides a "default" config
     for the purposes of having a server communicate with the default client.  It's likely
     that you will need to changed the server URL contained in the file to match
     that of your NMTK tool server.

  ```     
  vi NMTK_apps/NMTK_server/fixtures/initial_data.json
  ```
      
 6.  Change to the NMTK_apps subdirectory and initialize the database, and generate static media:

  ```
  pushd NMTK_apps
  python manage.py syncdb # Note: Here you should create an administrative user for yourself
  python manage.py minify # Needed if running in production
  python manage.py collectstatic  # Add -l to this for development systems, -c for production
  popd
  ```

 7.  Change the nmtk_files subdirectory so that it, and all it's subdirectories,
 are writeable by the www-data user (or whatever user the web server runs as.):

  ``` 
  chown -R nmtk_files www-data.www-data
  ```

 8.  Change the database and log locations so that the apache user will be able to access/write to them:

  ```
  sudo chown -R www-data logs
  sudo chmod g+rwxs logs
  sudo g+rw logs/*
  ```

     
 9.  Run the "python manage.py syncdb" command.  This will populate the initial
     database and get things so they are ready to run.  
 
 10.  Restart your apache server
 
 11.  Run the discover_tools command to discover new tools, and remove no-longer
      valid/published tools:

  ```    
  python manage.py discover_tools   
  ```
     
 12.  It is likely you will want to have a superuser you can use to administer 
      the server, this can be done using the following command, then following
      the prompts:
      
  ```
  python manage.py createsuperuser
  ```    
 
The remainder of configuration (such as removing the default tool server and/or
adding a new tool server) can now be done via the Administrative pages of the 
application - via the web.

To add a new tool:
 
Here we will assume the NMTK server "base" URL is is http://nmtk.example.com):

1.  Ensure your tool server is working (accepting requests via the web) 
    otherwise adding it will be a futile task, since the server will immediately 
    try to query the tool server for a list of tools it provides.
    
2.  Open your browser and point to the administrative page of the server:

  http://nmtk.example.com/server/admin

3.  Login using the credentials you created in step 9 (above)

4.  Click on "Tool Servers"

5.  If you wish to not use the "default" tools, then click the check box next 
	to the "Sample tool server", choose "delete" from the drop down, and 
	press "Go" to delete the tool server.  Note that deleting the tool server 
	will also delete all associated tools supplied by that server.

6.  To add a new tool server, click on "Add Tool Server" (upper right of the page.)

7.  Give your tool server a sensible name, and provide it with a URL (the url
    for the tool server.)  Note that the URL with "/index" appended should return a
    list of the available tools as a JSON string.  

8.  Copy the "auth token", which is the key used to sign requests between the 
    NMTK server and tool server.  This is commonly referred to as a 
    "shared secret" and is used to authenticate requests between the NMTK
    server and tool server.  You will need to share it with the tool server
    admin.

9.  Click "Save" to add the tool server (the NMTK server will immediately go 
    out and query the tool server to get a list of tools!)

10.  Copy the tool server ID that appears on the "Tool Servers" admin page
     and provide it, along with the shared secret you got in step 7 to the
     maintainer of the tool server.  You should also provide the tool admin
     the URL for the NMTK server.
    
Using the NMTK provided tool server:

If you are using the NMTK provided tool server, you'll need to get a set of
credentials (auth token and a tool server ID) from the NMTK server administrator.

Once you have these credentials, open up NMTK_apps/NMTK_apps/local_settings.py and
scroll to the end of the file.

Add a new entry to the NMTK_SERVERS= dictionary.  The key should be
the tool server ID (as provided by the NMTK server admin).  The value
should be another dictionary with two keys:

 - url - The URL for the NMTK server
 - secret - The "shared secret" (also called "auth key") provided by the NMTK 
            server administrator.
            
Restart apache to ensure these settings are reloaded and the tool will properly
accept and respond to authenticated requests from the tool server.

Note: If you wish to re-discover tools that an NMTK server provides, you have 
two options:
  * python manage.py discover_tools
      - This command will re-discover the provided tools for each tool server
        that is configured.
  * Return to the admin page, open the tool server you wish to refresh for editing,
    and hit "save" (no need to make any changes, the act of saving will kick off a 
    refresh for the tools provided by that tool server.)


Minification/Optimization of UI Components
------------------------------------------
1.  Run the node/install.sh script to install minification tools.
2.  Activate the virtual environment (source venv/bin/activate)
2.  Run "python manage.py minify" to minify code
3.  Run "python manage.py collectstatic -c" to re-install the static media (along with minified stuff.)
