from flask import Flask,url_for,render_template,request,redirect,jsonify,session,flash
import os
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context #for password validation
from helpers import bfulSoup,sendmail
import datetime

app=Flask(__name__)

app.config['SECRET_KEY']="1234"
db=SQL("sqlite:///database.db")


@app.route('/',methods=['GET','POST'])
def home_page():
    if request.method=='POST':
        db.execute("INSERT INTO feedback VALUES (:x,:t)",x=request.form["feedback"],t=datetime.datetime.now())

        if session.get('email'):        #if user logged in then extend index.html else layout.html
            return render_template('homepage.html',status="logged_in")
        else:
            return render_template('homepage.html',status="logged_out")
    else:
        if session.get('email'):
            return render_template('homepage.html',status="logged_in")
        else:
            return render_template('homepage.html',status="logged_out")






@app.route("/index")
def index():
    return render_template("welcome.html")






@app.route("/register",methods=["GET","POST"])
def register():

    session.clear()

    if request.method=="POST":

        #This is for backend form validation in case javascript fails
        if request.form["email"]=="" or request.form["password"]=="":

            flash( "username or password field(s) left empty")  #flash messages, use cookies
            return redirect( url_for('register') )


        if request.form["password"]!=request.form["confirm"]:

            flash("passwords do not match")
            return redirect( url_for('register') )


        users=db.execute("SELECT email FROM users")


        for i in range(len(users)):
            if request.form["email"]==users[i]["email"]:

                flash('Username already exists')
                return redirect( url_for('register') )

        db.execute("INSERT INTO users (email,password) VALUES (:n,:p)",n=request.form["email"], \

        p=pwd_context.hash(request.form["password"]))   #to store hash of the password in dataabase

        session["email"]=request.form["email"]

        sendmail( session['email'] )

        return redirect(url_for('index'))

    else:
        return render_template("register.html")







@app.route('/login',methods=['GET','POST'])
def login():

    session.clear()

    if request.method=="POST":

        if request.form["email"]=="" or request.form["password"]=="":   #backend form validation

            flash( "One or more fields are blank")

            return render_template('login.html')

        data=db.execute("SELECT password FROM users WHERE email=:name",name=request.form["email"])


        if len(data)!=1 or not pwd_context.verify(request.form["password"],data[0]["password"]):

            flash( "Invalid credentials")

            return render_template('login.html')



        session["email"]=request.form["email"]  #to take email in session

        return redirect(url_for('index'))

    else:
        return render_template('login.html')




@app.route("/search",methods=['GET','POST'])
def search():

    if request.method=='POST':

        if not session.get('email'):
            return redirect(url_for('login'))   #redirects user to login if logged out


        if request.form['query']=='':
            flash('Please enter a query')
            return redirect(url_for('search'))


        db.execute('INSERT INTO history VALUES (:e,:x,:t)',e=session.get('email'),x=request.form['query'],t=datetime.datetime.now())

        contents = bfulSoup(request.form['query'])

        content=contents[0]

        ytd=contents[2] #For youtube link

        with open('templates/results.html','r') as file:
            f=file.read()   #reads from results.html

        i,html=0,''

        session['query']=request.form['query']

        #using beautiful soup and appending the appropriate html

        html="<div id='info'> <br> <a href= ' " + str( ytd ) + " '> <b style='color:DarkGreen;font-size:24px;text-align:center'>Click to see youtube results for your search</b> </a> </div>"

        if len(content)>0 and len(contents[0])>0:

            html+="<br> <div id='info'> <br> <a href= ' " + str( contents[1] ) + " '> <b style='color:DarkGreen;font-size:24px;text-align:center'>Click to see wikipedia results for your search</b> </a> </div><br>"

            html+="<br><br><b style='font-size:22px;color:black;text-align:center'>Some more wiki hits--></b><br><br>"

            for data in content:
                i+=1

                html=html+ "<a id='links' href= ' " + data['href'] + " ' > " + data['title'] + "</a> </br>" #to extract top links and titles from wikipedia

                if i>10: break



        html+="<br> <a href= ' " + str( contents[3] ) + " '> <b style='color:DarkGreen;font-size:24px;text-align:center'>Click to see google results for your search</b> </a> </div>"

        html+=' </body> </html>'

        return f + str(html)     #here html has html parsed content from wikipedia




    else:
        if not session.get('email'):
            return redirect(url_for('login'))

        return render_template("search.html",status="logged_in")







@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))








@app.route('/unregister')
def unregister():

    if session.get('email'):

        db.execute('DELETE FROM users WHERE email=:e',e=session.get('email') )

        db.execute('DELETE FROM history WHERE email=:e',e=session.get('email') )

        db.execute('DELETE FROM notes WHERE email=:e',e=session.get('email') )

        session.clear()

        return redirect(url_for('home_page'))
    else:
        return redirect(url_for('login'))








@app.route('/relax',methods=['GET','POST'])
def relax():

    if request.method=="POST":

        query=request.form["query"]

        url='https://www.youtube.com/results?search_query=' + query

        return redirect(url)

    else:

        if session.get('email'):
            return render_template('relax.html',status="logged_in")
        else:
            return render_template('relax.html',status="logged_out")






@app.route('/results',methods=['GET','POST'])
def results():

    q=session.get('query')

    return render_template('books.html',q=q)









@app.route('/history')
def history():      #to display search history

    if not session.get('email'):
        return redirect(url_for('login'))

    history=db.execute('SELECT query,time FROM history WHERE email=:e',e=session.get('email'))

    return render_template('history.html',h=reversed(history) )






@app.route('/notes',methods=['GET','POST'])
def notes():    #to get and display notes

    if request.method=="POST":

        if not session.get('email'):
            return redirect(url_for('login'))

        if not request.form['notes']=="":

            db.execute('INSERT INTO notes VALUES (:e,:x,:t)',e=session.get('email'),x=request.form['notes'],t=datetime.datetime.now() )

            notes=db.execute('SELECT * FROM notes WHERE email=:e',e=session.get('email'))

        return render_template('notes.html',notes=reversed(notes) ) #newest first

    else:
        if not session.get('email'):
            return redirect(url_for('login'))

        notes=db.execute('SELECT * FROM notes WHERE email=:e',e=session.get('email'))

        return render_template('notes.html',notes=reversed(notes) )








@app.route('/rmv')
def rmv():

    if request.args.get('table')=='notes':  #if it gets called in notes page

        val=request.args.get('val')

        db.execute("DELETE FROM notes WHERE note = :ln",ln=val)

        return redirect(url_for('notes'))

    else:
        val=request.args.get('val') #if it gets called in history page

        db.execute("DELETE FROM history WHERE query = :ln",ln=val)

        return redirect(url_for('history'))








@app.route('/aboutme')
def aboutme():
    if session.get('email'):
        return render_template('aboutme.html',status='logged_in')
    return render_template('aboutme.html',status='logged_out')



if __name__=='__main__':
	Flask.run(app)
