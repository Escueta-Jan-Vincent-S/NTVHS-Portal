from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from database_functions import (init_database, get_all_items, add_item_to_db, get_item_by_id,
                                update_item_in_db, delete_item_from_db, add_video_to_db,
                                update_video_in_db, delete_video_from_db, get_videos_by_grade,
                                search_videos_by_title, add_library_book_to_db, update_library_book_in_db,
                                delete_library_book_from_db, get_library_books_by_grade, search_library_books_by_title)
from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = SECRET_KEY

# File upload configuration
UPLOAD_FOLDER = 'static/videos'
LIBRARY_PDF_FOLDER = 'static/library/pdfs'
LIBRARY_PICTURE_FOLDER = 'static/library/pictures'
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm', 'flv', '3gp', 'm4v'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LIBRARY_PDF_FOLDER'] = LIBRARY_PDF_FOLDER
app.config['LIBRARY_PICTURE_FOLDER'] = LIBRARY_PICTURE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = None  # No file size limit

# Create upload folders if they don't exist
folders = [UPLOAD_FOLDER, LIBRARY_PDF_FOLDER, LIBRARY_PICTURE_FOLDER]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)


def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


def allowed_pdf_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PDF_EXTENSIONS


def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# ==================== AUTHENTICATION ROUTES ====================
@app.route("/")
def login():
    return render_template("index.html")


@app.route("/login", methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('homepage'))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))


@app.route("/homepage")
def homepage():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("admin_homepage.html")


@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


# ==================== QUIZ ROUTES ====================
@app.route("/manage_quizzes")
def manage_quizzes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    quizzes = get_all_items('quizzes')
    return render_template("manage_quizzes.html", quizzes=quizzes)


