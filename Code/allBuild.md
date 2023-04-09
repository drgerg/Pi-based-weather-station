## Building Brilliant (home to 'allApp.py' and others)

(alternate notes in OneNote)

**Assumptions:** Things that were already in place.

- In all cases, the OS is Ubuntu.
- Brilliant is the name of the machine I'm working on. I'm replacing the storage drive and updating the OS.
- Valiant is the name of the machine I am working at. Windows Subsystem for Linux running Ubuntu.
- Brilliant is in the 'hosts' file on Valiant, so I don't need to type the IP address.
- ssh keys are in place on Valiant for use in public key authentication (passwordless login).
- mySQL databases must be moved from the old drive to the new one. They must be 'exported' before the old drive is deactivated.
- The username for the primary user must be the same on the new drive/OS as on the old one.
- The contents of the /home/{user}/ folder must be copied intact to the new drive. That's where my Python program files live.


Curly brackets should not be typed in commands. They indicate a private value that should be known only to you.  
For example: {user} is your username.

## Getting Started ##

### First: Before removing the old drive, prepare to move mySQL data.

**Either ssh into Brilliant, or do this locally on Brilliant**

    mysql -u {user} -p

Now you're logged into mySQL, so from now on we're at the mySQL prompt.

    select @@datadir;
    show databases;
    quit;
This gives you info on the location and names of your databases.

**Now export your databases** at the Linux commandline.

    mysqldump outdata > outdata-20210220.sql -u {user} -p

The result is 'outdata-20210220.sql' in your current directory.
Repeat for each database you want to export / backup.

### Second: Install the new drive.

**Locally on Brilliant:**
Prepare the new drive.

   1. Disconnect the old drive from the computer.
   2. Connect the new drive.
   3. Install the OS (Remember the user name and the machine name need to be the same as they were before.)

Get ssh-server up and running on the new drive.

    sudo install ssh-server
    sudo nano /etc/sshd_config

Uncomment #port 22 and replace 22 with your {port} number.

    sudo service sshd restart

**Make the old drive available to the system in some fashion.**

I used a USB interface to connect the old drive to Brilliant.  
Then copy these folders over to the new drive:
   
    The /home/{user}/all folder.
    The /home/{user}/.ssh folder.


**Get mySQL up and running on the new drive.**

    sudo apt install mysql-server
    sudo mysql      (logs you in as root)
    create user {user}@localhost identified by '{password}';
    grant all privileges on *.* to {user}@localhost;
    flush privileges;
    quit;

That should have done it.  But NO, I had been using 5.7.33 and the new mySQL was 8.0.23.
Every time I brought my databases in, mysql went squirrely.

I finally had to figure out how to install 5.7.3 again.  It went like this:

    wget https://dev.mysql.com/get/mysql-apt-config_0.8.12-1_all.deb
    sudo dpkg -i mysql-apt-config_0.8.12-1_all.deb
        Select Bionic
        Select mySQL 5.7 server
    sudo apt-get update
    sudo apt install -f mysql-client=5.7.33-1ubuntu18.04
    sudo apt install -f mysql-community-server=5.7.33-1ubuntu18.04
    sudo apt install -f mysql-server=5.7.33-1ubuntu18.04

I did assign a password to the 'root' account. I tried to use the 'empty' method first time through these steps, but it didn't work, so I had to start over.

    sudo mysql_secure_installation

    sudo ufw status verbose
    sudo ufw allow {port}/tcp
    sudo ufw allow from 192.168.1.1/24 to any port 3306
    sudo ufw allow 80,443/tcp

    sudo ufw enable

**Create a mySQL user for each node of PiNet for allSysReport.service (zAllSysChk.py)**

**Copy the ssh key to the other nodes.**

    ssh-copy-id -i id_rsa -p {port} {user}@{machine}

This needs to be done from Brilliant (/home/{user}/.ssh) to every other PiNet machine <b> including Brilliant </b>.  I know, that doesn't exactly make sense, but it is true.


**Locally on Valiant**

Copy the ssh keys to Brilliant and reset known_hosts to accept the new Brilliant.

    ssh-copy-id -i {publickeyfile} -p{port} {user}@brilliant
    ssh-keygen -f "/home/{user}/.ssh/known_hosts" -R "[brilliant]:{port}"

**Log into Brilliant.**

    ssh -p {port} 

Start installing some of the dependencies.

    sudo apt install python3-pip
    sudo apt-get install nginx
    sudo pip3 install gunicorn
    pip3 install mysql-connector
    sudo apt-get install python3-numpy
    pip3 install noaa-sdk
    sudo pip3 install -U Flask
    sudo pip3 install flask_wtf
    pip install pyyaml ua-parser user-agents
    sudo apt install mailutils
    sudo apt-get install msmtp msmtp-mta

**Configure nginx**

    sudo nano /etc/nginx/nginx.conf

Once in there, look for these various entries and make them look like this, character for character, no # in front:  (All this comes from e-tinkers linked above.)

    multi_accept on;
    keepalive_timeout 30;
    server_tokens off; 
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 5;
    gzip_http_version 1.1;

Add a line just before the <b>gzip_types</b> line that says this: 

    gzip_min_length 256;

Honestly, I don't know if this is necessary, but it was in the instructions, and I can say it didn't hurt anything, so, plug this in just below the # gzip_types ... line that is there. (Yes, you can just use this to replace the existing line.)

    gzip_types
       application/atom+xml 
       application/javascript 
       application/json 
       application/rss+xml 
       application/vnd.ms-fontobject 
       application/x-font-ttf 
       application/x-web-app-manifest+json 
       application/xhtml+xml 
       application/xml 
       font/opentype 
       image/svg+xml 
       image/x-icon 
       text/css 
       text/plain 
       text/x-component 
       text/javascript 
       text/xml;

**Set up msmtp to handle notifications**

The instructions can be found in the doorPi (ohd) docs here on Github. https://github.com/casspop/ohd/blob/master/SetupRaspianForOhd.md
I don't see any reason to copy and paste that over here.



