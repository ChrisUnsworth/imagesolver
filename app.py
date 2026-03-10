import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

from detectors.puzzle_detector import detect_puzzle_type
from analyzers.sudoku_analyzer import analyze_sudoku
from analyzers.queens_analyzer import analyze_queens
from solvers.sudoku_solver import solve_sudoku
from solvers.queens_solver import solve_queens

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

# Colour palette for Queens region display (up to 15 regions).
REGION_COLORS = [
    "#FF6B6B",  # 1  red
    "#4ECDC4",  # 2  teal
    "#45B7D1",  # 3  sky blue
    "#96CEB4",  # 4  sage green
    "#FFD93D",  # 5  yellow
    "#C77DFF",  # 6  purple
    "#F4A261",  # 7  orange
    "#06D6A0",  # 8  mint
    "#FF85A1",  # 9  pink
    "#74B3CE",  # 10 steel blue
    "#B5838D",  # 11 mauve
    "#90BE6D",  # 12 lime green
    "#F9C74F",  # 13 gold
    "#577590",  # 14 slate
    "#F08080",  # 15 light coral
]

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

        # ── Step 1: detect puzzle type ────────────────────────────────────────
        try:
            puzzle_info = detect_puzzle_type(save_path)
        except Exception as e:
            flash(f"Puzzle detection failed: {e}", "error")
            return redirect(url_for("index"))

        puzzle_type = puzzle_info["type"]

        # ── Step 2: route to the appropriate handler ──────────────────────────
        if puzzle_type == "sudoku":
            try:
                detected = analyze_sudoku(save_path)
            except Exception as e:
                flash(f"Sudoku analysis failed: {e}", "error")
                return redirect(url_for("index"))

            try:
                solution = solve_sudoku(detected["grid"])
            except Exception as e:
                flash(f"Sudoku solver error: {e}", "error")
                solution = None

            return render_template(
                "index.html",
                puzzle_info=puzzle_info,
                filename=filename,
                detected=detected,
                solution=solution,
                queens_data=None,
                queens_solution=None,
                queens_colors=None,
            )

        if puzzle_type == "queens":
            try:
                queens_data = analyze_queens(save_path)
            except Exception as e:
                flash(f"Queens analysis failed: {e}", "error")
                return redirect(url_for("index"))

            try:
                queens_solution = solve_queens(queens_data["grid"])
            except Exception as e:
                flash(f"Queens solver error: {e}", "error")
                queens_solution = None

            return render_template(
                "index.html",
                puzzle_info=puzzle_info,
                filename=filename,
                detected=None,
                solution=None,
                queens_data=queens_data,
                queens_solution=queens_solution,
                queens_colors=REGION_COLORS,
            )

        # Unknown type — show image only
        return render_template(
            "index.html",
            puzzle_info=puzzle_info,
            filename=filename,
            detected=None,
            solution=None,
            queens_data=None,
            queens_solution=None,
            queens_colors=None,
        )

    return render_template(
        "index.html",
        puzzle_info=None,
        filename=None,
        detected=None,
        solution=None,
        queens_data=None,
        queens_solution=None,
        queens_colors=None,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
