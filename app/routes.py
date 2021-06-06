from flask import render_template, flash, redirect, url_for, send_file, after_this_request
from app.forms import generateNonogramForm
from app import app
from nonogen.generator import no_generator
from werkzeug.utils import secure_filename
import zipfile
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

        run_result = no_generator(img_path=img_path,
                                  size=f"{generate_nonogram_form.width.data}x{generate_nonogram_form.height.data}",
                                  colour=generate_nonogram_form.colour.data).run()

        if run_result:
            os.remove(img_path)

            filename = filename.split(".")[0]

            base_path = os.path.normpath(
                os.path.normpath(img_path + os.sep + os.pardir) + os.sep + os.pardir)

            if generate_nonogram_form.colour.data:
                no_join = os.path.join(base_path, "nonograms", f"{filename}_colour_nonogram.png")
                so_join = os.path.join(base_path, "solutions", f"{filename}_colour_solution.png")
            else:
                no_join = os.path.join(base_path, "nonograms", f"{filename}_nonogram.png")
                so_join = os.path.join(base_path, "solutions", f"{filename}_solution.png")

            files_zip = zipfile.ZipFile(os.path.join(base_path, f"{filename}.zip"), "w", zipfile.ZIP_DEFLATED)
            files_zip.write(no_join, os.path.basename(no_join))
            files_zip.write(so_join, os.path.basename(so_join))
            files_zip.close()

            os.remove(no_join)
            os.remove(so_join)

            @after_this_request
            def remove_file(response):
                try:
                    os.remove(os.path.join(base_path, f"{filename}.zip"))
                    return redirect(url_for("index"))
                except Exception as e:
                    app.logger.error("Error removing or closing zip file.", e)
                return response

            return send_file(os.path.join(base_path, f"{filename}.zip"),
                             mimetype="zip",
                             attachment_filename=f"{filename}_nonogram.zip",
                             as_attachment=True)
        else:
            flash("Something went wrong. Please try again or contact the maintainer of the website.")

    flash(generate_nonogram_form.errors)

    return redirect(url_for("index"))
