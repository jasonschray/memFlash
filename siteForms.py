from abc import ABCMeta, abstractmethod

class abstractField( object ):

    __metaclass__ = ABCMeta

    name = None
    value = None
    field_type = None
    support_key = 'TEXT'
    file_object = None
    htmlClass = None
    form=None
    html_id = None
    minlength = None

    def __init__(self, name = None, request = None, value = None, htmlClass = None, form=None, html_id=None, minlength = None):
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value
        if htmlClass is not None:
            self.htmlClass = htmlClass
        if html_id is not None:
            self.html_id = html_id
        if minlength is not None:
            self.minlength = minlength

    
    def get_html(self):
        return ('<input '
                + ('' if not self.field_type else ' type="'+self.field_type+'"')
                + ('' if not self.name else ' name="'+self.name+'"')
                + ('' if not self.value else ' value="'+self.value+'"')
                + ('' if not self.htmlClass else ' class="'+self.htmlClass+'"')
                + ('' if not self.form else ' form="'+self.form+'"')
                + ('' if not self.html_id else ' id="'+self.html_id+'"')
                + ('' if not self.minlength else ' minlength="'+self.minlength+'"')
                + '>')

    @abstractmethod
    def validate(self):
        pass

    @classmethod
    def init_with_info(cls,field_name,field_value=None):
        temp_field = cls()
        temp_field.field_name = field_name
        temp_field.field_value = field_value
        return temp_field

    def update_value(self, value=None, request=None):
        if value is not None:
            self.value = value
        elif request is not None and self.name is not None and self.name in request.form:
            self.value = request.form[self.name]
        else:
            return False
        return True

    def get_Info(self):
        return self.value




class textField ( abstractField ):
    field_type = 'text'
    

    def validate(self):
        return True
    

class textArea ( abstractField ):
    field_type = 'textarea'
    cols = '50'
    rows='4' 

    def get_html(self):
        return ('<textarea '
                + ('' if not self.name else ' name="'+self.name+'"')
                + ('' if not self.htmlClass else ' class="'+self.htmlClass+'"')
                + ('' if not self.form else ' form="'+self.form+'"')
                + ('' if not self.rows else ' rows="'+self.rows+'"')
                + ('' if not self.cols else ' cols="'+self.cols+'"')
                + '>'
                + ('' if not self.value else self.value)
                + '</textarea>')

    def validate(self):
        return True
   

class submitField ( abstractField ):
    field_type = "Submit"
    value= "Submit"
    name = "Submit"
    htmlClass = "btn btn-lg btn-primary btn-block"

    def validate(self):
        return True

class passwordField ( abstractField ):
    name = 'password'
    field_type = 'Password'
    autocomplete = 'off'
    minlength = '6'

    

    def validate(self):
        return True

    def get_html(self):
        return ('<input '
                + ('' if not self.field_type else ' type="'+self.field_type+'"')
                + ('' if not self.name else ' name="'+self.name+'"')
                + ('' if not self.autocomplete else ' autocomplete="'+self.autocomplete+'"')
                + ('' if not self.htmlClass else ' class="'+self.htmlClass+'"')
                + ('' if not self.html_id else ' id="'+self.html_id+'"')
                + ('' if not self.minlength else ' minlength="'+self.minlength+'"')
                + '>')

class verifiedPasswordField ( abstractField ):
    name = 'password'
    name_repeat = 'password_repeat'
    field_type = 'Password'
    autocomplete = 'off'
    repeat_value = None



    def validate(self):
        return True

    def get_html(self):
        html = ('<input '
                + ('' if not self.field_type else ' type="'+self.field_type+'"')
                + ('' if not self.name else ' name="'+self.name+'"')
                + ('' if not self.autocomplete else ' autocomplete="'+self.autocomplete+'"')
                + '>\n'
                + '<br>\n'
                '<input '
                + ('' if not self.field_type else ' type="'+self.field_type+'"')
                + ('' if not self.name_repeat else ' name="'+self.name_repeat+'"')
                + ('' if not self.autocomplete else ' autocomplete="'+self.autocomplete+'"')
                + '>')
        return html

    def update_value(self, value=None, repeat_value=None, request=None):
        if value is not None:
            self.value = value
        if repeat_value is not None:
            self.repeat_value = repeat_value
        elif request is not None and request.method== 'POST':
            self.value = request.form[self.name]
            self.repeat_value = request.form[self.name_repeat]
        else:
            return False
        return True


