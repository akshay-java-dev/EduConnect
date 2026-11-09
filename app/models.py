from datetime import datetime
from flask_login import UserMixin
from .extensions import db
class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False)
    email=db.Column(db.String(180),unique=True,nullable=False,index=True)
    password_hash=db.Column(db.String(255),nullable=False); role=db.Column(db.String(20),default="student",nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    def set_password(self,p,bcrypt): self.password_hash=bcrypt.generate_password_hash(p).decode()
    def check_password(self,p,bcrypt): return bcrypt.check_password_hash(self.password_hash,p)
class Subject(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),unique=True,nullable=False)
class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(180),nullable=False)
    description=db.Column(db.Text); filename=db.Column(db.String(255),nullable=False)
    subject_id=db.Column(db.Integer,db.ForeignKey("subject.id"),nullable=False); subject=db.relationship("Subject")
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Video(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(180),nullable=False)
    description=db.Column(db.Text); video_url=db.Column(db.String(600),nullable=False)
    subject_id=db.Column(db.Integer,db.ForeignKey("subject.id"),nullable=False); subject=db.relationship("Subject")

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text)

    # Connect exam to a subject
    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject.id"),
        nullable=True
    )
    subject = db.relationship("Subject")

    duration_minutes = db.Column(db.Integer, default=30)
    total_marks = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)

    questions = db.relationship(
        "Question",
        backref="exam",
        cascade="all, delete-orphan",
        order_by="Question.id"
    )
class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True); exam_id=db.Column(db.Integer,db.ForeignKey("exam.id"),nullable=False)
    prompt=db.Column(db.Text,nullable=False); question_type=db.Column(db.String(20),default="mcq")
    option_a=db.Column(db.String(500)); option_b=db.Column(db.String(500)); option_c=db.Column(db.String(500)); option_d=db.Column(db.String(500))
    correct_option=db.Column(db.String(1)); marks=db.Column(db.Integer,default=1)
class Submission(db.Model):
    id=db.Column(db.Integer,primary_key=True); exam_id=db.Column(db.Integer,db.ForeignKey("exam.id"),nullable=False)
    student_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    started_at=db.Column(db.DateTime,default=datetime.utcnow); submitted_at=db.Column(db.DateTime)
    score=db.Column(db.Integer,default=0); status=db.Column(db.String(20),default="in_progress")
    exam=db.relationship("Exam"); student=db.relationship("User")
    answers=db.relationship("Answer",backref="submission",cascade="all, delete-orphan")
    __table_args__=(db.UniqueConstraint("exam_id","student_id",name="one_attempt_per_exam"),)
class Answer(db.Model):
    id=db.Column(db.Integer,primary_key=True); submission_id=db.Column(db.Integer,db.ForeignKey("submission.id"),nullable=False)
    question_id=db.Column(db.Integer,db.ForeignKey("question.id"),nullable=False)
    answer_text=db.Column(db.Text); awarded_marks=db.Column(db.Integer,default=0); question=db.relationship("Question")
