from tg.i18n import lazy_ugettext as l_
from tgext.pluggable import plug_url

from tw2.core import DateTimeValidator, Required
from tw2.forms import TextField, CalendarDateTimePicker, TextArea, FormPage, TableForm

class NewPollForm(FormPage):
    title = l_("Poll")

    class child(TableForm):
        action = '/tgpolls/save'
        body = TextField(validator=Required)
        expire = CalendarDateTimePicker(label_text=l_('Expiry date'), date_format='%d/%m/%Y %H:%M',
                                                  validator=DateTimeValidator(required=True, format='%d/%m/%Y %H:%M')
                                                  )
        answers = TextArea(label_text=l_('Answers separated by | (eg: First answer|Second answer)'), validator=Required)

new_poll_form = NewPollForm()
