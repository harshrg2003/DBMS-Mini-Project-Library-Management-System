from flask import Flask,render_template,request,session,redirect,url_for,flash, jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,logout_user,login_manager,LoginManager,login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import date
from sqlalchemy import text as stmt_text
import json
with open("C:\\Users\\admin\\Desktop\\DBMS Project\\dev.json","r") as f:
     device_data=json.load(f)
from sqlalchemy.exc import SQLAlchemyError


local_server=True
app=Flask(__name__)
app.secret_key=device_data["mysql_pass"]

login_manager=LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
     return LibraryMember.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']=device_data['mysql_url']
db=SQLAlchemy(app)

#used to define db models

class Book(db.Model):
     Book_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     Title=db.Column(db.String(200),nullable=False)
     Edition=db.Column(db.Integer)
     Available=db.Column(db.Boolean,default=True)
     Publisher_id=db.Column(db.Integer,db.ForeignKey("publisher.Publisher_id"))
     genres=db.relationship("Genre",secondary="book_genre",back_populates="books")
     authors = db.relationship("Author", secondary="written_by",back_populates="books")

class Author(db.Model):
     Author_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     Author_name=db.Column(db.String(200))
     books = db.relationship("Book", secondary="written_by", back_populates="authors")

class Publisher(db.Model):
     Publisher_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     Publisher_name=db.Column(db.String(200))
     Publisher_phone=db.Column(db.String(20))
     Publisher_address=db.Column(db.String(200))

class LibraryMember(db.Model,UserMixin):
     Member_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     Fname=db.Column(db.String(30),nullable=False)
     Mname=db.Column(db.String(30))
     Lname=db.Column(db.String(30))
     Membership_level=db.Column(db.Integer,default=1)
     Books_taken=db.Column(db.Integer,default=0)
     address=db.relationship("MemberAddress",uselist=False,back_populates="member")
     emails=db.relationship("MemberEmail",back_populates="member")
     phones=db.relationship("MemberPhoneNumber",back_populates="member")
     user_cred = db.relationship('UserCred', back_populates='member')

class BorrowedBy(db.Model):
     Transaction_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
     Due_date=db.Column(db.Date)
     Borrowing_date=db.Column(db.Date)
     Book_id=db.Column(db.Integer,db.ForeignKey("book.Book_id"))
     Member_id=db.Column(db.Integer,db.ForeignKey("library_member.Member_id"))
     returned=db.Column(db.Boolean,default=False)

class WrittenBy(db.Model):
     Author_id=db.Column(db.Integer,db.ForeignKey("author.Author_id"),primary_key=True)
     Book_id=db.Column(db.Integer,db.ForeignKey("book.Book_id"),primary_key=True)

class Genre(db.Model):
     Genre_id=db.Column(db.Integer,primary_key=True)
     Genre_name=db.Column(db.String(30))
     books=db.relationship("Book",secondary="book_genre")

class BookGenre(db.Model):
     Book_id=db.Column(db.Integer,db.ForeignKey("book.Book_id"),primary_key=True)
     Genre_id=db.Column(db.Integer,db.ForeignKey("genre.Genre_id"),primary_key=True)

class MemberAddress(db.Model):
     Member_id=db.Column(db.Integer,db.ForeignKey("library_member.Member_id"),primary_key=True)
     address=db.Column(db.String(200),primary_key=True)
     member=db.relationship("LibraryMember",back_populates="address")

class MemberEmail(db.Model):
     Member_id=db.Column(db.Integer,db.ForeignKey("library_member.Member_id"),primary_key=True)
     email=db.Column(db.String(70),primary_key=True)
     member=db.relationship("LibraryMember",back_populates="emails")

class MemberPhoneNumber(db.Model):
     Member_id=db.Column(db.Integer,db.ForeignKey("library_member.Member_id"),primary_key=True)
     phone=db.Column(db.String(15),primary_key=True)
     member=db.relationship("LibraryMember",back_populates="phones")

class UserCred(db.Model,UserMixin):
     id=db.Column(db.Integer,db.ForeignKey("library_member.Member_id"),primary_key=True)
     user_name=db.Column(db.String(30),unique=True,nullable=False)
     last_login=db.Column(db.Date,default=(2000,1,1))
     password=db.Column(db.String(30))
     member=db.relationship("LibraryMember",back_populates="user_cred")

