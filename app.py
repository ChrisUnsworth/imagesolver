import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from detector import detect_puzzle_type
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


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


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

        # Step 1: detect puzzle type
        try:
            puzzle_info = detect_puzzle_type(save_path)
        except Exception as e:
            flash(f"Puzzle detection failed: {e}", "error")
            return redirect(url_for("index"))

        puzzle_type = puzzle_info["type"]

        # Step 2: route to the appropriate handler
        if puzzle_type == "sudoku":
            try:
                detected = analyze_sudoku(save_path)
            except Exception as e:
                flash(f"Sudoku analysis failed: {e}", "error")
                return redirect(url_for("index"))

            try:
                solution = solve_sudoku_mip(detected["grid"])
            except Exception as e:
                flash(f"MIP solver error: {e}", "error")
                solution = None

            return render_template(
                "index.html",
                puzzle_info=puzzle_info,
                filename=filename,
                detected=detected,
                solution=solution,
            )

        # Queens and any future unknown types — show image + detection result only
        return render_template(
            "index.html",
            puzzle_info=puzzle_info,
            filename=filename,
            detected=None,
            solution=None,
        )

    return render_template("index.html", puzzle_info=None, filename=None, detected=None, solution=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