@app.route("/add_quiz", methods=['POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    quiz_data = {
        'name': request.form.get('name'),
        'grade': request.form.get('grade'),
        'end_date': request.form.get('end_date'),
        'upload_link': request.form.get('upload_link'),
        'professor': request.form.get('professor')
    }

    if add_item_to_db('quizzes', quiz_data):
        flash('Quiz added successfully!', 'success')
    else:
        flash('Error adding quiz. Please try again.', 'error')

    return redirect(url_for('manage_quizzes'))


@app.route("/edit_quiz/<int:quiz_id>")
def edit_quiz(quiz_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    quiz = get_item_by_id('quizzes', quiz_id)
    if not quiz:
        flash('Quiz not found!', 'error')
        return redirect(url_for('manage_quizzes'))

    return render_template("edit_quiz.html", quiz=quiz)


@app.route("/update_quiz/<int:quiz_id>", methods=['POST'])
def update_quiz(quiz_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    quiz_data = {
        'name': request.form.get('name'),
        'grade': request.form.get('grade'),
        'end_date': request.form.get('end_date'),
        'upload_link': request.form.get('upload_link'),
        'professor': request.form.get('professor')
    }

    if update_item_in_db('quizzes', quiz_id, quiz_data):
        flash('Quiz updated successfully!', 'success')
    else:
        flash('Error updating quiz. Please try again.', 'error')

    return redirect(url_for('manage_quizzes'))


@app.route("/delete_quiz/<int:quiz_id>")
def delete_quiz(quiz_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if delete_item_from_db('quizzes', quiz_id):
        flash('Quiz deleted successfully!', 'success')
    else:
        flash('Error deleting quiz. Please try again.', 'error')

    return redirect(url_for('manage_quizzes'))


# ==================== ACTIVITY ROUTES ====================
@app.route("/manage_activities")
def manage_activities():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    activities = get_all_items('activities')
    return render_template("manage_activity.html", activities=activities)


@app.route("/add_activity", methods=['POST'])
def add_activity():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    activity_data = {
        'name': request.form.get('name'),
        'grade': request.form.get('grade'),
        'end_date': request.form.get('end_date'),
        'upload_link': request.form.get('upload_link'),
        'professor': request.form.get('professor')
    }

    if add_item_to_db('activities', activity_data):
        flash('Activity added successfully!', 'success')
    else:
        flash('Error adding activity. Please try again.', 'error')

    return redirect(url_for('manage_activities'))


@app.route("/edit_activity/<int:activity_id>")
def edit_activity(activity_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    activity = get_item_by_id('activities', activity_id)
    if not activity:
        flash('Activity not found!', 'error')
        return redirect(url_for('manage_activities'))

    return render_template("edit_activity.html", activity=activity)


@app.route("/update_activity/<int:activity_id>", methods=['POST'])
def update_activity(activity_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    activity_data = {
        'name': request.form.get('name'),
        'grade': request.form.get('grade'),
        'end_date': request.form.get('end_date'),
        'upload_link': request.form.get('upload_link'),
        'professor': request.form.get('professor')
    }

    if update_item_in_db('activities', activity_id, activity_data):
        flash('Activity updated successfully!', 'success')
    else:
        flash('Error updating activity. Please try again.', 'error')

    return redirect(url_for('manage_activities'))


@app.route("/delete_activity/<int:activity_id>")
def delete_activity(activity_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if delete_item_from_db('activities', activity_id):
        flash('Activity deleted successfully!', 'success')
    else:
        flash('Error deleting activity. Please try again.', 'error')

    return redirect(url_for('manage_activities'))


# ==================== WORKSHEET ROUTES ====================
@app.route("/manage_worksheets")
def manage_worksheets():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    worksheets = get_all_items('worksheets')
    return render_template("manage_worksheets.html", worksheets=worksheets)


@app.route("/add_worksheet", methods=['POST'])
def add_worksheet():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    worksheet_data = {
        'name': request.form.get('name'),
        'grade': request.form.get('grade'),
        'end_date': request.form.get('end_date'),
        'upload_link': request.form.get('upload_link'),
        'professor': request.form.get('professor')
    }

    if add_item_to_db('worksheets', worksheet_data):
        flash('Worksheet added successfully!', 'success')
    else:
        flash('Error adding worksheet. Please try again.', 'error')

    return redirect(url_for('manage_worksheets'))


@app.route("/edit_worksheet/<int:worksheet_id>")
def edit_worksheet(worksheet_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    worksheet = get_item_by_id('worksheets', worksheet_id)
    if not worksheet:
        flash('Worksheet not found!', 'error')
        return redirect(url_for('manage_worksheets'))

    return render_template("edit_worksheet.html", worksheet=worksheet)


@app.route("/update_worksheet/<int:worksheet_id>", methods=['POST'])
def update_worksheet(worksheet_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    worksheet_data = {
        'name': request.form.get('name'),
        'grade': request.form.get('grade'),
        'end_date': request.form.get('end_date'),
        'upload_link': request.form.get('upload_link'),
        'professor': request.form.get('professor')
    }

    if update_item_in_db('worksheets', worksheet_id, worksheet_data):
        flash('Worksheet updated successfully!', 'success')
    else:
        flash('Error updating worksheet. Please try again.', 'error')

    return redirect(url_for('manage_worksheets'))


@app.route("/delete_worksheet/<int:worksheet_id>")
def delete_worksheet(worksheet_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if delete_item_from_db('worksheets', worksheet_id):
        flash('Worksheet deleted successfully!', 'success')
    else:
        flash('Error deleting worksheet. Please try again.', 'error')

    return redirect(url_for('manage_worksheets'))


# ==================== VIDEO ROUTES ====================
@app.route("/manage_videos")
def manage_videos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("manage_videos.html")


@app.route("/upload_video", methods=['POST'])
def upload_video():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Check if file was uploaded
    if 'video_file' not in request.files:
        flash('No video file selected!', 'error')
        return redirect(url_for('manage_videos'))

    file = request.files['video_file']
    if file.filename == '' or not allowed_video_file(file.filename):
        flash('Please select a valid video file!', 'error')
        return redirect(url_for('manage_videos'))

    # Save file with timestamp
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
    filename = timestamp + filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Get file size
    file_size = os.path.getsize(file_path)

    video_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'grade': request.form.get('grade'),
        'filename': filename,
        'file_size': file_size
    }

    if add_video_to_db(video_data):
        flash('Video uploaded successfully!', 'success')
    else:
        flash('Error uploading video. Please try again.', 'error')
        # Clean up file if database insert failed
        try:
            os.remove(file_path)
        except:
            pass

    return redirect(url_for('video_library'))


@app.route("/video_library")
def video_library():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    grade = request.args.get('grade')
    search = request.args.get('search')

    if search:
        videos = search_videos_by_title(search)
    elif grade:
        videos = get_videos_by_grade(grade)
    else:
        videos = get_all_items('videos')

    return render_template("video_library.html", videos=videos, selected_grade=grade)


@app.route("/edit_video/<int:video_id>")
def edit_video(video_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    video = get_item_by_id('videos', video_id)
    if not video:
        flash('Video not found!', 'error')
        return redirect(url_for('video_library'))

    return render_template("edit_video.html", video=video)


@app.route("/update_video/<int:video_id>", methods=['POST'])
def update_video(video_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    video_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'grade': request.form.get('grade')
    }

    if update_video_in_db(video_id, video_data):
        flash('Video updated successfully!', 'success')
    else:
        flash('Error updating video. Please try again.', 'error')

    return redirect(url_for('video_library'))


@app.route("/delete_video/<int:video_id>")
def delete_video(video_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if delete_video_from_db(video_id):
        flash('Video deleted successfully!', 'success')
    else:
        flash('Error deleting video. Please try again.', 'error')

    return redirect(url_for('video_library'))


@app.route("/download_video/<int:video_id>")
def download_video(video_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    video = get_item_by_id('videos', video_id)
    if not video:
        flash('Video not found!', 'error')
        return redirect(url_for('video_library'))

    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            video['filename'],
            as_attachment=True,
            download_name=f"{video['title']}.{video['filename'].split('.')[-1]}"
        )
    except Exception as e:
        flash('Error downloading video. Please try again.', 'error')
        return redirect(url_for('video_library'))


# ==================== LIBRARY ROUTES ====================
@app.route("/manage_library")
def manage_library():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("manage_library.html")


@app.route("/upload_book", methods=['POST'])
def upload_book():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Check if PDF was uploaded
    if 'pdf_file' not in request.files:
        flash('No PDF file selected!', 'error')
        return redirect(url_for('manage_library'))

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '' or not allowed_pdf_file(pdf_file.filename):
        flash('Please select a valid PDF file!', 'error')
        return redirect(url_for('manage_library'))

    # Save PDF file with timestamp
    pdf_filename = secure_filename(pdf_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
    pdf_filename = timestamp + pdf_filename
    pdf_path = os.path.join(app.config['LIBRARY_PDF_FOLDER'], pdf_filename)
    pdf_file.save(pdf_path)

    # Get PDF file size
    file_size = os.path.getsize(pdf_path)

    # Handle optional picture file
    picture_filename = None
    if 'picture_file' in request.files:
        picture_file = request.files['picture_file']
        if picture_file.filename != '' and allowed_image_file(picture_file.filename):
            picture_filename = secure_filename(picture_file.filename)
            picture_filename = timestamp + picture_filename
            picture_path = os.path.join(app.config['LIBRARY_PICTURE_FOLDER'], picture_filename)
            picture_file.save(picture_path)

    book_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'grade': request.form.get('grade'),
        'pdf_filename': pdf_filename,
        'picture_filename': picture_filename,
        'file_size': file_size
    }

    if add_library_book_to_db(book_data):
        flash('Book uploaded successfully!', 'success')
    else:
        flash('Error uploading book. Please try again.', 'error')
        # Clean up files if database insert failed
        try:
            os.remove(pdf_path)
            if picture_filename:
                os.remove(picture_path)
        except:
            pass

    return redirect(url_for('library_books'))


@app.route("/library_books")
def library_books():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    grade = request.args.get('grade')
    search = request.args.get('search')

    if search:
        books = search_library_books_by_title(search)
    elif grade:
        books = get_library_books_by_grade(grade)
    else:
        books = get_all_items('library')

    return render_template("library_books.html", books=books, selected_grade=grade)


@app.route("/edit_book/<int:book_id>")
def edit_book(book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    book = get_item_by_id('library', book_id)
    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('library_books'))

    return render_template("edit_book.html", book=book)


@app.route("/update_book/<int:book_id>", methods=['POST'])
def update_book(book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    book_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'grade': request.form.get('grade')
    }

    if update_library_book_in_db(book_id, book_data):
        flash('Book updated successfully!', 'success')
    else:
        flash('Error updating book. Please try again.', 'error')

    return redirect(url_for('library_books'))


@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if delete_library_book_from_db(book_id):
        flash('Book deleted successfully!', 'success')
    else:
        flash('Error deleting book. Please try again.', 'error')

    return redirect(url_for('library_books'))


@app.route("/download_book/<int:book_id>")
def download_book(book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    book = get_item_by_id('library', book_id)
    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('library_books'))

    try:
        return send_from_directory(
            app.config['LIBRARY_PDF_FOLDER'],
            book['pdf_filename'],
            as_attachment=True,
            download_name=f"{book['title']}.pdf"
        )
    except Exception as e:
        flash('Error downloading book. Please try again.', 'error')
        return redirect(url_for('library_books'))


if __name__ == "__main__":
    # Initialize database on startup
    init_database()
    app.run(debug=True)