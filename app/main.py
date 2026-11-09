from flask import Blueprint,render_template,send_from_directory,current_app,abort
from flask_login import login_required
from .models import Note,Video,Exam
main=Blueprint("main",__name__)
@main.get("/")
def home():
    return render_template("home.html",notes=Note.query.order_by(Note.id.desc()).limit(3).all(),
      videos=Video.query.order_by(Video.id.desc()).limit(3).all(),exams=Exam.query.filter_by(is_published=True).all())
@main.get("/notes/<int:nid>/download")
@login_required
def download_note(nid):
    note=Note.query.get_or_404(nid)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"],note.filename,as_attachment=True)