class emailField ( abstractField ):
    field_type = "Email"
    name = "email"

    def validate(self):
        return True


class selectField ( abstractField ):
    field_type = "select"
    options = []

    def validate(self):
        return True

    def __init__(self, options = None, name = None, value = None):
        if name is not None:
            self.name = name
        if options is not None and len(options) > 0:
            self.options = options
            self.value = options[0]['Value']
        if value is not None:
            self.value = value


    def get_html(self):
        html = ('<select'
                +('' if not self.name else ' name="'+self.name+'"')
                +('' if not self.value else ' value="'+self.value+'"')
                +'>\n')

        for option_dict in self.options:
            html += ('<option value="'+option_dict['Value']+'"'
                     +('selected="selected"' if (self.value == option_dict['Value']) else '')
                     +'>'
                     +option_dict['Key']
                     +'</option>\n')

        html += '</select>'
        return html


class uploadField ( abstractField ):
    field_type = "file"
    name = "upload"
    accept = None
    

    def validate(self):
        return True 

    def update_value(self,request = None):
        if request is not None and request.method == 'POST':
            if self.name in request.files:
                self.value = request.files[self.name]
                if self.value.filename == '':
                    self.value = None
                # if request.


    def get_html(self):
        return ('<input '
                + ('' if not self.field_type else ' type="'+self.field_type+'"')
                + ('' if not self.name else ' name="'+self.name+'"')
                + ('' if not self.accept else ' accept="'+self.accept+'"')
                + '>')

class imageField ( uploadField ):
    name = "image"
    accept = 'image/*'
    support_key = 'IMAGE'


class audioField ( uploadField ):
    name = "audio"
    accept = 'audio/*'
    support_key = 'AUDIO'
   

class hiddenField ( abstractField ):
    field_type ="hidden"

    def validate(self):
        return True

    

class abstractForm( object ):


    __metaclass__ = ABCMeta
    is_post = False
    fields = []
    # Must be of the following format
    # [{'Name': Name1, 'Field': Field1,
    #   'Name': Name2, 'Field': Field2,
    #   ...
    #   'Name': None, 'Field': submitField()}]

    def __init__(self,request=None):
        if request is not None:
            if request.method == 'POST':
                self.is_post = True
        if self.is_post:
            for field_dict in self.fields:
                if field_dict['Field'].name in request.form:
                    field_dict['Field'].value = request.form[field_dict['Field'].name]


    def validate(self):
        if not self.is_post:
            return False
        else:
            for field_dict in self.fields:
                if not field_dict['Field'].validate():
                    return False
        return True

    def get_html(self):
        html = ''
        for field_dict in self.fields:
            html += ('<div>' 
                     + ('' if not field_dict['Name'] else (field_dict['Name']+': '))
                     + field_dict['Field'].get_html()
                     + '</div> <br>\n' )
        return html

    def get_Info(self):
        result = {}
        for field_dict in self.fields:
            if field_dict['Name'] is not None:
                result[field_dict['Field'].name] = field_dict['Field'].get_Info()
        return result

class loginForm ( abstractForm ):
    fields = [{'Name':'Username','Field':textField(name = 'username', htmlClass="form-control")},
              {'Name':'Password','Field':passwordField(htmlClass = "form-control")},
              {'Name': None,'Field':submitField()}]

    def get_html(self):
        html = ''
        for field_dict in self.fields:
            html += ('<div>' 
                     + ('' if not field_dict['Name'] else (field_dict['Name']+': '))
                     + field_dict['Field'].get_html()
                     + '</div> <br>\n' )
        return html

class recover_password_Form ( abstractForm ):
    fields = [{'Name':'Email','Field':emailField(htmlClass="form-control")},
              {'Name': None,'Field':submitField()}]

    def get_html(self):
        html = ''
        for field_dict in self.fields:
            html += ('<div>' 
                     + ('' if not field_dict['Name'] else (field_dict['Name']+': '))
                     + field_dict['Field'].get_html()
                     + '</div> <br>\n' )
        return html    

supported_sides = {textField.support_key: textField,
                   imageField.support_key: imageField,
                   audioField.support_key: audioField}

