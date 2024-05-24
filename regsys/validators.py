from django.core.exceptions import ValidationError

class RegularValidator:
    def __init__(self, min_length=8, capital=True, digit=True):
        self.min_length = min_length
        self.capital = capital
        self.digit = digit

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                "Пароль должен содержать хотя бы %(min_length)d символов",
                code="password_too_short",
                params={"min_length": self.min_length},
            )
        if self.capital and password.lower() == password:
            raise ValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву",
                code="no_capitals",
                params={},
            )
        if self.digit and not any(c.isdigit() for c in password):
            raise ValidationError(
                "Пароль должен содержать хотя бы одну цифру",
                code="no_digits",
                params={},
            )

    def get_help_text(self):
        return "Пароль должен содержать хотя бы " + str(self.min_length) + " символов" + (", одну заглавную букву" if self.capital else "") + (", одну цифру" if self.digit else "")
