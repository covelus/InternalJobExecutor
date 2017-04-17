#!/usr/bin/env python3


__author__  = "Breogan COSTA"
__version__ = "1.0"
__email__   = "xbcovelo (at) gmail (dot) com, breo (at) cern (dot) ch"

'''
 Required Python packages: flask Werkzeug pandas
 You can install them in the next (or some equivalent) way:
 
 pip3 install flask Werkzeug pandas
 
 Optional: if you run GNU/Linux or Ubuntu and your Flask version is previous
 than 0.11, you may need to install the CLI integration.
 
 [NOTE: in the Flask Website they recommend to avoid installing flask-cli if 
 you already have CLI integration]
 
 sudo pip3 install flask-cli
 
'''

import logging
from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import decimal
import subprocess
import time, datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


SCRIPTS_STORE   = "src_scripts/"
SCRIPTS_RUN_DIR = SCRIPTS_STORE # for future improvements
SCRIPTS_OUT_DIR = SCRIPTS_STORE # for future improvements
DATA            = "data/"
DATA_FILES_DIR  = SCRIPTS_OUT_DIR + DATA
RESULTS         = "results/" # for future improvements
RESULTS_DIR     = SCRIPTS_OUT_DIR + RESULTS # for future improvements
STDOUTERR       = "stderrout/"
STDOUT_DIR      = SCRIPTS_OUT_DIR + STDOUTERR
HTMLS_DIR       = "html/"
KPIS            = "kpis/"
KPIS_DIR        = SCRIPTS_OUT_DIR + KPIS

app.config['RESULTS_FOLDER'] = SCRIPTS_STORE + STDOUTERR


@app.route('/', methods=['GET'])
def main_page():
  fileHandler = open(HTMLS_DIR+"index.html",'r')
  content = fileHandler.read()
  fileHandler.close()
  return content