class Test(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     name=db.Column(db.String(30))
     password=db.Column(db.String(1000))

        

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/home")
def home():
     return render_template("index.html")

@app.route("/LoginForm",methods=["POST","GET"])
def login():
     if request.method=="POST":
          username = request.form.get("username")
          password = request.form.get("password")
          # Query UserCred to get the associated LibraryMember
          user = UserCred.query.filter_by(user_name=username).first()
          print(user) 
          if user and user.password==password:
               member=user.member
               fname=member.Fname 
               mname=member.Mname
               lname=member.Lname
               print("Login Successful!")
               # flash("Login Successful!", "success")
               # output=render_template("dashboard.html",fname=fname,mname=mname,lname=lname)
               output=dashboardpg(fname=fname,mname=mname,lname=lname,level=1,Mid=user.id)
               resp=make_response(output)
               resp.set_cookie("username",username) 
               resp.set_cookie("Member_id",str(user.id)) 
               resp.set_cookie("user_level","Member") 
               login_user(user)
               return resp
          else:
               print("Invalid credentials. Try again")
               flash("Invalid credentials. Try again", "error")
               print(f"Debugging: User: {username}, Password: {password}")

     return render_template("LoginForm.html")
     
    

@app.route("/signup",methods=["POST","GET"])
def signup():
     if request.method=="POST":
          username = request.form.get("username")
          password = request.form.get("password")
          if UserCred.query.filter_by(user_name=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template("signup.html")
        
          fullnames=username.split(" ")
          fname=fullnames[0]
          mname=fullnames[1] if len(fullnames)>1 else ""
          lname=fullnames[2] if len(fullnames)>1 else ""
          new_member = LibraryMember(Fname=fname, Mname=mname, Lname=lname)
          db.session.add(new_member)
          db.session.commit()

        # Create a new UserCred and associate it with the LibraryMember
          last_login_date = date.today()
           #encry_password = generate_password_hash(password,method='scrypt')
          new_user = UserCred(user_name=username, last_login=last_login_date, password=password, member=new_member)
          db.session.add(new_user)
          db.session.commit()

          login_user(new_user)

          flash('Account created successfully. You can now log in.', 'success')
          return redirect(url_for('login'))

          
            
     return render_template("signup.html")

@app.route("/admin",methods=["POST","GET"])
def adminlogin():
     if request.method=="POST":
          username = request.form.get("ID")
          password = request.form.get("password")
          if username=="Admin" and password=="root123":
               print("Login Successful!")
               output=dashboardpg(fname="Administrator",mname="",lname="",level=2)
               resp=make_response(output)
               resp.set_cookie("username","Administator") 
               resp.set_cookie("user_level","Admin") 
               return resp
          else:
               print(f"Debugging: User: {username}, Password: {password}")
     return render_template("adminLogin.html")

@app.route("/dashboard")
def dashboardpg(fname="",mname="",lname="",level=None,Mid=None):
     user_level=request.cookies.get('user_level')
     total_books=db.session.execute(stmt_text("select count(*) from book")).scalar_one()
     if level is None and (user_level is None or user_level=="Guest"):
          return render_template("dashboard.html",fname="Guest",total_books=total_books)
     elif user_level=="Member" or level==1:
          username=request.cookies.get('username')
          member_id=request.cookies.get("Member_id")
          if username is None:
               if Mid is None:
                    return render_template("dashboard.html",user_name=" ",is_admin=False,fname=fname+" ",mname=mname+" ",lname=lname,total_books=total_books)
               member_id=Mid
          borrowed_books=db.session.execute(stmt_text(f"select books_taken from library_member where member_id={member_id}")).scalar_one()
          Beyond_due_date=db.session.execute(stmt_text(f"select count(*) from borrowed_by where Member_id={member_id} and returned=0 and Due_date<curdate()")).scalar_one()
          membership_level=db.session.execute(stmt_text(f"select Membership_level M from library_member where Member_id={member_id}")).scalar_one()
          result=db.session.execute(stmt_text(f"select fname,mname,lname from library_member where Member_id={member_id}")).first()
          fname=result.fname
          mname=result.mname
          lname=result.lname
          return render_template("dashboard.html",user_name=username,is_admin=False,fname=fname+" ",mname=mname+" ",lname=lname,membership_level=membership_level,total_books=total_books,borrowed_books=borrowed_books,beyond_due_date=Beyond_due_date)
     elif user_level=="Admin" or level==2:
          borrowed_books=db.session.execute(stmt_text("select count(*) from borrowed_by where returned=0")).scalar_one()
          Beyond_due_date=db.session.execute(stmt_text("select count(*) from borrowed_by where returned=0 and Due_date<curdate()")).scalar_one()
          total_members=db.session.execute(stmt_text("select count(*) from library_member")).scalar_one()
          return render_template("dashboard.html",user_name="Administrator",fname="Administrator",is_admin=True,total_books=total_books,borrowed_books=borrowed_books,beyond_due_date=Beyond_due_date,total_members=total_members)
     return render_template("dashboard.html",is_admin=False,total_books=total_books)

@app.route("/books",methods=['GET',"POST"])
def books():
     page=0
     if request.method =='GET':
          page=request.form.get("page")
          if not page:
               page=0
          # print("page",page)
     elif request.method=="POST":
          data=request.form.get("change_type")
          if (data=="Book_Delete"):
               book_id=request.form.get("Book_id")
               try:
                    db.session.execute(stmt_text("Delete from book B where B.Book_id=%r"%book_id))
                    db.session.commit()
               except:
                    print("failed")
               print("Attempt to delete book of id",book_id)
          elif (data=="Book_Edit"):
               book_id=request.form.get("Book_id")
               book_title=request.form.get("Book_title")
               book_authors_list=request.form.get("Book_authors").split(',')
               book_authors=[]
               for each in book_authors_list:
                    if each.strip()=="":
                         continue
                    else:
                         book_authors.append(each.strip())
               book_available=request.form.get("Book_available")
               book_edition=request.form.get("Book_edition")
               book_genres=request.form.get("Book_genres")
               try:
                    for each in book_authors:
                         temp=db.session.execute(stmt_text(f"select Author_id from author where Author_name=\"{each}\""))  
                         is_new=True
                         for row in temp:
                              is_new=False
                         if is_new:
                              db.session.execute(stmt_text(f"insert into author(Author_name) values ('{each}')"))
                    temp=db.session.execute(stmt_text(f"select A.Author_name name,A.Author_id id from author A,written_by W where W.Author_id=A.Author_id and W.Book_id={book_id}"))
                    for row in temp:
                         # print(row.name)
                         to_be_deleted=True
                         for single_name in book_authors:
                              if row.name.lower()==single_name.lower():
                                   to_be_deleted=False
                                   break
                         if to_be_deleted:
                              db.session.execute(stmt_text(f"delete from written_by where Book_id={book_id} and Author_id={row.id}"))
                    # print("flag")
                    for each in book_authors:
                         temp=db.session.execute(stmt_text(f"select A.author_id Aid from author A where A.author_name=\"{each}\" and not exists(select * from written_by W where W.book_id={book_id} and W.author_id=A.author_id)"))
                         for row in temp:
                              db.session.execute(stmt_text(f"insert into written_by(book_id,Author_id) values ({book_id},{row.Aid})"))
                    db.session.execute(stmt_text(f"update book set Title=\"{book_title}\", Edition={book_edition}, Available={book_available} where Book_id={book_id};"))
                    genre_ids=tuple(int(id) for id in book_genres.split(','))
                    db.session.execute(stmt_text(f"delete from book_genre B where B.book_id={book_id} and genre_id not in(-1,-2{',' if book_genres!='' else ''}{book_genres})"))
                    temp=db.session.execute(stmt_text(f"select genre_id from book_genre where book_id={book_id} "))
                    genres=[row.genre_id for row in temp]
                    for genre in genre_ids:
                         if genre not in genres:
                              db.session.execute(stmt_text(f"insert into book_genre (book_id,genre_id) values({book_id},{genre})"))
                    db.session.commit()
               except Exception as e:
                    print(e)
               # print("_"*8)
               # print("editing",book_id)
               # print("editing",book_title)
               # print("editing",book_authors)
               # print("editing",book_available)
               # print("editing",book_edition)
               # print("editing",book_genres)
     result=db.session.execute(stmt_text(f"select Book_id,Title,Edition,Available from book where Book_id>{page} limit 10"))
     data=[]
     for row in result:
          temp_data={"Book_id":row.Book_id,"Title":row.Title,"Edition":row.Edition,"Available":row.Available,"Authors":[]}
          temp_var=db.session.execute(stmt_text("select A.Author_name author from author A,written_by W where A.Author_id=W.Author_id and W.Book_id=%r"%row.Book_id))
          # print(row.Book_id,[row.author for row in temp_var])
          temp_data["Authors"]=[row2.author for row2 in temp_var]
          temp_var=db.session.execute(stmt_text("select G.genre_name from genre G, book_genre B where G.genre_id=B.genre_id and B.Book_id=%r order by B.Book_id"%row.Book_id))
          # for each in temp_var:
          #      print(each)
          # print(row.Book_id,[row.author for row in temp_var])
          temp_data["Genre"]=[row2.genre_name for row2 in temp_var]
          # print(temp_data)
          data.append(temp_data)
     genre_data=[]
     result=db.session.execute(stmt_text("select genre_id,genre_name from Genre"))
     for row in result:
          temp_data=[row.genre_id,row.genre_name]
          genre_data.append(temp_data)
     search_title=request.form.get("book_search")
     if search_title is not None:
          data=search_books_by_title(search_title)
     return render_template("books.html",Books=data,AllGenre=genre_data,is_admin=detected_as_admin())

@app.route("/addbook",methods=['GET','POST'])
def addbook():
     if request.method=="POST":
          if request.cookies.get("user_level")=="Admin":
               Booktitle = request.form.get("Booktitle")
               BookEdition = request.form.get("BookEdition")
               Availablity = request.form.get("Availablity")
               Genre_name = request.form.get("Genre")  # Use a different variable name
               Available = True if Availablity == 'Available' else False

               genre = Genre.query.filter_by(Genre_name=Genre_name).first()
               # print(genre)
               if genre:
                    book = Book(Title=Booktitle, Edition=BookEdition, Available=Available, genres=[genre])
               else:
                    book = Book(Title=Booktitle, Edition=BookEdition, Available=Available)
                    
               db.session.add(book)
               db.session.commit()
               return redirect(url_for("books"))
          else:
               return make_response("Insufficient Authorisation")


     if request.cookies.get("user_level")=="Admin":
          return render_template("addbook.html")
     else:
          return make_response("Insufficient Authorisation")



@app.route("/logout")
def logout():
     username = request.cookies.get("username")

    # Expire the username cookie by setting its expiration date to the past
     response = make_response(render_template("LoginForm.html"))
     response.set_cookie("username", "", expires=0)
     response.set_cookie("user_level", "Guest")
     response.set_cookie("Member_id", "",expires=0)

    # Add a flash message for the user
     if request.cookies.get("user_level")=="Member":
          flash(f"You have been successfully logged out, {username}!", "success")

     # Print a message to the console
          print(f"User {username} logged out successfully.")

     # Redirect to the login page
          return response
     elif request.cookies.get("user_level")=="Admin":
          flash(f"You have been successfully logged out, Administrator!", "success")
          print(f"Admin logged out successfully.")
          return response
     return redirect(url_for("login"))


@app.route("/issuebook",methods=['POST',"GET"])
def issuebook():
     if request.method=="POST":
          if request.cookies.get("user_level")=="Member":
               if request.form.get("change_type")=="Book_Borrow":
                    try:
                         db.session.execute(stmt_text(f"insert into borrowed_by(Book_id,Member_id) values({request.form.get('Book_id')},{request.form.get('Member_id')})"))
                         db.session.commit()
                    except Exception as e:
                         print(e)
          elif request.cookies.get("user_level")=="Admin":
               if request.form.get("change_type")=="Book_Return":
                    try:
                         db.session.execute(stmt_text(f"update borrowed_by set returned=true where Transaction_id={request.form.get('Transaction_id')}"))
                         db.session.commit()
                    except Exception as e:
                         print(e)
          return render_template("books.html")
     elif request.method=="GET":
          search_title=request.args.get("book_search")
          if request.cookies.get("user_level")=="Member":
               result=db.session.execute(stmt_text("select Book_id,Title,Edition from book where Available=true limit 10"))
               data=[]
               for row in result:
                    temp_data={"Book_id":row.Book_id,"Title":row.Title,"Edition":row.Edition,"Authors":[]}
                    temp_var=db.session.execute(stmt_text("select A.Author_name author from author A,written_by W where A.Author_id=W.Author_id and W.Book_id=%r"%row.Book_id))
                    temp_data["Authors"]=[row2.author for row2 in temp_var]
                    temp_var=db.session.execute(stmt_text("select G.genre_name from genre G, book_genre B where G.genre_id=B.genre_id and B.Book_id=%r order by B.Book_id"%row.Book_id))
                    temp_data["Genre"]=[row2.genre_name for row2 in temp_var]
                    data.append(temp_data)
               genre_data=[]
               result=db.session.execute(stmt_text("select genre_id,genre_name from Genre"))
               for row in result:
                    temp_data=[row.genre_id,row.genre_name]
                    genre_data.append(temp_data)
               member_id=request.cookies.get("Member_id")
               borrowable=False
               Borrowed_Books=[]
               if member_id:
                    borrowable=db.session.execute(stmt_text(f"select Can_Borrow({member_id}) ")).scalar()==1
                    result=db.session.execute(stmt_text(f"select Book_id,Title,Edition from book where Book_id in(select B.Book_id from borrowed_by B where B.returned=false and B.Member_id={member_id})"))
                    for row in result:
                         temp_data={"Book_id":row.Book_id,"Title":row.Title,"Edition":row.Edition,"Authors":[]}
                         temp_var=db.session.execute(stmt_text("select A.Author_name author from author A,written_by W where A.Author_id=W.Author_id and W.Book_id=%r"%row.Book_id))
                         temp_data["Authors"]=[row2.author for row2 in temp_var]
                         temp_var=db.session.execute(stmt_text("select G.genre_name from genre G, book_genre B where G.genre_id=B.genre_id and B.Book_id=%r order by B.Book_id"%row.Book_id))
                         temp_data["Genre"]=[row2.genre_name for row2 in temp_var]
                         temp_data["Borrow_Date"]=db.session.execute(stmt_text(f"select Borrowing_date from borrowed_by where Book_id={row.Book_id} and member_id={member_id} and returned=false")).scalar()
                         temp_data["Due"]=db.session.execute(stmt_text(f"select datediff(due_date,curdate()) from borrowed_by where Book_id={row.Book_id} and member_id={member_id} and returned=false")).scalar()
                         Borrowed_Books.append(temp_data)
               if search_title is not None:
                    newdata=search_books_by_title(search_title)
                    data=[]
                    for each in newdata:
                         if each['Available']==1:
                              data.append(each)
               return render_template("issuebook.html",page_type="Borrowing",Books=data,borrowable=borrowable,Member_id=member_id,Borrowed_Books=Borrowed_Books)
          elif request.cookies.get("user_level")=="Admin":
               result=db.session.execute(stmt_text("select B.Book_id,B.Title,M.Fname,M.Mname,M.Lname,R.Due_date,R.Borrowing_date,R.Transaction_id from book B,library_member M,borrowed_by R where R.Book_id=B.Book_id and R.Member_id=M.Member_id and R.returned=False limit 10"))
               data=[]
               for row in result:
                    temp_data={"Book":row.Title,"Member":f"{row.Fname} {row.Mname} {row.Lname}","Borrow_Date":row.Borrowing_date,"Due_Date":row.Due_date,"Transaction_id":row.Transaction_id}
                    temp_var=db.session.execute(stmt_text("select A.Author_name author from author A,written_by W where A.Author_id=W.Author_id and W.Book_id=%r"%row.Book_id))
                    temp_data["Authors"]=[row2.author for row2 in temp_var]
                    temp_var=db.session.execute(stmt_text("select G.genre_name from genre G, book_genre B where G.genre_id=B.genre_id and B.Book_id=%r order by B.Book_id"%row.Book_id))
                    temp_data["Genre"]=[row2.genre_name for row2 in temp_var]
                    data.append(temp_data)
               return render_template("issuebook.html",page_type="Returning",Borrow_books=data)
          return render_template("books.html")
          
     


@app.route("/test")
def test():
      try:
           Test.query.all()
           print(search_books_by_title("War and Peace"))
           return "My Database is connected"
      except:
           return "My database is not connected"


def detected_as_admin():
     return request.cookies.get('user_level')=="Admin"

def search_books_by_title(title):
    query = """
    SELECT B.Book_id, B.Title, B.Edition, B.Available, 
           GROUP_CONCAT(DISTINCT G.genre_name) AS genres, 
           GROUP_CONCAT(DISTINCT A.Author_name) AS authors
    FROM book B
    LEFT JOIN book_genre BG ON B.Book_id = BG.Book_id
    LEFT JOIN genre G ON BG.genre_id = G.genre_id
    LEFT JOIN written_by WB ON B.Book_id = WB.Book_id
    LEFT JOIN author A ON WB.Author_id = A.Author_id
    WHERE B.Title LIKE :title
    GROUP BY B.Book_id;
    """
    result = db.session.execute(stmt_text(query), {"title": f"%{title}%"})

    books = []
    for row in result:
        book_info = {
            "Book_id": row.Book_id,
            "Title": row.Title,
            "Edition": row.Edition,
            "Available": row.Available,
            "Genre": row.genres.split(",") if row.genres else [],
            "Authors": row.authors.split(",") if row.authors else [],
        }
        books.append(book_info)

    return books

app.run(debug=True)