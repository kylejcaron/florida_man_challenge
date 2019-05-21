### ReadMe

This application is hosted on a AWS T2.micro EC2 instance, with an AWS RDS setup to store user feedback. Check out the medium article to learn more! 

Please note: this is app will not run as is, since personal details (access to my Amazon RDS) were removed from app.py. Setting up your own EC2 instance, RDS, and editing app.py with the relevant data should allow you to run this properly.


### Some help navigating app.py:

The variable POSTGRES is a dictionary containing user, pw, db, host, and port details that you must specify yourself.

app.secret_key must also be modified, you should create a secret key for yourself.

I recommend storing this in a separate script (kept off of github), and calling variables from that script as a more secure method of running the app.

### Setting up the pipeline

Running the following command in the static folder will start the pipeline and log any errors:

	nohup python pipeline.py &