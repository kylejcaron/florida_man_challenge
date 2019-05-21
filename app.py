from flask import render_template
from flask import Flask, request, session
from flask_bootstrap import Bootstrap
from dateutil.parser import parse
from fastai import *
from fastai.text import * 
import numpy as np
import pandas as pd
import os
import re
import time
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
import psycopg2 as pg2
from sqlalchemy import create_engine
import pickle
from static.content_filtering_model import Model


app = Flask(__name__)
Bootstrap(app)

POSTGRES = {
    'user': 'your_username',
    'pw': 'your_password',
    'db': 'content_filtering',
    'host': 'content-filtering.xxxxxxxxxx.xxxxxx.rds.amazonaws.com',
    'port': 'xxxx',
}
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

sql_id = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.secret_key = 'xxxxxxxxxx'


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/florida_man', methods=['GET','POST'])
def submission_page():
    if request.method == 'POST':
      label = request.form['options']
      content = session.get('predict_var', None)
      df = pd.DataFrame([[content, label]])
      df.columns = ['headline', 'label']
      
      conn = pg2.connect(dbname = POSTGRES['db'], host = POSTGRES['host'],
         user = POSTGRES['user'], password = POSTGRES['pw'])
      conn.autocommit = True
      engine = create_engine(sql_id)
      df.to_sql("entries", con = engine, if_exists= "append", index=False)
      conn.close()

    page = '''
        <!DOCTYPE html>
    <html lang="en">

    <head>

      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <meta name="description" content="">
      <meta name="author" content="">

      <title>Kyle Caron</title>

      <!-- Bootstrap core CSS -->
      <link href="static/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">

      <!-- Custom fonts for this template -->
      <link href="https://fonts.googleapis.com/css?family=Saira+Extra+Condensed:500,700" rel="stylesheet">
      <link href="https://fonts.googleapis.com/css?family=Muli:400,400i,800,800i" rel="stylesheet">
      <link href="static/vendor/fontawesome-free/css/all.min.css" rel="stylesheet">

      <!-- Custom styles for this template -->
      <link href="static/css/resume.min.css" rel="stylesheet">

      <style>
            p {font-family:Muli; font-size:1rem;}
      </style>


    </head>

    <body id="page-top">

      <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top" id="sideNav">
        <a class="navbar-brand js-scroll-trigger" href="#page-top">
          <span class="d-block d-lg-none">Kyle Caron</span>
          <span class="d-none d-lg-block">
            <img class="img-fluid img-profile rounded-circle mx-auto mb-2" src="static/img/profile2.jpg" alt="">
          </span>
        </a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link js-scroll-trigger" href="/">Home</a>
            </li>
            <li class="nav-item">
              <a class="nav-link js-scroll-trigger" href="#Florida-Man">Florida Man Headlines</a>
            </li>
        
          </ul>
        </div>
      </nav>

      <div class="container-fluid p-0">

        <section class="resume-section p-3 p-lg-5 d-flex justify-content-center" id="Florida-Man">
          <div class="w-100">
            <h1 class="mb-0">Kyle
              <span class="text-primary">Caron</span>
            </h1>
            <div class="subheading mb-5">  Data Scientist · New York, NY · 
              <a href="mailto:name@email.com">kyle.j.caron@gmail.com</a>
            
            <div class="social-icons">
              <a href="http://www.linkedin.com/in/kylecaron">
                <i class="fab fa-linkedin-in"></i>
              </a>
              <a href="http://www.github.com/kylejcaron">
                <i class="fab fa-github"></i>
              </a>
              </div>


        <div class="resume-item d-flex flex-column flex-md-row justify-content-around mb-5">
          <div class="resume-content">
            
            <h3 style="margin-top: 30px; class="mb-20">Florida Man Challenge</h3>
                 <div class="subheading mb-3">Enter your birthday (month, day) below for fake Florida headlines!</div>
                <p> These are Neural Net generated, fictitious Florida Man headlines, based on the popular 
                <a href="https://www.usatoday.com/story/news/nation/2019/03/21/florida-man-challenge-why-do-so-many-crazy-crimes-happen-florida/3240636002/">
                Florida Man Challenge</a>. Please note these may contain offensive content. For more information on how this was generated, 
                check out my blog post on Medium (coming soon).</p>
                <form action="/florida_man_predictions" method='POST' >
                    <input type="text" name="user_input" />
                    <input type="submit" />
                </form>
              </div>
              </div>
            </div>

            </div>
          </div>
        </section>
    </div>

      <!-- Bootstrap core JavaScript -->
      <script src="static/vendor/jquery/jquery.min.js"></script>
      <script src="static/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>

      <!-- Plugin JavaScript -->
      <script src="static/vendor/jquery-easing/jquery.easing.min.js"></script>

      <!-- Custom scripts for this template -->
      <script src="static/js/resume.min.js"></script>

    </body>

    </html>
    '''
    return page


