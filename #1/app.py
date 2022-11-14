import os
from flask import *
from flask_sqlalchemy import *
curr_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(curr_dir, "database.sqlite3")
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
        
        l = request.form.getlist('courses')

        val = {"course_1": 1, "course_2": 2, "course_3": 3, "course_4":4}
        if "course_1" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a1 = Enrollments(es_id.student_id, val["course_1"])
            db.session.add(a1)
            db.session.commit()
        if "course_2" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a2 = Enrollments(es_id.student_id, val["course_2"])
            db.session.add(a2)
            db.session.commit()
        if "course_3" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a3 = Enrollments(es_id.student_id, val["course_3"])
            db.session.add(a3)
            db.session.commit()
        if "course_4" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a4 = Enrollments(es_id.student_id, val["course_4"])
            db.session.add(a4)
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
    return render_template("enroll.html", x = x, final = final, len = len(final))


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
        enrol = Enrollments.query.filter_by(estudent_id = user.student_id).all()
        for i in enrol:
            Enrollments.query.filter_by(estudent_id = user.student_id).delete()
            db.session.commit()

        l = request.form.getlist('courses')
        roll = user.roll_number
        val = {"course_1": 1, "course_2": 2, "course_3": 3, "course_4":4}
        if "course_1" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a1 = Enrollments(es_id.student_id, val["course_1"])
            db.session.add(a1)
            db.session.commit()
        if "course_2" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a2 = Enrollments(es_id.student_id, val["course_2"])
            db.session.add(a2)
            db.session.commit()
        if "course_3" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a3 = Enrollments(es_id.student_id, val["course_3"])
            db.session.add(a3)
            db.session.commit()
        if "course_4" in l:
            es_id = Student.query.filter_by(roll_number = roll).first()
            a4 = Enrollments(es_id.student_id, val["course_4"])
            db.session.add(a4)
            db.session.commit()

        f_name = request.form["f_name"]
        l_name = request.form["l_name"]
        
        user.first_name = f_name
        user.last_name = l_name
        db.session.commit()
        return redirect(url_for('home'))

    x = Student.query.filter_by(student_id = student_id).first()
    return render_template("update_form.html", curr_rol = x.roll_number, current_f_name = x.first_name, current_l_name = x.last_name)

if __name__ == '__main__': 
    app.run()