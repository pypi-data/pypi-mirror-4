from wtforms import Form, validators
from wtforms import BooleanField, TextField
from wtforms import HiddenField, PasswordField
from wtforms import SubmitField

from mako.template import Template

valid_name = [validators.Length(min=1, max=25)]
valid_password = [validators.Length(min=6, max=35)]
optional = [validators.Optional()]

password = PasswordField('Password')

def submit_button(label):
    return SubmitField(label)

BASE_FORM_TEMPLATE_MAKO = """
<div class="chpasswd">
<form action="${action}" method="post">
<div>
<table>
%for field in form:
    <tr>
        <td><div>${field.label}:</td>
        <td>${field()}</div></td>
    </tr>
%endfor
<tr>
<td><div>${form.submit.label}:</td><td>${form.submit()}</div></td>
</tr>
</table>
</div>
</form>
</div>
"""
BaseFormTemplate = Template(BASE_FORM_TEMPLATE_MAKO)


class BaseForm(Form):
    _template = BaseFormTemplate
    submit = None
    
    def render(self, **kw):
        return self._template.render(**kw)
        
    def add_submit(self, label='Submit'):
        self.submit = SubmitField(label).bind(self, 'submit')

    def set_template(self, content):
        self._template = Template(content)
        

        
        
LOGIN_FORM_TEMPLATE_MAKO = """
<div class="loginmessage">
${message}
</div>
<form action="${action}" method="post">
<div>${form.came_from(value=came_from)}</div>
<div>
<table>
<tr>
<td><div>${form.login.label()}</td><td>${form.login()}</div></td>
</tr>
<tr>
<td><div>${form.password.label()}</td><td>${form.password()}</div></td>
</tr>
<tr>
<td><div>${form.submit.label()}</td><td>${form.submit()}</div></td>
</tr>
</table>
</div>
</form>
"""
LoginTemplate = Template(LOGIN_FORM_TEMPLATE_MAKO)
class LoginForm(BaseForm):
    came_from = HiddenField()
    login = TextField('User Name', valid_name)
    password = PasswordField('Password')
    _template = LoginTemplate
    
    def render(self, action, message='', came_from=''):
        return BaseForm.render(self, form=self, action=action,
                               message=message,
                               came_from=came_from)