@app.route('/florida_man_predictions', methods=['GET','POST'] )
def class_prediction():
    
    page = '''
            <!DOCTYPE html>
        <html lang="en">

        <head>

          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
          <meta name="description" content="">
          <meta name="author" content="">

          <title>Kyle Caron</title>

          <!-- Bootstrap core CSS -->
          <link href="static/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">

          <!-- Custom fonts for this template -->
          <link href="https://fonts.googleapis.com/css?family=Saira+Extra+Condensed:500,700" rel="stylesheet">
          <link href="https://fonts.googleapis.com/css?family=Muli:400,400i,800,800i" rel="stylesheet">
          <link href="static/vendor/fontawesome-free/css/all.min.css" rel="stylesheet">

          <!-- Custom styles for this template -->
          <link href="static/css/resume.min.css" rel="stylesheet">

          </head>

        <body id="page-top">

          <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top" id="sideNav">
            <a class="navbar-brand js-scroll-trigger" href="#page-top">
              <span class="d-block d-lg-none">Kyle Caron</span>
              <span class="d-none d-lg-block">
                <img class="img-fluid img-profile rounded-circle mx-auto mb-2" src="static/img/profile2.jpg" alt="">
              </span>
            </a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
              <ul class="navbar-nav">
                <li class="nav-item">
                  <a class="nav-link js-scroll-trigger" href="/">Home</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link js-scroll-trigger" href="#Florida-Man">Florida Man Headlines</a>
                </li>
            
              </ul>
            </div>
          </nav>

          <div class="container-fluid p-0">

            <section class="resume-section p-3 p-lg-5 d-flex justify-content-center" id="Florida-Man">
              <div class="w-100">
                <h1 class="mb-0">Kyle
                  <span class="text-primary">Caron</span>
                </h1>
                <div class="subheading mb-5">  Data Scientist · New York, NY · 
                  <a href="mailto:name@email.com">kyle.j.caron@gmail.com</a>
                
                <div class="social-icons">
                  <a href="http://www.linkedin.com/in/kylecaron">
                    <i class="fab fa-linkedin-in"></i>
                  </a>
                  <a href="http://www.github.com/kylejcaron">
                    <i class="fab fa-github"></i>
                  </a>
                  </div>


            <div class="resume-item d-flex flex-column flex-md-row justify-content-around mb-5">
              <div class="resume-content">
                
                <h3 style="margin-top: 30px; class="mb-20">Florida Man Challenge</h3>
                     <div class="subheading mb-3">Enter your birthday (month, day) below for fake Florida headlines!</div>
                    <p style="font-family:Muli; font-size:1rem;"> These are Neural Net generated, fictitious Florida Man 
                    headlines, based on the popular <a href="https://www.usatoday.com/story/news/nation/2019/03/21/florida-man-challenge-why-do-so-many-crazy-crimes-happen-florida/3240636002/"> Florida Man Challenge</a>. Please note these may contain offensive content. 
                    For more information on how this was generated, check out my blog post on Medium (coming soon).</p>
                    
                    <form action="/florida_man_predictions" method='POST' >
                        <input placeholder="enter day and month" type="text" name="user_input" />
                        <input type="submit" />
                    </form>
                  </div>
                  </div>

            <div class="resume-item d-flex flex-column flex-md-row justify-content-around mb-5">
              <div class="resume-content">
                <h3 style="margin-top: 30px; class="mb-20">{}</h3>
                <p style="font-family:Muli; font-size:1rem;"> Disclaimer: many of these headlines 
                    are quite offensive, and unprofessional. What was originally 
                    intended as a light-hearted approach to text-generation ended up creating offensive
                    content. 

                    <br> <br>In an effort to turn this into something positive, please feel free to 
                    indicate if something was too offensive below. Your submissions will be used to 
                    create an offensive content filter. </p>
                </div>
              </div>
                

              {}

              
            </section>
        </div>

          <!-- Bootstrap core JavaScript -->
          <script src="static/vendor/jquery/jquery.min.js"></script>
          <script src="static/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>

          <!-- Plugin JavaScript -->
          <script src="static/vendor/jquery-easing/jquery.easing.min.js"></script>

          <!-- Custom scripts for this template -->
          <script src="static/js/resume.min.js"></script>

        </body>

        </html>
        '''

    radio = '''
      <form name="offensive_content" action="/florida_man" method="POST" onsubmit="">
      <h4>Was this too offensive?</h4>
          <p>
          <input type="radio" name="options" id="Yes" value="Yes"> Yes <br>
          <input type="radio" name="options" id="No" value="No"> No <br>
          <input type="radio" name="options" id="Funny" value="Funny"> No, it was funny <br>
          </p>
          <p><input type=submit value=Submit></p>
          </form>
      '''

    if request.method == 'GET':
      prediction = 'Incorrect Search Terms, please enter proper format (i.e. "Jan 1")'
      radio = ''
      return page.format(str(prediction),radio)

    if request.method == 'POST': 
      # Conditions to ensure input data is properly formatted
      text = [clean_date(str(request.form['user_input']).lower())]
      cond1 = text[0].startswith('florida man ') and is_date(text[0][12:]) #
      cond2 = is_date(text[0])
      
      # if input data is properly formatted:
      if cond1 or cond2:
      	
        # Load data
        with open("static/data/train_df.pkl", "rb") as training:
          train_df = pickle.load(training)
        with open("static/data/valid_df.pkl", "rb") as validation:
          valid_df = pickle.load(validation)
        data_lm = TextLMDataBunch.from_df('data', train_df, valid_df,
                                  text_cols='title')
        learn = language_model_learner(data_lm, AWD_LSTM, drop_mult=0.5)
        # Load Generative Model (FastAI)
        os.chdir('static') # Necessary to work with FastAIs required folder structure
        learn.load_encoder('ml_ft_enc')
        # Load content_filtering model
        with open('data/filtering_model.pkl', 'rb') as f:
          filter_content = pickle.load(f)
        
        # Make prediction
        prediction = learn.predict("florida man", n_words=20, temperature=0.8).split('xxbos')[0]
        # Predict if content is offensive
        offensive = filter_content.predict([prediction])[0]
        # If content is offensive, keep generating predictions until it is not
        while offensive == 1:
          prediction = learn.predict("florida man", n_words=20, temperature=0.8).split('xxbos')[0]
          offensive = filter_content.predict([prediction])[0]
        os.chdir('../') # Necessary to work with FastAIs required folder structure

        session['predict_var'] = prediction
        return page.format(str(prediction), radio)

      else:
        prediction = 'Incorrect Search Terms, please enter proper format (i.e. "Jan 1")'
        radio = ''
        return page.format(str(prediction),radio)
    

def clean_date(str):
    return re.sub('(st|nd|rd|th)', '', str)

def is_date(string, fuzzy=True):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)