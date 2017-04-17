# pyInternalJobExecutor

JobExecRequestWebUI.py

Language and platform:
  Build and tested in Python 3.5 in MacOS 10.12.3 with Google Chrome.
  It uses an embedded Web Server, flask.

Dependences installation:
  The next extra Python 3 libraries will be required:
      Flask
      Werkzeug
      pandas
  They can be installed, with the following or an equivalent command:
  
    pip3 install flask Werkzeug pandas
    
  If you are using Ubuntu/Linux, your Flask version might be 0.10 instead
  of 0.11, it means that your flask installation comes without the shell 
  integration. You can check your flask version running:
	pip show flask | grep Version
  In any case, I recommend to check first if it works **. If the execution 
  fails ("flask not found") your system requires the installation of 
  flask-cli.
  
	sudo pip3 install flask-cli
  
  ** IMPORTANT NOTE: test if it works first, in the Website they don't  
  recommend to install flask-cli if our flask version comes already with 
  shell integration:

Execution:
  chmod a+x
  ./run_JobExecRequestWebUI.sh
  
 or manually:
 
  export FLASK_APP=JobExecRequestWebUI.py
  flask run
  
 And type in your Web browser URL area: "http://localhost:5000/"
  
Testing the Application:
  It is provided an example, that is a script "script.sh" that only lists the 
  / directory. 
  In the WebApp served in "http://localhost:5000/", the name of the script 
  should be typed in the form in the bottom "Run a job", in the field 
  "Scrip complete name", so, "script.sh" must be typed there.
  Also, if we want to use a parameter, we can type, for example "-la" in the 
  "Parameters" field.
  
  They are also provided results of the execution of this script in 
  "src_scripts/strerrout", that can ve visualised selecting the link:
  "Download the STDOUT and STDERR of a script execution".
  We can also upload a file using the top link, 
  "Upload a data file to be used by the scripts"