class deckBuildForm ( abstractForm ):
    side_count_options = [{'Key': '2', 'Value': '2'},
                          {'Key': '3', 'Value': '3'},
                          {'Key': '4', 'Value': '4'}]

    side_type_options = [{'Key': 'Text', 'Value': textField.support_key},
                         {'Key': 'Image', 'Value': imageField.support_key},
                         {'Key': 'Audio', 'Value': audioField.support_key}]

    fields = [{'Name': 'Deck Name','Field':textField(name = 'deck_name')},
              {'Name': 'Number of Sides in Deck', 'Field':selectField(name='side_count',options=side_count_options)},
              {'Name': 'Side 1 Name','Field':textField(name = 'side_1_name')},
              {'Name': 'Side 1 Type', 'Field':selectField(name='side_1_type',options=side_type_options)},
              {'Name': 'Side 2 Name','Field':textField(name = 'side_2_name')},
              {'Name': 'Side 2 Type', 'Field':selectField(name='side_2_type',options=side_type_options)},
              {'Name': 'Side 3 Name','Field':textField(name = 'side_3_name')},
              {'Name': 'Side 3 Type', 'Field':selectField(name='side_3_type',options=side_type_options)},
              {'Name': 'Side 4 Name','Field':textField(name = 'side_4_name')},
              {'Name': 'Side 4 Type', 'Field':selectField(name='side_4_type',options=side_type_options)},
              {'Name': None,'Field':submitField()}]

    def get_Info(self):
        result = {}
        for field_dict in self.fields:
            if field_dict['Name'] == 'Deck Name':
                result[field_dict['Field'].name] = field_dict['Field'].get_Info()
            elif field_dict['Name'] == 'Number of Sides in Deck':
                temp_result = int((field_dict['Field'].get_Info()))
                result[field_dict['Field'].name] = temp_result

        side_info = []
        for i in range(1,result['side_count']+1):
            name_field = None
            type_field = None
            for field_dict in self.fields:
                if field_dict['Name'] is not None and ('Side '+str(i)+' Name') in field_dict['Name']:
                    name_field = field_dict['Field']
                if field_dict['Name'] is not None and ('Side '+str(i)+' Type') in field_dict['Name']:
                    type_field = field_dict['Field']    
            if name_field is not None and type_field is not None:

                side_info.append({'side_name':name_field.value,'side_type':type_field.value})

        result['side_info'] = side_info
        return result

class cubeBuildForm ( abstractForm ):


    fields = []
    is_post = False
    is_populated = False
    def __init__(self,request=None,deck_info=None):
        if deck_info is not None:
            self.fields = []
            for i in range(0,len(deck_info)):
                side_dict = deck_info[i]
                name = side_dict['side_name']
                self.fields.append({'Name':side_dict['side_name'],'Field':supported_sides[side_dict['side_type']](name=name)})
            self.fields.append({'Name': None,'Field':submitField()})
            self.is_populated = True
        if request is not None and request.method == 'POST':
            self.is_post = True
        if self.is_post and self.is_populated:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                if field_dict['Field'].name in request.form or field_dict['Field'].name in request.files:
                    field_dict['Field'].update_value(request=request)



class updatePasswordForm ( abstractForm ):
    fields = [{'Name':'Password','Field':passwordField(htmlClass="form-control")},
              {'Name':'Repeat Password','Field':passwordField(htmlClass="form-control")},
              {'Name': None,'Field':submitField()}]

    def __init__(self,request=None):
        if request.method == 'POST':
            self.is_post = True
        if request is not None and self.is_post:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                field_dict['Field'].update_value(request=request)

    def validate(self):
        if not self.is_post:
            return False
        else:
            for field_dict in self.fields:
                if not field_dict['Field'].validate():
                    return False
        if self.fields[0]['Field'].value != self.fields[1]['Field'].value:
            return False
        return True

class signupForm ( abstractForm ):
    fields = [{'Name':'Username','Field':textField(name = 'username',htmlClass="form-control", minlength='6')},
              {'Name':'Email','Field':emailField(htmlClass="form-control")},
              {'Name':'Password','Field':passwordField(htmlClass="form-control", minlength='6')},
              {'Name':'Repeat Password','Field':passwordField(htmlClass="form-control", minlength='6')},
              {'Name': None,'Field':submitField()}]

    def __init__(self,request=None):
        if request.method == 'POST':
            self.is_post = True
        if request is not None and self.is_post:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                field_dict['Field'].update_value(request=request)

    def validate(self):
        if not self.is_post:
            return False
        else:
            for field_dict in self.fields:
                if not field_dict['Field'].validate():
                    return False
        if self.fields[2]['Field'].value != self.fields[3]['Field'].value:
            return False
        return True


