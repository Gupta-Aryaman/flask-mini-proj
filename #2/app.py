from importlib.resources import Resource
import os
from flask import *
from flask_sqlalchemy import *
from werkzeug.exceptions import HTTPException
from flask_restful import Api, Resource, marshal_with, reqparse, fields



app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(curr_dir, "database.sqlite3")
db = SQLAlchemy(app)

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

class SchemaValidationError(HTTPException):
    def __init__(self, status_code, error_message):
        data = {"error_message": error_message}
        self.response = make_response(json.dumps(data), status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(data), status_code)


class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)

course_field = {"course_id": fields.Integer,
                "course_name": fields.String,
                "course_code": fields.String,
                "course_description":fields.String}

student_fields = {
    "student_id": fields.Integer,
    "first_name": fields.String,
    "last_name": fields.String,
    "roll_number": fields.String}

course_parser = reqparse.RequestParser()
course_parser.add_argument('course_name', type = str)
course_parser.add_argument('course_code', type = str)
course_parser.add_argument('course_description', type = str)

course_parser2 = reqparse.RequestParser()
course_parser2.add_argument('course_name', type = str)
course_parser2.add_argument('course_code', type = str)
course_parser2.add_argument('course_description', type = str)

create_course_parser = reqparse.RequestParser()
create_course_parser.add_argument("course_name")
create_course_parser.add_argument("course_code")
create_course_parser.add_argument("course_description")

update_student_parser = reqparse.RequestParser()
update_student_parser.add_argument("first_name")
update_student_parser.add_argument("last_name")
update_student_parser.add_argument("roll_number")

create_student_parser = reqparse.RequestParser()
create_student_parser.add_argument("first_name")
create_student_parser.add_argument("last_name")
create_student_parser.add_argument("roll_number")

create_enroll_parser = reqparse.RequestParser()
create_enroll_parser.add_argument("enrollment_id")
create_enroll_parser.add_argument("student_id")
create_enroll_parser.add_argument("course_id")

class OpCourses(Resource):
    def get(self, course_id):
        x = Course.query.filter_by(course_id = course_id).first()
        if x is None:
            raise SchemaValidationError(status_code=404, error_message="Course not found")
        else:
            return {"course_id": course_id, "course_name": x.course_name, "course_code": x.course_code, "course_description": x.course_description}

    def put(self, course_id):
        args = course_parser.parse_args()
        curs_name = args.get("course_name", None)
        curs_code = args.get("course_code", None)
        curs_descr = args.get("course_description", None)

        if curs_name is None or curs_name.isnumeric():
            raise BusinessValidationError(
                status_code=400, error_code="COURSE001", error_message="Course name is required")

        if curs_code is None or curs_code.isnumeric():
            raise BusinessValidationError(
                status_code=400, error_code="COURSE002", error_message="Course code is required")

        if curs_descr is None or curs_descr.isnumeric():
            raise BusinessValidationError(
                status_code=400, error_code="COURSE003", error_message="Course description is required")

        course_data = db.session.query(Course).filter(Course.course_id == course_id).first()

        if course_data is None:
            raise SchemaValidationError(status_code=404, error_message="Course not found")
        
        course_data.course_name = curs_name
        course_data.course_code = curs_code
        course_data.course_description = curs_descr
        # db.session.add(curs_det)
        db.session.commit()
        return {"course_id": course_id, "course_name": course_data.course_name, "course_code":course_data.course_code, "course_description": course_data.course_description}, 200

    def delete(self, course_id):
        curs_det = db.session.query(Course).filter(Course.course_id == course_id).scalar()
        
        if curs_det is None:
            raise SchemaValidationError(status_code=404, error_message="Course not found")

        enrolls = Enrollments.query.filter(Enrollments.ecourse_id == course_id).all()

        for enroll in enrolls:
            db.session.delete(enroll)
        db.session.commit()

        db.session.delete(curs_det)
        db.session.commit()
        return "", 200
    
    @marshal_with(course_field)
    def post(self):
        args = course_parser2.parse_args()
                      
        curs_name = args.get("course_name",None)
        curs_code = args.get("course_code",None)
        curs_descr = args.get("course_description",None)

       
        if curs_name is None or curs_name.isnumeric():
            raise BusinessValidationError(
                status_code=400, error_code="COURSE001", error_message="Course name is required")

        if curs_code is None or curs_code.isnumeric():
            raise BusinessValidationError(
                status_code=400, error_code="COURSE002", error_message="Course code is required")

        curs_det = db.session.query(Course).filter(Course.course_code == curs_code).first()
        if curs_det:
            raise SchemaValidationError(status_code=409, error_message="course_code already exist")

        new_course = Course(course_name=curs_name, course_code=curs_code, course_description= curs_descr)
        db.session.add(new_course)
        db.session.commit()
        return new_course

api.add_resource(OpCourses,"/api/course", "/api/course/<int:course_id>")

