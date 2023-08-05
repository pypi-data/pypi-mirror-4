from datetime import datetime
from formencode.validators import FancyValidator, Invalid

class NaiveDateTimeValidator(FancyValidator):

    def _to_python(self, value, status):
        date_string = value.strip()
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        except:
            raise Invalid('date must be in format yyyy-mm-dd hh:mm', value, status)
        return date
