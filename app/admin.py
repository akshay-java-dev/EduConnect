
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory,
    abort
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .extensions import db
from .models import (
    User,
    Subject,
    Note,
    Video,
    Exam,
    Question,
    Submission
)


admin = Blueprint("admin", __name__)


# ADMIN LOGIN PROTECTION
@admin.before_request
@login_required
def guard():
    if current_user.role != "admin":
        abort(403)


# CREATE OR FIND SUBJECT
def subject_for(name):

    name = (name or "").strip()

    if not name:
        return None

    subject = Subject.query.filter(
        db.func.lower(Subject.name) == name.lower()
    ).first()

    if not subject:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.flush()

    return subject


# ADMIN DASHBOARD
@admin.get("/dashboard")
def dashboard():

    return render_template(
        "admin/dashboard.html",
        students=User.query.filter_by(role="student").count(),
        exams=Exam.query.count(),
        notes=Note.query.count(),
        submissions=Submission.query.count()
    )


# MANAGE SUBJECTS
@admin.route("/subjects", methods=["GET", "POST"])
def subjects():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        if name:
            subject_for(name)
            db.session.commit()
            flash("Subject saved successfully.", "success")
        else:
            flash("Please enter a subject name.", "danger")

        return redirect(url_for("admin.subjects"))

    return render_template(
        "admin/subjects.html",
        subjects=Subject.query.order_by(Subject.name).all()
    )


# MANAGE PDF NOTES
@admin.route("/notes", methods=["GET", "POST"])
def notes():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        subject = subject_for(
            request.form.get("subject_name")
        )
        file = request.files.get("pdf")

        if (
            not title
            or not subject
            or not file
            or not file.filename.lower().endswith(".pdf")
        ):
            flash(
                "Enter title, subject and a valid PDF file.",
                "danger"
            )

        else:

            filename = (
                uuid.uuid4().hex
                + "_"
                + secure_filename(file.filename)
            )

            file.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            note = Note(
                title=title,
                description=request.form.get("description", ""),
                filename=filename,
                subject=subject
            )

            db.session.add(note)
            db.session.commit()

            flash("PDF uploaded successfully.", "success")

        return redirect(url_for("admin.notes"))

    return render_template(
        "admin/notes.html",
        notes=Note.query.order_by(Note.id.desc()).all()
    )


# DOWNLOAD PDF
@admin.get("/notes/<int:nid>/download")
def download_note(nid):

    note = db.get_or_404(Note, nid)

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        note.filename,
        as_attachment=True
    )


# DELETE PDF
@admin.post("/notes/<int:nid>/delete")
def delete_note(nid):

    note = db.get_or_404(Note, nid)

    path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        note.filename
    )

    if os.path.exists(path):
        os.remove(path)

    db.session.delete(note)
    db.session.commit()

    flash("Note deleted successfully.", "success")

    return redirect(url_for("admin.notes"))


# MANAGE VIDEO LECTURES
@admin.route("/videos", methods=["GET", "POST"])
def videos():

    if request.method == "POST":

        subject = subject_for(
            request.form.get("subject_name")
        )

        title = request.form.get("title", "").strip()

        video_url = request.form.get(
            "video_url", ""
        ).strip()

        if (
            not subject
            or not title
            or not video_url.startswith(("https://", "http://"))
        ):

            flash(
                "Enter title, subject and a valid video URL.",
                "danger"
            )

        else:

            video = Video(
                title=title,
                description=request.form.get("description", ""),
                video_url=video_url,
                subject=subject
            )

            db.session.add(video)
            db.session.commit()

            flash("Video added successfully.", "success")

        return redirect(url_for("admin.videos"))

    return render_template(
        "admin/videos.html",
        videos=Video.query.order_by(Video.id.desc()).all()
    )


# DELETE VIDEO
@admin.post("/videos/<int:vid>/delete")
def delete_video(vid):

    video = db.get_or_404(Video, vid)

    db.session.delete(video)
    db.session.commit()

    flash("Video deleted successfully.", "success")

    return redirect(url_for("admin.videos"))


