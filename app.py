import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from solver import analyze_sudoku
from mip_solver import solve_sudoku_mip

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

app = Flask(__name__)
app.secret_key = "dev-secret-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.", "error")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected.", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type. Please upload an image (png, jpg, jpeg, gif, bmp, webp).", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        try:
            detected = analyze_sudoku(save_path)
        except Exception as e:
            flash(f"Image analysis failed: {e}", "error")
            return redirect(url_for("index"))

        try:
            solution = solve_sudoku_mip(detected["grid"])
        except Exception as e:
            flash(f"MIP solver error: {e}", "error")
            solution = None

        return render_template(
            "index.html",
            detected=detected,
            solution=solution,
            filename=filename,
        )

    return render_template("index.html", detected=None, solution=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