class StudentAPI(Resource):
    @marshal_with(student_fields)
    def get(self, student_id):
        # Get the student details from the database
        student = Student.query.filter(
            Student.student_id == student_id).scalar()

        if student:
            # student exists in database, hence return the student object which will be marshalled to json
            return student
        else:
            # Return 404 Error
            raise NotFoundError(status_code=404)

    @marshal_with(student_fields)
    def put(self, student_id):  # Update
        student = Student.query.filter(
            Student.student_id == student_id).scalar()

        if student is None:
            raise NotFoundError(status_code=404)

        # Get the data from request body
        args = update_student_parser.parse_args()
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        roll_number = args.get("roll_number", None)

        if (first_name is None) or (first_name.isnumeric()):
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT002",
                error_message="First Name is required."
            )

        if (roll_number is None) or (roll_number.isnumeric()):
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT001",
                error_message="Roll Number is required."
            )

        
        student.first_name = first_name
        student.last_name = last_name
        student.roll_number = roll_number
        db.session.commit()
        return student

    def delete(self, student_id):
        # check if student exists
        student = Student.query.filter(
            Student.student_id == student_id).scalar()

        if student is None:
            raise NotFoundError(status_code=404)

        enrolls = Enrollments.query.filter(
            Enrollments.estudent_id == student_id).all()

        for enroll in enrolls:
            db.session.delete(enroll)
        db.session.commit()

        db.session.delete(student)
        db.session.commit()
        return "", 200

    @marshal_with(student_fields)
    def post(self):
        # Get the data from request body
        args = update_student_parser.parse_args()
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        roll_number = args.get("roll_number", None)

        student = Student.query.filter(
            Student.roll_number == roll_number).scalar()

        if student != None:
            raise SchemaValidationError(status_code=409, error_message="student already exist")

        if (first_name is None) or (first_name.isnumeric()):
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT002",
                error_message="First Name is required."
            )

        if (roll_number is None) or (roll_number.isnumeric()):
            raise BusinessValidationError(
                status_code=400,
                error_code="STUDENT001",
                error_message="Roll Number is required."
            )

        

        student = Student(f_name=first_name,l_name=last_name,roll=roll_number)

        db.session.add(student)
        db.session.commit()

        return student, 201

    
api.add_resource(StudentAPI, "/api/student", "/api/student/<int:student_id>")


class EnrollmentAPI(Resource):
    def get(self, student_id):
        student = Student.query.filter(
            Student.student_id == student_id).scalar()

        if student is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT002",
                error_message="Invalid Student Id"
            )
        enrolls = Enrollments.query.filter(
            Enrollments.estudent_id == student_id).all()

        if enrolls == []:
            raise NotFoundError(status_code=404)

        l = []

        for enroll in enrolls:
            msg = {
                "enrollment_id": enroll.enrollment_id,
                "student_id": enroll.estudent_id,
                "course_id": enroll.ecourse_id
            }
            l.append(msg)

        return l, 200

    def post(self, student_id):
        args = create_enroll_parser.parse_args()
        course_id = args.get("course_id", None)



        student = Student.query.filter(
            Student.student_id == student_id).scalar()

        if student is None:
            raise BusinessValidationError(
                status_code=404,
                error_code="ENROLLMENT002",
                error_message="Student not found"
            )

        course = Course.query.filter(Course.course_id == course_id).scalar()

        if course is None:
            raise BusinessValidationError(
                status_code=404,
                error_code="ENROLLMENT001",
                error_message="Course not found"
            )

        enroll = Enrollments(
            es_id=student_id,
            ec_id=course_id
        )

        db.session.add(enroll)
        db.session.commit()

        enrolls = Enrollments.query.filter(
            Enrollments.estudent_id == student_id).all()

        if enrolls == []:
            raise NotFoundError(status_code=404)

        l = []

        for enroll in enrolls:
            msg = {
                "enrollment_id": enroll.enrollment_id,
                "student_id": enroll.estudent_id,
                "course_id": enroll.ecourse_id
            }
            l.append(msg)

        return l, 201

    def delete(self, course_id, student_id):
        student = Student.query.filter(
            Student.student_id == student_id).scalar()

        if student is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT002",
                error_message="Student does not exist"
            )

        course = Course.query.filter(Course.course_id == course_id).scalar()

        if course is None:
            raise BusinessValidationError(
                status_code=400,
                error_code="ENROLLMENT001",
                error_message="Course does not exist"
            )

        enrolls = Enrollments.query.filter(
            Enrollments.estudent_id == student_id).filter(Enrollments.ecourse_id == course_id
        ).all()

        if enrolls == []:
            raise NotFoundError(status_code=404)

        for enroll in enrolls:
            db.session.delete(enroll)
        db.session.commit()

        return "", 200


api.add_resource(EnrollmentAPI, "/api/student/<int:student_id>/course","/api/student/<int:student_id>/course/<int:course_id>")


if __name__ == '__main__':
    app.run()
