from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class RegularValidator:
    def __init__(self, min_length=8, capital=True, digit=True):
        self.min_length = min_length
        self.capital = capital
        self.digit = digit

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )
        if self.capital and password.lower() == password:
            raise ValidationError(
                _("This password must contain at least one capital letter."),
                code="no_capitals",
                params={},
            )
        if self.digit and not any(c.isdigit() for c in password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code="no_digits",
                params={},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least " + str(self.min_length) + " characters" + (", one capital letter" if self.capital else "") + (", one digit" if self.digit else "")
        )