class emailVerificationForm ( abstractForm ):
    fields = [{'Name':'Username','Field':textField(name = 'username')},
              {'Name':'Email','Field':emailField()},
              {'Name': None,'Field':submitField()}]

    def __init__(self,request=None):
        if request.method == 'POST':
            self.is_post = True
        if request is not None and self.is_post:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                field_dict['Field'].update_value(request=request)



class deckUpdateForm ( abstractForm ):
    fields = [{'Name':'Profile Photo','Field':imageField(name = 'profile_photo')},
              {'Name': 'Deck Name','Field':textField(name = 'deck_name', value=None)},
              {'Name':'Description','Field':textArea(name = 'self_description', htmlClass = 'description_box', form='updateDeckForm', value=None)},
              {'Name': None,'Field':submitField(value='Update')}]

    def __init__(self,request=None, deck = None):
        if deck is not None:
            self.fields[1]['Field'].value = deck.name
            self.fields[2]['Field'].value = deck.self_description

        if request is not None and request.method == 'POST':
            self.is_post = True
        if self.is_post :
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                if field_dict['Field'].name in request.form or field_dict['Field'].name in request.files:
                    field_dict['Field'].update_value(request=request)

class profileUpdateForm ( abstractForm ):


    fields = [{'Name':'Profile Photo','Field':imageField(name = 'profile_photo')},
              {'Name':'About Me','Field':textArea(name = 'self_description')},
              {'Name': None,'Field':submitField()}]

    def __init__(self,request=None, user = None):
        if user is not None:
            self.fields[1]['Field'].value = user.self_description

        
        if request is not None and request.method == 'POST':
            self.is_post = True
        if self.is_post :
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                if field_dict['Field'].name in request.form or field_dict['Field'].name in request.files:
                    field_dict['Field'].update_value(request=request)

class forumForm ( abstractForm ):
    fields = [{'Name':'Forum Title','Field':textField(name = 'title')},
              {'Name':'Description of Forum','Field':textArea(name = 'description')},
              {'Name': None,'Field':submitField()}]

    def __init__(self,request=None):
        if request.method == 'POST':
            self.is_post = True
        if request is not None and self.is_post:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                field_dict['Field'].update_value(request=request)

class postForm ( abstractForm ):
    fields = [{'Name':'Forum Post Text','Field':textArea(name = 'post')},
              {'Name': None,'Field':submitField()}]

    def __init__(self,request=None):
        if request.method == 'POST':
            self.is_post = True
        if request is not None and self.is_post:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                field_dict['Field'].update_value(request=request)




class smartTesterForm ( abstractForm ):

    fields = []
    is_post = False
    is_populated = False
    test_input_options = [{'Key': 'Multiple Choice', 'Value': 'multiple_choice'},
                          {'Key': 'True False', 'Value': 'true_false'}]
    
    def __init__(self,request=None, flashdeck = None):
        if flashdeck is not None:
            deck_info = flashdeck.getSideInfo()
            self.fields = []
            options = []
            self.fields.append({'Name': None, 'Field':hiddenField(name='flashdeck_id',value=str(flashdeck.id))})

            for i in range(0,len(deck_info)):
                side_dict = deck_info[i]
                name = side_dict['side_name']
                options.append({'Key': name, 'Value': str(i)})

            self.fields.append({'Name': 'Question Side', 'Field':selectField(name='question_side',options=options)})
            self.fields.append({'Name': 'Answer Side', 'Field':selectField(name='answer_side',options=options)})
            self.fields.append({'Name': 'Answer Type', 'Field':selectField(name='answer_type',options=self.test_input_options)})

            self.fields.append({'Name': None,'Field':submitField(value='Start Smart Test')})
            self.is_populated = True
        if request is not None and request.method == 'POST':
            self.is_post = True
        if self.is_post and self.is_populated:
            for i in range(0,len(self.fields)):
                field_dict = self.fields[i]
                if field_dict['Field'].name in request.form or field_dict['Field'].name in request.files:
                    field_dict['Field'].update_value(request=request)

if __name__== '__main__':
    print('testing')

    # field1 = textField()
    # print(field1.get_html())
    # field1.field_value = 'valcoral'
    # print(field1.get_html())
    # print(textField.init_with_info('username','lisa').get_html())
    # print(textField.init_with_info('flavor').get_html())
    # field2 = submitField()
    # print(field2.get_html())
    # field3 = passwordField()
    # print(field3.get_html())
    # field4 = emailField()
    # print(field4.get_html())

    # print(loginForm().get_html())
    print(verifiedPasswordField().get_html())


