from flask import render_template, flash, redirect, url_for, send_file
from app.forms import generateNonogramForm
from app import app
from nonogen.generator import no_generator
from werkzeug.utils import secure_filename
import os


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    generate_nonogram_form = generateNonogramForm()

    return render_template("nonogen.html",
                           generate_nonogram_form=generate_nonogram_form)


@app.route("/generate_nonogram_form", methods=["GET", "POST"])
def generate_nonogram():
    generate_nonogram_form = generateNonogramForm()

    if generate_nonogram_form.validate_on_submit():
        image = generate_nonogram_form.image.data
        filename = secure_filename(image.filename)
        img_path = os.path.join(
            os.path.join(
                os.path.normpath(app.instance_path + os.sep + os.pardir), "nonogen")
            , "input_images", filename)
        image.save(img_path)

        base_path = os.path.normpath(
                        os.path.normpath(img_path + os.sep + os.pardir) + os.sep + os.pardir)

        run_result = no_generator(img_path=img_path,
                                  size=f"{generate_nonogram_form.width.data}x{generate_nonogram_form.height.data}",
                                  colour=generate_nonogram_form.colour.data).run()

        if run_result:
            os.remove(img_path)

            no_path = f"{filename}_nonogram"
            so_path = f"{filename}_solution"

            if generate_nonogram_form.colour.data:
                no_path = f"{filename}_colour_nonogram"
                so_path = f"{filename}_colour_solution"

            no_join = os.path.join(base_path, "nonograms", no_path)
            so_join = os.path.join(base_path, "solutions", so_path)

            return redirect(url_for("send_files", no_path=no_join, so_path=so_join, filename=filename))

        else:
            flash("Something went wrong. Please try again or contact the maintainer of the website.")

    flash(generate_nonogram_form.errors)

    return redirect(url_for("index"))


@app.route("/download_files")
def send_files(no_path, so_path, filename):
    send_file(no_path, attachment_filename=f"{filename}_solution.png")
    send_file(so_path, attachment_filename=f"{filename}_nonogram.png")

    os.remove(no_path)
    os.remove(so_path)

    flash("Succes!")