# CREATE SUBJECT-WISE EXAMS
@admin.route("/exams", methods=["GET", "POST"])
def exams():

    if request.method == "POST":

        title = request.form.get(
            "title", ""
        ).strip()

        subject_name = request.form.get(
            "subject_name", ""
        ).strip()

        subject = subject_for(subject_name)

        if not title or not subject:

            flash(
                "Please enter exam title and subject name.",
                "danger"
            )

            return redirect(url_for("admin.exams"))

        try:

            duration = max(
                1,
                int(request.form.get("duration", 30))
            )

        except (ValueError, TypeError):

            duration = 30

        exam = Exam(
            title=title,
            description=request.form.get("description", ""),
            subject=subject,
            duration_minutes=duration
        )

        db.session.add(exam)
        db.session.commit()

        flash(
            "Exam created successfully.",
            "success"
        )

        return redirect(url_for("admin.exams"))

    exams_list = Exam.query.order_by(
        Exam.id.desc()
    ).all()

    return render_template(
        "admin/exams.html",
        exams=exams_list
    )


# ADD EXAM QUESTIONS
@admin.route("/exams/<int:eid>/edit", methods=["GET", "POST"])
def edit_exam(eid):

    exam = db.get_or_404(Exam, eid)

    if request.method == "POST":

        kind = request.form.get(
            "question_type", "mcq"
        )

        prompt = request.form.get(
            "prompt", ""
        ).strip()

        try:
            marks = max(
                1,
                int(request.form.get("marks", 1))
            )
        except (ValueError, TypeError):
            marks = 1

        question = Question(
            exam=exam,
            prompt=prompt,
            question_type=kind,
            marks=marks
        )

        if not question.prompt:

            flash(
                "Question text is required.",
                "danger"
            )

        else:

            if kind == "mcq":

                for option in "abcd":

                    setattr(
                        question,
                        "option_" + option,
                        request.form.get(
                            "option_" + option, ""
                        ).strip()
                    )

                question.correct_option = request.form.get(
                    "correct_option", "A"
                )

                if not all([
                    question.option_a,
                    question.option_b,
                    question.option_c,
                    question.option_d
                ]):

                    flash(
                        "Please fill all MCQ options.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "admin.edit_exam",
                            eid=eid
                        )
                    )

            db.session.add(question)
            db.session.flush()

            exam.total_marks = sum(
                item.marks for item in exam.questions
            )

            db.session.commit()

            flash(
                "Question added successfully.",
                "success"
            )

        return redirect(
            url_for("admin.edit_exam", eid=eid)
        )

    return render_template(
        "admin/edit_exam.html",
        exam=exam
    )


# PUBLISH OR UNPUBLISH EXAM
@admin.post("/exams/<int:eid>/publish")
def publish_exam(eid):

    exam = db.get_or_404(Exam, eid)

    if exam.questions:

        exam.is_published = not exam.is_published

        db.session.commit()

        flash(
            "Exam publication status updated.",
            "success"
        )

    else:

        flash(
            "Add questions before publishing.",
            "warning"
        )

    return redirect(url_for("admin.exams"))


# VIEW STUDENT SUBMISSIONS
@admin.get("/grading")
def grading():

    submissions = (
        Submission.query
        .filter_by(status="submitted")
        .order_by(Submission.submitted_at.desc())
        .all()
    )

    return render_template(
        "admin/grading.html",
        submissions=submissions
    )


# GRADE WRITTEN ANSWERS
@admin.route("/grading/<int:sid>", methods=["GET", "POST"])
def grade(sid):

    submission = db.get_or_404(Submission, sid)

    if request.method == "POST":

        for answer in submission.answers:

            if answer.question.question_type == "written":

                try:

                    marks = int(
                        request.form.get(
                            "marks_" + str(answer.id), 0
                        )
                    )

                    answer.awarded_marks = max(
                        0,
                        min(answer.question.marks, marks)
                    )

                except (ValueError, TypeError):

                    answer.awarded_marks = 0

        submission.score = sum(
            answer.awarded_marks
            for answer in submission.answers
        )

        db.session.commit()

        flash(
            "Answers graded successfully.",
            "success"
        )

        return redirect(url_for("admin.grading"))

    return render_template(
        "admin/grade.html",
        submission=submission
    )