def runScript(scriptname, params = None):
  out = ""
  err = ""
    
  if params != None:
    job_call = ["sh", SCRIPTS_RUN_DIR+scriptname, params]
  else:
    job_call = ["sh", SCRIPTS_RUN_DIR+scriptname]
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  
  try:
    logging.debug(" job call: ", job_call)
    out, err = subprocess.Popen(job_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    logging.debug(out)
    logging.info(err)
  except:
    logging.error(" Error executing the script")
  
  out_to_ret = str(out).replace("\\n","\n")
  err_to_ret = str(err).replace("\\n","\n")
  
  try:
    df = os.statvfs(".")
    dfstr = str( round( (df.f_bavail * df.f_frsize) / (1024**3), 4) ) #df in a string and in GiB
  except:
    logging.error(" Disk free check not performed")
    dfstr = ""
    
  return timestamp, scriptname, dfstr, out_to_ret, err_to_ret

def saveResult(file_2_save, data, log_error_message):
  try:
    fileHandler = open(file_2_save,'wb')
    write_res = fileHandler.write(bytes(data, 'utf-8'))
    fileHandler.close()
    return True
  except:
    logging.error(log_error_message)
    return False
  
def saveKPIs(timestamp, scriptname, disk_free):
  whitespace = timestamp.index(' ')
  timestamp_date = timestamp[:whitespace]
  with open(KPIS_DIR + timestamp_date + ".log", 'a+') as file:
    file.write(timestamp + "," + scriptname + "," + disk_free + "\n")

@app.route('/run', methods=['POST'])
def run():
  j_script = request.form['jobname']
  j_params = request.form['jobparams']
  if j_params == "":
    timestamp, scriptname, df, exec_result, err = runScript(j_script)
  else:
    timestamp, scriptname, df, exec_result, err = runScript(j_script, j_params)
  
  logging.debug( timestamp.replace(":","-").replace(" ","_") )
  logging.debug(scriptname)
  logging.debug(df, " GiB free")
  
  to_ret =  timestamp + '<br>' + scriptname + '<br>' + df + " GiB free" + '<br>' + exec_result
  file_2_save = STDOUT_DIR + timestamp.replace(":","-").replace(" ","_") + "-" + scriptname.replace(".","_") + "-stdOUT.txt"
  saveResult(file_2_save, exec_result, "Error saving script execution STDOUT")
  file_2_save = STDOUT_DIR + timestamp.replace(":","-").replace(" ","_") + "-" + scriptname.replace(".","_") + "-stdERR.txt"
  saveResult(file_2_save, err, "Error saving script execution STDERR")
  saveKPIs(timestamp, scriptname, df)
  
  return to_ret

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
  if request.method == 'POST':
    f = request.files['userfile']
    content = f.read()
    fileHandler = open(DATA_FILES_DIR+f.filename,'wb')
    write_res = fileHandler.write(content)
    fileHandler.close()
    return "Wrote file " + f.filename + " with size " + str(write_res) + " Bytes<br><a href=\"/\">Go to index</a></p><br>"
  else:
    fileHandler = open(HTMLS_DIR+"upload.html",'r')
    content = fileHandler.read()
    fileHandler.close()
    return content

@app.route('/stderrout', methods=['GET'])
def get_stdX():
  dirs = os.listdir(STDOUT_DIR)
  html_content = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
      <title>Result files</title>
      <meta http-equiv="content-type" content="text/html;charset=utf-8" />
      <meta name="generator" content="Geany 1.26" />
    </head>
    <body>
      <h1>RESULT FILES</h1>\n\t"""
  
  for i in dirs:
    size = os.path.getsize(STDOUT_DIR + i)
    html_content = html_content + "\t<p><a href=\"" + STDOUTERR + str(i) + "\">" + str(i) + "</a>, size: " + str(round(size/1024,4)) +" KiB </p>\n\t"
  html_content = html_content + """<br><br><a href=\"/\">Go to index</a></p><br></body>\n\t</html>"""
  return html_content
  
@app.route('/stderrout/<filename>', methods=['GET'])
def download_stdXFile(filename):
  return send_from_directory(app.config['RESULTS_FOLDER'], filename, as_attachment=False)

'''
#To serve files created by scripts in local dir (not easy, not fixed, yet)
@app.route('/results', methods=['GET'])
def get_Results():
  dirs = os.listdir(RESULTS_DIR)
  html_content = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
      <title>Result files</title>
      <meta http-equiv="content-type" content="text/html;charset=utf-8" />
      <meta name="generator" content="Geany 1.26" />
    </head>
    <body>
      <h1>RESULT FILES</h1>\n\t"""
  for i in dirs:
    size = os.path.getsize(RESULTS_DIR + i)
    print( str(i) +", size: ", size)
    html_content = html_content + "\t<p><a href=\"" + RESULTS_DIR + str(i) + "\">" + str(i) + "</a>, size: " + str(round(size/1024,4)) +" KiB </p>\n\t"
  html_content = html_content + """<br><br><a href=\"/\">Go to index</a></p><br></body>\n\t</html>"""
  return html_content
  
@app.route('/src_scripts/results/<filename>')
def download_ResultsX(filename):
  return send_from_directory(app.config['RESULTS_FOLDER'], RESULTS_DIR + filename, as_attachment=True)
'''

def getKPITaks(df):
  return df.describe().loc[['count']]

def getKPITimestampedScripts(df):
  return df[['timestamp','script']]
  
def getKPISizeAfterRuns(df):
  return df[['space','script']]

def getKPIs(date):
  df = pd.read_csv(KPIS_DIR+date, names=["timestamp","script","space"])
  return df

@app.route('/kpi', methods=['GET'])
def kpis():
  dirs = os.listdir(KPIS_DIR)
  html_content = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
      <title>KPIs list by date</title>
      <meta http-equiv="content-type" content="text/html;charset=utf-8" />
      <meta name="generator" content="Geany 1.26" />
    </head>
    <body>
      <h1>KPIs by date</h1>\n\t"""
  
  for i in dirs:
    html_content = html_content + "\t<p><a href=\"" + KPIS + str(i)[:-4] + "\">" + str(i)[:-4] + "</a></p>\n\t"
  html_content = html_content + """<br><br><a href=\"/\">Go to index</a></p><br></body>\n\t</html>"""
  return html_content

@app.route('/kpis/<date_file>', methods=['GET'])
def kpisDetailDay(date_file):
  html_content = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
      <title>KPIs list by date: """ + date_file + """</title>
      <meta http-equiv="content-type" content="text/html;charset=utf-8" />
      <meta name="generator" content="Geany 1.26" />
    </head>
    <body>
      <h1>KPIs by date: """ + date_file + """</h1>\n\t"""
      
  df = getKPIs(date_file + ".log")
  
  count = str(getKPITaks(df)).replace("space\ncount ","").replace(".0","")
  html_content = html_content + "<h2>Executed tasks</h2><p>" + count + "</p>"
  
  size_after_runs = getKPISizeAfterRuns(df)
  html_content = html_content + "<h2>Free space after runs</h2>"
  html_content = html_content + "<table style=\"width:100%\">"
  html_content = html_content + "<tr>"
  html_content = html_content + "<th>GiB free</th>"
  html_content = html_content + "<th>Script run</th>"
  html_content = html_content + "</tr>"
  for index,row in size_after_runs.iterrows():
    html_content = html_content + "<tr>"
    html_content = html_content + "<th>" + str(row['space']) + "</th>"
    html_content = html_content + "<th>" + str(row['script']) + "</th>"
    html_content = html_content + "</tr>"
  html_content = html_content + "</table>"
  
  runs = getKPITimestampedScripts(df)
  html_content = html_content + "<h2>Run log</h2>"
  html_content = html_content + "<table style=\"width:100%\">"
  html_content = html_content + "<tr>"
  html_content = html_content + "<th>Timestamp</th>"
  html_content = html_content + "<th>Script run</th>"
  html_content = html_content + "</tr>"
  for index,row in runs.iterrows():
    html_content = html_content + "<tr>"
    html_content = html_content + "<th>" + str(row['timestamp']) + "</th>"
    html_content = html_content + "<th>" + str(row['script']) + "</th>"
    html_content = html_content + "</tr>"
  html_content = html_content + "</table>"
    
  html_content = html_content + """<br><br><a href=\"/\">Go to index</a></p><br>
  </body>\n\t</html>"""
  return html_content

