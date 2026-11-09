
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import login_required, current_user

from .extensions import db
from .models import Subject, Exam, Note, Video, Submission, Answer

student = Blueprint("student", __name__)


@student.before_request
@login_required
def guard():
    if current_user.role != "student":
        abort(403)


# STUDENT DASHBOARD
@student.get("/dashboard")
def dashboard():

    subjects = Subject.query.order_by(Subject.name.asc()).all()

    submissions = (
        Submission.query
        .filter_by(student_id=current_user.id)
        .order_by(Submission.id.desc())
        .all()
    )

    return render_template(
        "student/dashboard.html",
        subjects=subjects,
        submissions=submissions
    )


# INDIVIDUAL SUBJECT PAGE
@student.get("/subject/<int:sid>")
def subject_detail(sid):

    subject = db.get_or_404(Subject, sid)

    notes = (
        Note.query
        .filter_by(subject_id=subject.id)
        .order_by(Note.id.desc())
        .all()
    )

    videos = (
        Video.query
        .filter_by(subject_id=subject.id)
        .order_by(Video.id.desc())
        .all()
    )

    exams = (
        Exam.query
        .filter_by(
            subject_id=subject.id,
            is_published=True
        )
        .order_by(Exam.id.desc())
        .all()
    )

    return render_template(
        "student/subject_detail.html",
        subject=subject,
        notes=notes,
        videos=videos,
        exams=exams
    )


# STUDENT EXAM
@student.route("/exam/<int:eid>", methods=["GET", "POST"])
def take_exam(eid):

    e = db.get_or_404(Exam, eid)

    if not e.is_published:
        abort(404)

    s = Submission.query.filter_by(
        exam_id=e.id,
        student_id=current_user.id
    ).first()

    if s and s.status == "submitted":
        flash("You already submitted this exam.", "info")
        return redirect(url_for("student.dashboard"))

    if not s:
        s = Submission(exam=e, student=current_user)
        db.session.add(s)
        db.session.commit()

    deadline = s.started_at + timedelta(
        minutes=e.duration_minutes
    )

    if request.method == "POST" or datetime.utcnow() >= deadline:

        score = 0

        for q in e.questions:

            val = request.form.get(
                "q_" + str(q.id), ""
            ).strip()

            a = next(
                (
                    x for x in s.answers
                    if x.question_id == q.id
                ),
                None
            )

            if not a:
                a = Answer(
                    submission=s,
                    question=q
                )
                db.session.add(a)

            a.answer_text = val

            if (
                q.question_type == "mcq"
                and val.upper() == (q.correct_option or "").upper()
            ):
                a.awarded_marks = q.marks
                score += q.marks

        s.score = score
        s.status = "submitted"
        s.submitted_at = datetime.utcnow()

        db.session.commit()

        flash(
            "Exam submitted. Written answers await grading.",
            "success"
        )

        return redirect(url_for("student.dashboard"))

    return render_template(
        "student/take_exam.html",
        exam=e,
        deadline=deadline
    )
