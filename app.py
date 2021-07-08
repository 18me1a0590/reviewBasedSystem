from flask import *
from flask_sqlalchemy import *
from datetime import *
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:gopireddy@localhost/project"
# DATABASE_URL="postgres://bbtxcnrrzdkolb:1a68bc2fa1c1901d344a22e3481bbd33e39aa02327e16d350e6d1acd385d5f6a@ec2-52-5-1-20.compute-1.amazonaws.com:5432/datk6k64lri1r6"
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# postgres://bbtxcnrrzdkolb:1a68bc2fa1c1901d344a22e3481bbd33e39aa02327e16d350e6d1acd385d5f6a@ec2-52-5-1-20.compute-1.amazonaws.com:5432/datk6k64lri1r6
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'thisismykey'
db = SQLAlchemy(app)

#-----------------ML CODE ------------------------------------------------------------

# import pandas as pd
# Reviewdata = pd.read_csv('train.csv')
# count = Reviewdata.isnull().sum().sort_values(ascending=False)
# percentage = ((Reviewdata.isnull().sum()/len(Reviewdata)*100)).sort_values(ascending=False)
# missing_data = pd.concat([count, percentage], axis=1,
# keys=['Count','Percentage'])
# Reviewdata.drop(columns = ['User_ID', 'Browser_Used', 'Device_Used'], inplace = True)
# import re
# import string

# def text_clean_1(text):
#     text = text.lower()
#     text = re.sub('\[.*?\]', '', text)
#     text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
#     text = re.sub('\w*\d\w*', '', text)
#     return text

# cleaned1 = lambda x: text_clean_1(x)
# Reviewdata['cleaned_description'] = pd.DataFrame(Reviewdata.Description.apply(cleaned1))
# def text_clean_2(text):
#     text = re.sub('[‘’“”…]', '', text)
#     text = re.sub('\n', '', text)
#     return text

# cleaned2 = lambda x: text_clean_2(x)
# Reviewdata['cleaned_description_new'] = pd.DataFrame(Reviewdata['cleaned_description'].apply(cleaned2))
# from sklearn.model_selection import train_test_split

# Independent_var = Reviewdata.cleaned_description_new
# Dependent_var = Reviewdata.Is_Response

# a_train, IV_test, DV_train, DV_test = train_test_split(Independent_var, Dependent_var, test_size = 0.1,random_state=225)
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression

# tvec = TfidfVectorizer()
# clf2 = LogisticRegression(solver = "lbfgs")


# from sklearn.pipeline import Pipeline

# model = Pipeline([('vectorizer',tvec),('classifier',clf2)])

# model.fit(a_train, DV_train)


# from sklearn.metrics import confusion_matrix

# predictions = model.predict(IV_test)

# confusion_matrix(predictions, DV_test)

import pickle

# load model
model = pickle.load(open('model.pkl','rb'))

#-------------------------------DATABASE CREATION------------------------------------------------
#-------------------------------TABLE CREATION---------------------------------------------------
class Users(db.Model):
    __tablename__='users'
    user_id = db.Column(db.Integer,primary_key = True)
    date = db.Column(db.Date,default = date.today(),nullable=False)
    user_email =db.Column(db.String(40))
    user_name = db.Column(db.String(40))
    password = db.Column(db.String(20))


class Reviews(db.Model):
    __tablename__='reviews'
    review_id = db.Column(db.Integer,primary_key = True)
    date = db.Column(db.Date,default = date.today(),nullable=False)
    user_name = db.Column(db.String(40))
    review =db.Column(db.String(100))





@app.route("/")
@app.route("/home")
def home():
    return render_template("senti.html")

#----------------------------login system--------------------------------------------------------
@app.route("/adminlogin")
def admin():
     return render_template("admin.html")
@app.route("/adminlogin" , methods = ['POST'])
def adminlogin():  
      uname=request.form['username']  
      passwrd=request.form['password']  
      if uname=="admin" and passwrd=="admin":
          return render_template("adminafterlogin.html")  
      return render_template("admin.html",msg="Username or Password are incorrect !!")

@app.route("/userlogin")
def user():
     return render_template("user.html")
@app.route("/userlogin" , methods = ['POST'])
def userlogin():  
      uname=request.form['username']  
      passwrd=request.form['password']  
      us=Users.query.filter_by(user_name=uname).first()
      if us ==None :
           return render_template("user.html",msg="Username is not found !!",col='warning')
      if us.password==passwrd :
          return render_template("userdashboard.html",user=us)
      return render_template("user.html",msg="Username or Password are incorrect !!",col='warning')

@app.route("/useregister")
def register():
     return render_template("register.html")
@app.route("/useregister" , methods = ['POST'])
def useregister():  
      email=request.form['email']  
      uname=request.form['username']  
      passwrd=request.form['password']  
      confirm=request.form['confirmpassword']  
      if passwrd==confirm :
          us=Users.query.filter_by(user_email=email).first()
          if us==None :
              pro=Users(user_email=email,user_name=uname,password=passwrd)
              db.session.add(pro)
              db.session.commit()
              return render_template("user.html",msg="Your account created successfully plzz login !!",col='success')
          return render_template("register.html",msg=" This Email have already account go to login page !! ",col="warning")  
      return render_template("register.html",msg=" Confirm Password is not same !! ",col="danger")


@app.route("/postcomment" , methods = ['POST'])
def comment():  
      
      uname=request.form['username']
      
      comment=request.form.get('re')  
      com=Reviews(user_name=uname,review=comment)
      db.session.add(com)
      db.session.commit()
      us=Users.query.filter_by(user_name=uname).first()
      return render_template("userdashboard.html",user=us,msg="Review saved Successfully!! Thankyou")
    




@app.route("/admin")
def loggedinadmin():
     return render_template("adminafterlogin.html")

@app.route("/admin/CustmerReviews")
def adminreviews():
     happy=[]
     sad=[]
     users = Reviews.query.all()
     for i in users :
         example = [i.review]
         result = model.predict(example)
         if result==["happy"] :
             happy.append([i.user_name,i.review])
         else :
             sad.append([i.user_name,i.review])
     happy.extend(sad)
     c=len(happy)
     return render_template("admindash.html",count=c,data=happy)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
