from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, NumberRange


class generateNonogramForm(FlaskForm):
    image = FileField(label="Image",
                      validators=[FileRequired("File was empty!"), FileAllowed(["jpg", "png"], ".jpg and .png only!")])
    width = IntegerField(label="Width",
                         validators=[DataRequired("Width field was empty!"),
                                     NumberRange(min=1, max=200, message="Please choose a width between 1 and 200")])
    height = IntegerField(label="Height",
                          validators=[DataRequired("Height field was empty!"),
                                      NumberRange(min=1, max=200, message="Please choose a height between 1 and 200")])
    colour = BooleanField(label="Colour",
                          default=False)
    submit = SubmitField("Generate nonogram")
