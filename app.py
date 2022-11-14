import os
from flask import *
from flask_sqlalchemy import *

curr_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(curr_dir, "database.sqlite3")
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + "database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)

    def __init__(self, course_name, course_code, course_description):
        self.course_code = course_code
        self.course_name = course_name
        self.course_description = course_description

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)

    def __init__(self, roll, f_name, l_name):
        self.roll_number = roll
        self.first_name = f_name
        self.last_name = l_name

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), primary_key = True, nullable = False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), primary_key = True, nullable = False)

    def __init__(self, es_id, ec_id):
        self.estudent_id = es_id
        self.ecourse_id = ec_id


@app.route("/", methods = ["POST", "GET"])

def home():
    student = Student.query.all()
    length = len(student)
    if(length == 0):
        return render_template("home_empty.html")
    else:
        return render_template("index.html", student = student, length = length)


@app.route("/student/create", methods = ["POST", "GET"])
def form():
    if request.method == "POST":
        roll = request.form["roll"]
        f_name = request.form["f_name"]
        l_name = request.form["l_name"]
        student = Student.query.filter_by(roll_number = roll).first()

        if student:
            return render_template("error.html")
            
        stmt = Student(roll, f_name, l_name)
        db.session.add(stmt)
        db.session.commit()        

        return redirect(url_for('home'))

    else:
        return render_template("form.html")
    

@app.route("/student/<student_id>")
def enroll_list(student_id):
    x = Student.query.filter_by(student_id = student_id).first()
    l = Enrollments.query.filter_by(estudent_id = student_id).all()
    final = []
    for i in l:
        final += Course.query.filter_by(course_id = i.ecourse_id).all()
    return render_template("enroll.html", x = x, final = final, len = len(final), student_id = student_id)


@app.route("/student/<student_id>/delete")
def delete(student_id):
    user = Student.query.filter_by(student_id=student_id).first()
    enrol = Enrollments.query.filter_by(estudent_id = user.student_id).all()
    for i in enrol:
        Enrollments.query.filter_by(estudent_id = user.student_id).delete()
        db.session.commit()
    user = Student.query.filter_by(student_id=student_id).delete()
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/student/<student_id>/update", methods = ["POST", "GET"])
def update(student_id):
    if request.method == "POST":
        user = Student.query.filter_by(student_id=student_id).first()
        enrol = Enrollments.query.filter(Enrollments.estudent_id == student_id).filter(Enrollments.ecourse_id == request.form.get('course')).all()

        if enrol != []:
            f_name = request.form["f_name"]
            l_name = request.form["l_name"]
            user.first_name = f_name
            user.last_name = l_name 
            db.session.commit()
            return redirect(url_for('home'))

        else:
            enrol = Enrollments(es_id = student_id, ec_id = request.form.get('course'))
            db.session.add(enrol)

            f_name = request.form["f_name"]
            l_name = request.form["l_name"]
            
            user.first_name = f_name
            user.last_name = l_name
            db.session.commit()
            return redirect(url_for('home'))

    x = Student.query.filter_by(student_id = student_id).first()
    courses_list = Course.query.all()
    len_course_list = len(courses_list)
    return render_template("update_form.html", curr_rol = x.roll_number, current_f_name = x.first_name, current_l_name = x.last_name, courses_list = courses_list, len_course_list = len_course_list)


@app.route("/student/<student_id>/withdraw/<course_id>")
def withdraw(student_id, course_id):
    enrolls = Enrollments.query.filter(
            Enrollments.estudent_id == student_id).filter(Enrollments.ecourse_id == course_id
        ).all()
    for enroll in enrolls:
            db.session.delete(enroll)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/courses")
def display_courses():
    courses = Course.query.all()
    length = len(courses)
    if(length == 0):
        return render_template("course_empty.html")
    else:
        return render_template("display_courses.html", student = courses, length = length)

@app.route("/course/create", methods = ["POST", "GET"])
def course_form():
    if request.method == "POST":
        course_code = request.form["code"]
        course_name = request.form["c_name"]
        course_desc = request.form["desc"]
        student = Course.query.filter_by(course_code = course_code).first()

        if student:
            return render_template("course_error.html")
            
        stmt = Course(course_name=course_name, course_code=course_code, course_description=course_desc)
        db.session.add(stmt)
        db.session.commit()        

        return redirect(url_for('display_courses'))

    else:
        return render_template("course_form.html")

@app.route("/course/<course_id>/update", methods = ["POST", "GET"])
def course_update(course_id):
    if request.method == "POST":
        course = Course.query.filter_by(course_id=course_id).first()

        c_name = request.form["c_name"]
        desc = request.form["desc"]
        
        course.course_name = c_name
        course.course_description = desc
        db.session.commit()
        return redirect(url_for('display_courses'))
    
    x = Course.query.filter_by(course_id = course_id).first()
    
    return render_template("course_update_form.html", current_code = course_id, x =x)

@app.route("/course/<course_id>/delete")
def course_delete(course_id):
    enrol = Enrollments.query.filter_by(ecourse_id = course_id).all()
    for i in enrol:
        Enrollments.query.filter_by(ecourse_id = course_id).delete()
        db.session.commit()
    user = Course.query.filter_by(course_id=course_id).delete()
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/course/<course_id>")
def display_course_enrol(course_id):
    x = Course.query.filter_by(course_id = course_id).first()
    l = Enrollments.query.filter_by(ecourse_id = course_id).all()
    final = []
    for i in l:
        final += Student.query.filter_by(student_id = i.estudent_id).all()
    length = len(final)

    return render_template("course_detail_display.html", x = x, final = final, length = length)

if __name__ == '__main__': 
    app.run()
