from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators, SelectField, FileField

class loginForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    password     = PasswordField('Password')
    submit       = SubmitField ('Submit')


class signupForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    password     = PasswordField('Password')
    passwordRepeat     = PasswordField('Repeat Password')
    email        = StringField('Email', [validators.Length(min=4, max=100)])
    submit       = SubmitField ('Submit')

class emailVerificationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    email        = StringField('Email', [validators.Length(min=4, max=100)])
    submit       = SubmitField ('Submit')

class deckBuildForm(Form):
    deckName = StringField('Deck Name', [validators.Length(min=4, max=25)])
    sideCount = SelectField('Number of Sides', choices=[('2',2),('3',3),('4',4)])#default=2
    side1Type = SelectField('Side 1 Type', choices=[('TEXT','Text'),('IMAGE','Image'),('AUDIO','Audio')])
    side2Type = SelectField('Side 2 Type', choices=[('TEXT','Text'),('IMAGE','Image'),('AUDIO','Audio')])
    side3Type = SelectField('Side 3 Type', choices=[('TEXT','Text'),('IMAGE','Image'),('AUDIO','Audio')])
    side4Type = SelectField('Side 4 Type', choices=[('TEXT','Text'),('IMAGE','Image'),('AUDIO','Audio')])
    side1Name = StringField('Side 1 Name', [validators.Length(min=1, max=25)])
    side2Name = StringField('Side 2 Name', [validators.Length(min=1, max=25)])
    side3Name = StringField('Side 3 Name', [validators.Length(min=1, max=25)])
    side4Name = StringField('Side 4 Name', [validators.Length(min=1, max=25)])

    submit       = SubmitField ('Submit')

    def getSideInfo(self):
        sides = int(self.sideCount.data)
        sideInfo = []
        sideInfo.append({"SideName":self.side1Name.data,"SideType":self.side1Type.data})
        sideInfo.append({"SideName":self.side2Name.data,"SideType":self.side2Type.data})
        sideInfo.append({"SideName":self.side3Name.data,"SideType":self.side3Type.data})
        sideInfo.append({"SideName":self.side4Name.data,"SideType":self.side4Type.data})
        return sideInfo[0:sides]

class flashCubeForm(Form):
    side1ImageFile        = FileField(u'Side 1 Image File')
    side2ImageFile        = FileField(u'Side 2 Image File')
    side3ImageFile        = FileField(u'Side 3 Image File')
    side4ImageFile        = FileField(u'Side 4 Image File')

    side1AudioFile        = FileField(u'Side 1 Audio File')
    side2AudioFile        = FileField(u'Side 2 Audio File')
    side3AudioFile        = FileField(u'Side 3 Audio File')
    side4AudioFile        = FileField(u'Side 4 Audio File')

    side1Text = StringField('Side 1 Text', [validators.Length(min=1, max=205)])
    side2Text = StringField('Side 2 Text', [validators.Length(min=1, max=205)])
    side3Text = StringField('Side 3 Text', [validators.Length(min=1, max=205)])
    side4Text = StringField('Side 4 Text', [validators.Length(min=1, max=205)])

    submit       = SubmitField ('Submit')

    def getFields(self, sideInfo):
        sideDict = [{'TEXT':self.side1Text, 'AUDIO':self.side1AudioFile, 'IMAGE':self.side1ImageFile},
                    {'TEXT':self.side2Text, 'AUDIO':self.side2AudioFile, 'IMAGE':self.side2ImageFile},
                    {'TEXT':self.side3Text, 'AUDIO':self.side3AudioFile, 'IMAGE':self.side3ImageFile},
                    {'TEXT':self.side4Text, 'AUDIO':self.side4AudioFile, 'IMAGE':self.side4ImageFile}]
        fields = []

        for i in range(0,len(sideInfo)):
            fields.append({'sideName':sideInfo[i]['SideName'],'sideField':sideDict[i][sideInfo[i]['SideType']]})


        return fields

    @classmethod
    def validatedResults(cls, request):

        fields = cls(request.form).getFields()
        print(fields)
        return cls(request.form)

class cubeForm():
    sides = {}

    def __init__(self):
        return 0

    def __init__(self, sideInfo): 
        for side in sideInfo:
            self.sides[side['SideName']] = side['SideType']


        




