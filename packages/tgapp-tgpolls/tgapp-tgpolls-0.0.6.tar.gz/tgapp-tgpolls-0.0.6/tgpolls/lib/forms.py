from tg.i18n import lazy_ugettext as l_
from tgext.pluggable import plug_url

from tw2.core import DateTimeValidator, Required
from tw2.forms import TextField, CalendarDateTimePicker, TextArea, FormPage, TableForm, LabelField, Label

class NewPollForm(TableForm):
    title = l_("Poll")

    action = plug_url('tgpolls', '/save', lazy=True)
    body = TextField(validator=Required, label= l_("The body of the poll in form of question (eg. Which one is the best team?)"))
    expire = CalendarDateTimePicker(date_format='%d/%m/%Y %H:%M', label=l_('Expiry date of the poll, dd/mm/YYYY hh:mm'),
                                        validator=DateTimeValidator(required=True, format='%d/%m/%Y %H:%M'))
    answers = TextArea(validator=Required, label=l_("Answers separated by | (eg: First answer|Second answer)"))

new_poll_form = NewPollForm()
