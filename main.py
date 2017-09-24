# coding: UTF-8
from flask import Flask , render_template, session, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from siteForms import loginForm
from siteForms import signupForm
from siteForms import emailVerificationForm
from siteForms import deckBuildForm
from siteForms import deckUpdateForm
from siteForms import profileUpdateForm
from siteForms import cubeBuildForm
from siteForms import forumForm
from siteForms import postForm
from siteForms import smartTesterForm
from siteForms import recover_password_Form
from siteForms import updatePasswordForm
import configmodule
import os
import pickle
# from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import datetime
from google.cloud import storage
import time
from flask import Markup
from google.cloud.storage import Blob
import random
import urllib
from werkzeug.security import generate_password_hash, check_password_hash
from google.appengine.api import mail
from google.appengine.api import images
from PIL import Image, ExifTags



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.from_object('configmodule.ProductionConfig')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
url_time_serializer = URLSafeTimedSerializer(app.secret_key, salt='activate-salt')


# app.config.update(
#     DEBUG=True,
#     #EMAIL SETTINGS
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=465,
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME = 'memflash.dev@gmail.com',
#     MAIL_PASSWORD = 'devpassword'
#     )




# mail = Mail(app)

flashdecks = db.Table('flashdecks',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('flashdeck_id', db.Integer, db.ForeignKey('flashdeck.id')))

favorite_decks = db.Table('favorite_decks',
                db.Column('favoritedby_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('flashdeck_id', db.Integer, db.ForeignKey('flashdeck.id')))


activity_events = db.Table('activity_events',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('event_id', db.Integer, db.ForeignKey('event.id')))


def send_mail_from_app(subject = None, message = None, destination = None):
    print subject
    print message
    print destination
    if message is not None and subject is not None and destination is not None:
        temp_message = mail.EmailMessage(
            sender='memflash.dev@gmail.com',
            subject=subject)

        temp_message.to = destination
        temp_message.html = message
        temp_message.send()


class search_result():
    match_strength_index = 0
    title = 'N/A'
    link = '/'
    description = 'N/A'
    image = None
    owner = None

    def __init__(self,match_strength_index = None, title = None, link = None, description = None, image = None, owner = None):
        self.match_strength_index = match_strength_index
        self.title = title
        self.link = link
        self.description = description
        self.image = image
        self.owner = owner

    @classmethod
    def sort(cls, search_result_list = None):
        if search_result_list == None or len(search_result_list) == 0:
            return None
        else:
            temp_list = search_result_list

        return temp_list


class event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    event_text = db.Column(db.String(1000))

    def __init__(self, event_text): 
        
        self.time = datetime.datetime.now()
        if event_text is None:
            self.event_text = 'Something happened'
        else:
            self.event_text = event_text



    @classmethod
    def newCardEvent(cls,user = None,flashcube = None,flashdeck = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' added a new ' 
                     +('card' if not flashcube else ('<a href="/flashcube_profile/'+str(flashcube.id)+'">card</a>'))
                     + ' to '
                     +('a deck' if not flashdeck else ('<a href="/flashdeck_profile/'+str(flashdeck.id)+'">'+flashdeck.name+'</a>'))
                     +'.</p>')
        return cls(event_text=event_text)

    @classmethod
    def deleteCardEvent(cls,user = None,flashdeck = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' deleted a card from ' 
                     +('a deck' if not flashdeck else ('<a href="/flashdeck_profile/'+str(flashdeck.id)+'">'+flashdeck.name+'</a>'))
                     +'.</p>')
        return cls(event_text=event_text)

    @classmethod
    def makeDeckEvent(cls,user = None,flashdeck = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' made a deck ' 
                     +('' if not flashdeck else ('called <a href="/flashdeck_profile/'+str(flashdeck.id)+'">'+flashdeck.name+'</a>'))
                     +'.</p>')
        return cls(event_text=event_text)

    @classmethod
    def deleteDeckEvent(cls,user = None, flashdeck_name = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' deleted a deck called '+str(flashdeck_name)+'.</p>')
        return cls(event_text=event_text)

    @classmethod
    def updateDeckEvent(cls,user = None, flashdeck = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' updated the information of a deck'
                     +('' if not flashdeck else (' called <a href="/flashdeck_profile/'+str(flashdeck.id)+'">'+flashdeck.name+'</a>'))
                     +'.</p>')
        return cls(event_text=event_text)

    @classmethod
    def updateProfileEvent(cls,user = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' updated their profile information.</p>')
        return cls(event_text=event_text)

    @classmethod
    def favoriteDeckEvent(cls,user = None, flashdeck = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' favorited a deck'
                     +('' if not flashdeck else (' called <a href="/flashdeck_profile/'+str(flashdeck.id)+'">'+flashdeck.name+'</a>'))
                     +'.</p>')
        return cls(event_text=event_text)

    @classmethod
    def unfavoriteDeckEvent(cls,user = None, flashdeck = None):
        event_text = ('<p>'
                     +('Someone' if not user else ('<a href="/profile/'+user.username+'">'+user.username+'</a>'))
                     + ' unfavorited a deck'
                     +('' if not flashdeck else (' called <a href="/flashdeck_profile/'+str(flashdeck.id)+'">'+flashdeck.name+'</a>'))
                     +'.</p>')
        return cls(event_text=event_text)

class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime)
    post = db.Column(db.String(10000))
    forum_id = db.Column(db.Integer, db.ForeignKey( 'forum.id' ))
    user_id = db.Column(db.Integer, db.ForeignKey( 'user.id' ))

    def __init__(self, post = None): 
        
        self.creation_time = datetime.datetime.now()
        if post is not None:
            self.post = post
        else:
            self.description = "No Post Given"
        

    

class forum(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime)
    title = db.Column(db.String(1000))
    recent_update_time = db.Column(db.DateTime)
    description = db.Column(db.String(1000))
    posts = db.relationship( 'post' , backref='forum', lazy='select' )
    user_id = db.Column(db.Integer, db.ForeignKey( 'user.id' ))

    def __init__(self, description = None, title = None): 
        
        self.creation_time = datetime.datetime.now()
        self.recent_update_time = datetime.datetime.now()
        if description is not None:
            self.description = description
        else:
            self.description = "No Description Given"
        if title is not None:
            self.title = title
        else:
            self.title = 'Forum Created on '+str(self.creation_time)

    def add_post(self,post):
        self.posts.append(post)
        self.recent_update_time = datetime.datetime.now()

    @classmethod
    def getForumnList(cls):
        return cls.query.order_by(forum.recent_update_time.desc())

    @classmethod
    def get_by_id(cls,id_number):
        return cls.query.filter_by(id=id_number).first() 

    def get_post_count(self):  
        return len(self.posts)

    

    

            
            

    post_count = property(get_post_count)


# Need to encrypt passwords at some point
class user(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(80), unique=True) 
    password = db.Column(db.String(500)) 
    email = db.Column(db.String(120), unique=True)
    flashdecks = db.relationship('flashdeck', secondary = flashdecks,backref=db.backref('user', lazy='select'))
    is_confirmed = db.Column(db.Boolean)
    registered_on = db.Column(db.DateTime)
    confirmed_on = db.Column(db.DateTime)
    self_description = db.Column(db.String(1000))
    profile_photo = db.Column(db.String(1000))
    favorite_decks = db.relationship('flashdeck', secondary = favorite_decks,backref=db.backref('favoritedby', lazy='select'))
    events = db.relationship('event', order_by="event.time.desc()", secondary = activity_events,backref=db.backref('user', lazy='select'))
    forums = db.relationship( 'forum' , backref=db.backref('creator', lazy='select') )
    posts = db.relationship( 'post' , backref=db.backref('poster', lazy='select') )
    smartdeckprofiles = db.relationship( 'smartdeckprofile' , backref=db.backref('user', lazy='select') )

    def __init__(self, username, email, password): 
        self.username = username 
        self.email = email
        self.set_password(password)
        self.registered_on = datetime.datetime.now()
        self.profile_photo = 'DATETIME_2017-06-06 01:37:51.427162SIDENUMBER__0'
        self.self_description = "I haven't filled this out yet"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


    def __repr__(self):
        return  '<User %r>'  % self.username

    def get_reset_password_link(self):
        serial_datetime = url_time_serializer.dumps(self.username, salt='recover-password')
        return "/password_reset/"+serial_datetime

    reset_link = property(get_reset_password_link)
        

    def smart_profile_for(self, flashdeck = None):
        temp_profile = None
        for profile in self.smartdeckprofiles:
            if profile.flashdeck.id == flashdeck.id:
                temp_profile = profile
        return temp_profile

    @classmethod
    def search(cls, search_string):
        results = cls.query.filter((user.username.ilike('%'+str(search_string)+'%')) 
                                   | (user.registered_on.ilike('%'+str(search_string)+'%'))
                                   | (user.self_description.ilike('%'+str(search_string)+'%')))
        search_result_list = list()
        for result in results:
            search_result_list.append(search_result(match_strength_index = 0.5, 
                                                    title = result.username , 
                                                    link = '/profile/'+result.username,
                                                    description = result.self_description,
                                                    image = result.profile))
        return search_result_list

    @classmethod
    def get(cls,id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_name(cls,username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_name_or_email(cls,username = None, email = None):
        return cls.query.filter((user.email == email) | (user.username == username)).first()

    @classmethod
    def get_by_name_and_email(cls,username,email):
        return cls.query.filter_by(username=username, email=email).first()


    def get_profile(self):  

        

        return 'https://storage.googleapis.com/memflash-167204.appspot.com/'+str(self.profile_photo)


            
            
        
    #need to add a delete to the old photo here
    def set_profile(self, profile_photo):
        if profile_photo is not None:
            tempsides = dict();
        

            storage_client = storage.Client(project='memflash-167204')
            bucket = storage_client.get_bucket('memflash-167204.appspot.com')

            encryption_key = 'Jasons Secret'
            blob_name = 'DATETIME_'+str(datetime.datetime.now())+'SIDENUMBER_'
            add_index = 0

            if not bucket.get_blob(blob_name=blob_name):
                while bucket.get_blob(blob_name=(blob_name+'_'+str(add_index))):
                    add_index += 1
                blob_name = blob_name+'_'+str(add_index)

            blob = Blob(blob_name, bucket, chunk_size = 262144)
            
            file_obj = profile_photo
            

            # print('File Obj Mode:'+str(file_obj.__dict__))
            blob.upload_from_file(file_obj)
            self.profile_photo = blob.name

            
            

    profile = property(get_profile, set_profile)


    def get_smartdeckprofile(self,flashdeck = None):
        if flashdeck is None:
            return None
        for smartprofile in self.smartdeckprofiles:
            if smartprofile.flashdeck.id == flashdeck.id:
                smartprofile.update()
                db.session.commit()
                return smartprofile
        newsmartprofile = smartdeckprofile(flashdeck = flashdeck, user = current_user)
        db.session.add(newsmartprofile)
        db.session.commit()
        return newsmartprofile

flashcubes  = db.Table('flashcubes',
                            db.Column('flashdeck_id', db.Integer, db.ForeignKey('flashdeck.id')),
                            db.Column('flashcube_id', db.Integer, db.ForeignKey('flashcube.id')))   

 


class smartdeckprofile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smartcardprofiles = db.relationship( 'smartcardprofile' , backref=db.backref('smartdeckprofile', lazy='select') )
    flashdeck_id = db.Column(db.Integer, db.ForeignKey( 'flashdeck.id' ))
    creation_time = db.Column(db.DateTime)
    recent_update_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey( 'user.id' ))

    def __init__(self, flashdeck = None, user = None): 
        
        self.creation_time = datetime.datetime.now()
        self.recent_update_time = datetime.datetime.now()
        self.flashdeck = flashdeck
        self.user = user
        if flashdeck is not None:
            self.flashdeck = flashdeck
            self.flashdeck.smartdeckprofiles.append(self)
            
        if user is not None:
            self.user = user
            self.user.smartdeckprofiles.append(self)
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_user_and_deck(cls, user = None, deck = None):
        if deck is None or user is  None:
            return None
        return cls.query.filter_by(user_id=user.id, flashdeck_id=deck.id).first()

    def reset_memory(self):
        for profile in self.smartcardprofiles:
            profile.knowledge_index = 1
    
    def get_update_profiles(self):  
        deck= self.flashdeck
        for profile in self.smartcardprofiles:
            deck_has_cube = False
            for flashcube in deck.flashcubes:
                if profile.flashcube.id == flashcube.id:
                    deck_has_cube = True
            if not deck_has_cube:
                self.smartcardprofiles.remove(profile)
                db.session.delete(profile)
                db.session.commit()
        for flashcube in deck.flashcubes:
            smartdeck_has_profile = False
            for profile in self.smartcardprofiles:
                if profile.flashcube.id == flashcube.id:
                    smartdeck_has_profile = True
            if not smartdeck_has_profile:
                temp_profile = smartcardprofile(smartdeckprofile = self, flashcube = flashcube)
                db.session.add(temp_profile)
                self.smartcardprofiles.append(temp_profile)
        return self.smartcardprofiles

    def update(self):
        deck= self.flashdeck

        ## first remove profiles we dont need
        for profile in self.smartcardprofiles:
            deck_has_cube = False
            for flashcube in deck.flashcubes:
                if profile.flashcube and profile.flashcube.id == flashcube.id:
                    deck_has_cube = True
            if not deck_has_cube:
                self.smartcardprofiles.remove(profile)
                db.session.delete(profile)
                db.session.commit()

        ## then add new profiles
        for flashcube in deck.flashcubes:
            smartdeck_has_profile = False
            for profile in self.smartcardprofiles:
                if profile.flashcube.id == flashcube.id:
                    smartdeck_has_profile = True
            if not smartdeck_has_profile:
                temp_profile = smartcardprofile(smartdeckprofile = self, flashcube = flashcube)
                db.session.add(temp_profile)

        return True


    def get_random_card(self, last_card_index = None):    
        smart_card_list = []
        smart_card_knowledge_index_random_weight_list = []
        self.update()
        for smartcardprofile in self.smartcardprofiles:
            smart_card_knowledge_index_random_weight_list.append(smartcardprofile.knowledge_index*random.random())
            smart_card_list.append(smartcardprofile)

        if smart_card_knowledge_index_random_weight_list[0] > smart_card_knowledge_index_random_weight_list[1]:
            temp_card_profile = smart_card_list[0]
            second_temp_card_profile = smart_card_list[1]
            max_weight = smart_card_knowledge_index_random_weight_list[0]
        else:
            temp_card_profile = smart_card_list[1]
            second_temp_card_profile = smart_card_list[0]
            max_weight = smart_card_knowledge_index_random_weight_list[1]
        for i in range(0,len(smart_card_knowledge_index_random_weight_list)):
            weight = smart_card_knowledge_index_random_weight_list[i]
            if weight > max_weight:
                second_temp_card_profile = temp_card_profile
                max_weight = weight
                temp_card_profile = smart_card_list[i]

        if last_card_index is not None and temp_card_profile.flashcube.id != last_card_index:
            return temp_card_profile.flashcube
        else:
            return second_temp_card_profile.flashcube

        return random.choice(self.flashdeck.flashcubes)   
            
    def get_smartcard_from_cube(self, flashcube_id = None):
        if flashcube_id is None:
            return None
        for smartcardprofile in self.smartcardprofiles:
            # print(smartcardprofile.flashcube.id)
            if str(smartcardprofile.flashcube.id) == flashcube_id:
                return smartcardprofile
        return None

    def get_id_knowledge_dict(self):
        knowledge_dict = dict()
        for card in self.smartcardprofiles:
            knowledge_dict[str(card.flashcube.id)] = {'STATUS':card.knowledge(), 'INDEX':card.knowledge_index}
        return knowledge_dict

    profiles = property(get_update_profiles)


fakecubes  = db.Table('fakecubes',
                            db.Column('smartcardprofile_id', db.Integer, db.ForeignKey('smartcardprofile.id')),
                            db.Column('flashcube_id', db.Integer, db.ForeignKey('flashcube.id')))  

class smartcardprofile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smartdeckprofile_id = db.Column(db.Integer, db.ForeignKey( 'smartdeckprofile.id' ))
    flashcube_id = db.Column(db.Integer, db.ForeignKey( 'flashcube.id' ))
    creation_time = db.Column(db.DateTime)
    recent_update_time = db.Column(db.DateTime)
    knowledge_index = db.Column(db.Float)
    fake_cubes = db.relationship('flashcube', secondary=fakecubes, backref=db.backref('fakecardprofile', lazy='dynamic'))


    def __init__(self, smartdeckprofile = None, flashcube = None): 
        
        self.creation_time = datetime.datetime.now()
        self.recent_update_time = datetime.datetime.now()
        self.flashdeck = flashdeck
        self.flashcube = flashcube
        self.knowledge_index = 1
        if smartdeckprofile is not None:
            self.smartdeckprofile = smartdeckprofile
        if flashcube is not None:
            self.flashcube = flashcube


    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_by_cube_id(cls, cube_id):
        return cls.query.filter_by(flashcube_id=cube_id).first()

    def known(self):

        self.knowledge_index = abs(self.knowledge_index)*.9 +.01
        return True

    def unknown(self):
        self.knowledge_index = (1-self.knowledge_index)*.1+self.knowledge_index - .01
        return True

    def knowledge(self):
        index = self.knowledge_index
        if index < 0.15:
            return 'COMPLETELY MEMORIZED'
        elif index < .3:
            return 'MOSTLY MEMORIZED'
        elif index < .5:
            return 'PARTIALLY MEMORIZED'
        elif index < .7:
            return 'STARTING TO MEMORIZE'
        else:
            return 'NOT MEMORIZED'

    def update_fake_cubes(self):
        self.fake_cubes = []
        count = 4
        if len(self.smartdeckprofile.smartcardprofiles) <5:
            count = len(self.smartdeckprofile.smartcardprofiles)
        new_index = int(random.random()*count)

        for i in range(0,count):
            if i == new_index:
                self.fake_cubes.append(self.flashcube)
            else:
                temp_profiles_list = []
                for profile in self.smartdeckprofile.smartcardprofiles:
                    if not (profile.flashcube in self.fake_cubes) and profile != self:
                        temp_profiles_list.append(profile)
                self.fake_cubes.append(random.choice(temp_profiles_list).flashcube)
        print('fake cubes are here')
        print(self.fake_cubes)





        
       

class flashdeck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    sideInfo = db.Column(db.PickleType)
    flashcubes = db.relationship('flashcube', secondary=flashcubes, backref=db.backref('flashdeck', lazy='dynamic'))
    self_description = db.Column(db.String(1000))
    profile_photo = db.Column(db.String(1000))
    smartdeckprofiles = db.relationship( 'smartdeckprofile' , backref=db.backref('flashdeck', lazy='select') )
    # profile_photo = '/static/papers-576385_1280.png'

    # sideInfo specifies the types of sides that the flashcubes have
    # sideInfo is of the following type:
    # sideInfo = [{"side_name":"SideName0", "side_type":"SideType0"},
    #             {"side_name":"SideName1", "side_type":"SideType1"},
    #             {"side_name":"SideName2", "side_type":"SideType2"},
    #             {"side_name":"SideName3", "side_type":"SideType3"}]
    #
    # sideInfo is limited to an array of size 4
    # This will be checked eventually but not now
    def __init__(self, name, sideInfo):
        self.name = name
        self.sideInfo = pickle.dumps(sideInfo)
        self.self_description = 'Lorem Ipsum'
        self.profile_photo = 'DATETIME_2017-06-11 02:39:45.900246SIDENUMBER__0'

    @classmethod
    def search(cls, search_string):
        results = cls.query.filter((flashdeck.name.ilike('%'+str(search_string)+'%')) 
                                   | (user.self_description.ilike('%'+str(search_string)+'%')))

        search_result_list = list()
        for result in results:
            search_result_list.append(search_result(match_strength_index = 0.5, 
                                                    title = result.name , 
                                                    link = '/flashdeck_profile/'+str(result.id),
                                                    description = result.self_description,
                                                    image = result.profile,
                                                    owner = result.user[0].username))
        return search_result_list



    def __repr__(self):
        return  '<Name ' + str(self.name)+' >'

    def getSideInfo(self):
        return  pickle.loads(self.sideInfo)

    def delete_cubes(self, db):
        for cube in self.flashcubes:
            db.session.delete(cube) # should add functionality to delete images and audio from cloud at some point
        db.session.commit()
        return True

    def add_cube(self, cube_info = None,db = None):
        if cube_info is not None:
            sides = {}
            side_info = self.getSideInfo()
            for i in range(0,len(side_info)):
                side_dict = side_info[i]
                sides[side_dict['side_name']]={'side_type':side_dict['side_type'],'side_value':cube_info[side_dict['side_name']]}

            new_cube = flashcube(sides)
            self.flashcubes.append(new_cube)
            db.session.add(new_cube)
            db.session.commit()
            return new_cube
        else: 
            return False

    @classmethod
    def get_by_id(cls,id_number):
        return cls.query.filter_by(id=id_number).first() 

    def get_html(self):
        html = '<ol>\n'

        for cube in self.flashcubes:
            html += '<li>\n'
            html += cube.get_html()
            html += '</li>\n'

        html += '</ol>'

        return html

    def get_profile(self):  
        return 'https://storage.googleapis.com/memflash-167204.appspot.com/'+str(self.profile_photo)
        
    #need to add a delete to the old photo here
    def set_profile(self, profile_photo):
        if profile_photo is not None:
            tempsides = dict();
        

            storage_client = storage.Client(project='memflash-167204')
            bucket = storage_client.get_bucket('memflash-167204.appspot.com')

            encryption_key = 'Jasons Secret'
            blob_name = 'DATETIME_'+str(datetime.datetime.now())+'SIDENUMBER_'
            add_index = 0

            if not bucket.get_blob(blob_name=blob_name):
                while bucket.get_blob(blob_name=(blob_name+'_'+str(add_index))):
                    add_index += 1
                blob_name = blob_name+'_'+str(add_index)

            blob = Blob(blob_name, bucket, chunk_size = 262144)
            
            file_obj = profile_photo
            blob.upload_from_file(file_obj)

            self.profile_photo = blob.name

    profile = property(get_profile, set_profile)

            

class flashcube(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sidePickle = db.Column(db.PickleType)
    secret = 'Jasons Secret'
    smartcardprofiles = db.relationship( 'smartcardprofile' , backref=db.backref('flashcube', lazy='select') )
    
    # sides should have the form of:
    # sides = {"SideName0": {"side_type":"SideType0", "side_value":"SideValue0"},
    #          "SideName1": {"side_type":"SideType1", "side_value":"SideValue1"},
    #          "SideName2": {"side_type":"SideType2", "side_value":"SideValue2"},
    #          "SideName3": {"side_type":"SideType3", "side_value":"SideValue3"}}
    # sides must be limited to 4 sides.
    # no type checking is done yet automatically in the class but that will be added
    # at one point. 
    def __init__(self, sides):
        tempsides = flashcube.upload_sides(sides)
        self.sidePickle = pickle.dumps(tempsides)
    
    def get_sides(self):
        tempsides= pickle.loads(self.sidePickle)
        for side_name in tempsides:
            image_url='https://storage.googleapis.com/memflash-167204.appspot.com/'
            if tempsides[side_name]['side_type'] == 'AUDIO' or tempsides[side_name]['side_type'] == 'IMAGE':
                tempsides[side_name]['side_value'] = image_url + str(tempsides[side_name]['side_value'])
        return tempsides

    def set_sides(self, sides):
        self.sidePickle = pickle.dumps(flashcube.upload_sides(sides))

    sides = property(get_sides, set_sides)

    @classmethod
    def upload_sides(cls, sides):
        tempsides = dict();
        count = 0
        for side_name in sides:
            count += 1
            # print sidename.encode('utf-8')
            # print sides[sidename]['Type']
            # print type(sides[sidename]['Value'][0])
            # print(sides[sidename]['Value'].encode('utf8'))
            if sides[side_name]['side_type'] == 'IMAGE' or sides[side_name]['side_type'] == 'AUDIO':

                storage_client = storage.Client(project='memflash-167204')
                # for bucket in storage_client.list_buckets():
                #     print(bucket)
                # print('hi')
                bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                # bucket.configure_website('index.html', '404.html')
                # bucket.make_public(recursive=True, future=True)
                encryption_key = 'Jasons Secret'
                blob_name = 'DATETIME_'+str(datetime.datetime.now())+'SIDENUMBER_'+str(count)
                add_index = 0
                if not bucket.get_blob(blob_name=blob_name):
                    while bucket.get_blob(blob_name=(blob_name+'_'+str(add_index))):
                        add_index += 1
                    blob_name = blob_name+'_'+str(add_index)

                blob = Blob(blob_name, bucket, chunk_size = 262144)
                
                file_obj = sides[side_name]['side_value']
                blob.upload_from_file(file_obj)

                tempsides[side_name] = {"side_type":sides[side_name]['side_type'], "side_value":blob.name}
            elif sides[side_name]['side_type'] == 'TEXT':  
                value =  sides[side_name]['side_value']
                # value = value.decode('utf-8')
                tempsides[side_name] = {"side_type":sides[side_name]['side_type'], "side_value":sides[side_name]['side_value']}
            else:
                tempsides[side_name] = {"side_type":sides[side_name]['side_type'], "side_value":sides[side_name]['side_value']}


        return tempsides

    def __repr__(self):
        return  '<flashcube, sideCount='+str(len(pickle.loads(self.sidePickle)))+'>'

    def getSides(self):
        return pickle.loads(self.sidePickle)

    def get_html(self):
        html = "<div>\n"
        sides = self.getSides()
        for side in sides:
            html += ("<div>\n"
                     + '<h1> Side: '+str(side)+'</h1>\n')
            if sides[side]['side_type'] == 'TEXT':
                html += '<h2>'+ str(sides[side]['side_value'].encode('utf-8')) + '</h2>\n'
            elif sides[side]['side_type'] == 'IMAGE':
                # storage_client = storage.Client(project='memflash-167204')
                # bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                # blob = bucket.get_blob(sides[side]['side_value'])
                # html += '<img src="'+blob.public_url+'" alt="Image File">'
                image_url='https://storage.googleapis.com/memflash-167204.appspot.com/'+str(sides[side]['side_value'])
                html += '<img src="'+image_url+'" alt="Image File">'
            elif sides[side]['side_type'] == 'AUDIO':
                # storage_client = storage.Client(project='memflash-167204')
                # bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                # blob = bucket.get_blob(sides[side]['side_value'])
                # html += ('<audio controls>'
                #          + '<source src="'+blob.public_url + '" >\n'
                #          + 'Your browser does not support the audio tag.\n'
                #          + '</audio>\n')
                audio_url='https://storage.googleapis.com/memflash-167204.appspot.com/'+str(sides[side]['side_value'])
                html += ('<audio controls>'
                         + '<source src="'+audio_url + '" >\n'
                         + 'Your browser does not support the audio tag.\n'
                         + '</audio>\n')
            else:
                html += '<h2> Undefined Side </h2>\n'
            html += "</div>\n"

        html += "</div>"

        return html

    def get_side_html(self, side=None):
        html = "<div>\n"
        sides = self.getSides()
        if side is not None and side in sides:
            html += ("<div>\n"
                     + '<h1> Side: '+str(side)+'</h1>\n')
            if sides[side]['side_type'] == 'TEXT':
                html += '<h2>'+ str(sides[side]['side_value'].encode('utf-8')) + '</h2>\n'
            elif sides[side]['side_type'] == 'IMAGE':
                # storage_client = storage.Client(project='memflash-167204')
                # bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                # blob = bucket.get_blob(sides[side]['side_value'])
                # html += '<img src="'+blob.public_url+'" alt="Image File">'
                image_url='https://storage.googleapis.com/memflash-167204.appspot.com/'+str(sides[side]['side_value'])
                html += '<img src="'+image_url+'" alt="Image File">'
            elif sides[side]['side_type'] == 'AUDIO':
                # storage_client = storage.Client(project='memflash-167204')
                # bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                # blob = bucket.get_blob(sides[side]['side_value'])
                # html += ('<audio controls>'
                #          + '<source src="'+blob.public_url + '" >\n'
                #          + 'Your browser does not support the audio tag.\n'
                #          + '</audio>\n')
                audio_url='https://storage.googleapis.com/memflash-167204.appspot.com/'+str(sides[side]['side_value'])
                html += ('<audio controls>'
                         + '<source src="'+audio_url + '" >\n'
                         + 'Your browser does not support the audio tag.\n'
                         + '</audio>\n')
            else:
                html += '<h2> Undefined Side </h2>\n'
            html += "</div>\n"
        html += "</div>"

        return html

    def get_html_without_side(self, without_side=None):
        html = "<div>\n"
        sides = self.getSides()
        for side in sides:
            if without_side is not None and without_side != side:

                html += ("<div>\n"
                         + '<h1> Side: '+str(side)+'</h1>\n')
                if sides[side]['side_type'] == 'TEXT':
                    html += '<h2>'+ str(sides[side]['side_value'].encode('utf-8')) + '</h2>\n'
                elif sides[side]['side_type'] == 'IMAGE':
                    # storage_client = storage.Client(project='memflash-167204')
                    # bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                    # blob = bucket.get_blob(sides[side]['side_value'])
                    # html += '<img src="'+blob.public_url+'" alt="Image File">'
                    image_url='https://storage.googleapis.com/memflash-167204.appspot.com/'+str(sides[side]['side_value'])
                    html += '<img src="'+image_url+'" alt="Image File">'
                elif sides[side]['side_type'] == 'AUDIO':
                    # storage_client = storage.Client(project='memflash-167204')
                    # bucket = storage_client.get_bucket('memflash-167204.appspot.com')
                    # blob = bucket.get_blob(sides[side]['side_value'])
                    # html += ('<audio controls>'
                    #          + '<source src="'+blob.public_url + '" >\n'
                    #          + 'Your browser does not support the audio tag.\n'
                    #          + '</audio>\n')
                    audio_url='https://storage.googleapis.com/memflash-167204.appspot.com/'+str(sides[side]['side_value'])
                    html += ('<audio controls>'
                             + '<source src="'+audio_url + '" >\n'
                             + 'Your browser does not support the audio tag.\n'
                             + '</audio>\n')
                else:
                    html += '<h2> Undefined Side </h2>\n'
                html += "</div>\n"
        html += "</div>"

        return html

    @classmethod
    def get_by_id(cls,id_number):
        return cls.query.filter_by(id=id_number).first() 

 



db.create_all()    

db.session.commit()


@login_manager.user_loader
def load_user(user_id): 
    return user.get(user_id)



@app.route("/static_file/<filename>")
@login_required
def static_file(filename):
    return "<h1>This is memFlash!</h1><p>Decks Page</p><a href=/logout>Logout</a> <a href=/>Home</p>"

@app.route("/search", methods=["GET", "POST"])
@app.route("/search/<page>", methods=["GET", "POST"])

@login_required
def search(search_query = None, search_type='all', page =1):
    results_per_page = 5
    if request.method == 'POST' and 'search_type' in request.form.keys():
        search_type = request.form['search_type']
    if request.method == 'POST' and 'search_query' in request.form.keys():
        search_query = request.form['search_query']


        return redirect(url_for('search', page=page, search_query = search_query, search_type = search_type))
    if 'search_query' in request.values:
        search_query = request.values['search_query']
    if 'search_type' in request.values:
        search_type = request.values['search_type']

    search_results = None
    end_page = 1

    page=int(page)
    search_url = request.full_path.replace(request.path,"",1)

    if search_query is not None:
        user_search_list = user.search(search_query)
        deck_search_list  = flashdeck.search(search_query)
        # deck_search_list = list()
        if search_type == 'decks':
            search_results = search_result.sort(deck_search_list)
        elif search_type == 'users':
            search_results = search_result.sort(user_search_list)
        else:   
            search_results = search_result.sort(user_search_list + deck_search_list)

        if not search_results:
            search_results = list()
        else:
            search_results = search_results[(int(page)-1)*results_per_page:int(page)*results_per_page]
            total_events = len(search_results)
            end_page = (total_events - (total_events % results_per_page))/results_per_page + 1

        # search_url = request
    return render_template('search.html', user=current_user, search_query = search_query, search_results = search_results, search_type = search_type, end_page=end_page, page=page, search_url = search_url)


@app.route("/")
def welcome():
    if(current_user.is_authenticated is True):
        return redirect('/profile/'+current_user.username)
    return render_template('index.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route("/profile")
@app.route("/profile/<username>")
@login_required
def profile(username = None):
    profile_update_form = profileUpdateForm(user=current_user)
    
    if username is None:
        return redirect('/profile/'+current_user.username)
    else:
        tempuser = user.get_by_name(username)
        if tempuser is not None:
            current_user.events
            return render_template('profile.html', user=tempuser, profile_update_form=Markup(profile_update_form.get_html()))
        else:
            return render_template('error.html')

@app.route("/forum_page/<forum_id>", methods=['GET','POST'])
@login_required
def forum_page(forum_id = None, page = 1):
    results_per_page = 10
    if forum_id is None and forum.get_by_id(forum_id) is not None:
        flash('That is an invalid forum id.')
        return redirect('forums') 
    temp_forum = forum.get_by_id(forum_id)
    form = postForm(request=request)
    
    if request.method == 'POST':
        if form.validate():
            info = form.get_Info()
            temp_post = post(post = info['post'])
            temp_post.forum = temp_forum
            temp_forum.add_post(temp_post)
            temp_post.creator = current_user
            current_user.posts.append(temp_post)
            db.session.add(temp_post)
            db.session.commit()
            end_page = (len(temp_forum.posts)-len(temp_forum.posts)%results_per_page)/results_per_page +1
            return redirect(url_for('forum_page',forum_id=forum_id, page = end_page))

    form = postForm(request=request)
    end_page = (len(temp_forum.posts)-len(temp_forum.posts)%results_per_page)/results_per_page +1
    if 'page' in request.values and int(request.values['page']) <= end_page and int(request.values['page']) >=1:
        page = int(request.values['page'])
    else:
        return redirect(url_for('forum_page',forum_id=forum_id, page = 1))
    print(end_page)
    pagination_url_dict = []
    if page == 1:
        pagination_url_dict.append(url_for('forum_page',forum_id=forum_id, page = 1))
    else:
        pagination_url_dict.append(url_for('forum_page',forum_id=forum_id, page = page-1))
    pagination_url_dict.append(url_for('forum_page',forum_id=forum_id, page = page))
    if page == end_page:
        pagination_url_dict.append(url_for('forum_page',forum_id=forum_id, page = end_page))
    else:
        pagination_url_dict.append(url_for('forum_page',forum_id=forum_id, page = page+1))
    print(pagination_url_dict)




    return render_template('forum_page.html', user = current_user, forum = temp_forum, post_form = Markup(form.get_html()), page = page, end_page = end_page, pagination_url_dict = pagination_url_dict, results_per_page=results_per_page)

@app.route("/forums", methods=['GET','POST'])
@login_required
def forums():
    
    forums = forum.getForumnList()
    forum_form = forumForm(request = request)
    if request.method == 'POST':
        if forum_form.validate():
            info = forum_form.get_Info()
            new_forum = forum(title = info['title'], description = info['description'])
            new_forum.creator = current_user
            current_user.forums.append(new_forum)
            db.session.add(new_forum)
            db.session.commit()

    forum_form = Markup(forum_form.get_html())
    return render_template('forums.html', user = current_user, forums = forums, forum_form=forum_form)

@app.route("/user_update/<user_id>", methods=['GET','POST'])
@login_required
def user_update(user_id = None):
    profile_update_form = profileUpdateForm(user=current_user, request = request)
    if profile_update_form.validate():
        info = profile_update_form.get_Info()
        if info['profile_photo'] is not None:
            current_user.profile = info['profile_photo']
        current_user.self_description = info['self_description']
        db.session.commit()
        new_event = event.updateProfileEvent(user=current_user)
        current_user.events.append(new_event)
        db.session.add(new_event)
        db.session.commit()
    #     print(info['profile_photo'])
    #     print(info['self_description'])
    # print(profile_update_form.get_Info())
    
    return redirect('/profile/'+current_user.username)
@app.route("/profile/<username>/activity_log/")    
@app.route("/profile/<username>/activity_log/<page>")
@login_required
def activity_log(username = None, page=1):
    rows_per_page = 10
    page = int(page)


    if username is None:
        flash('Must specify a user to se an activity log')
        return redirect('/profile/'+current_user.username)
    else:
        tempuser = user.get_by_name(username)
        if tempuser is not None:
            total_events = len(tempuser.events)
            end_page = (total_events - (total_events % rows_per_page))/rows_per_page + 1
            if page > end_page or page < 1:
                return redirect('/profile/'+str(username)+'/activity_log/')
            events = tempuser.events[rows_per_page*((page)-1):rows_per_page*int(page)]
            return render_template('activity_log.html', user=tempuser, events=events, end_page=end_page, page=page)
        else:
            return render_template('error.html')


@app.route("/profile/<username>/deckbook", methods=["GET","POST"])
@login_required
def deckbook(username = None):
    form = deckBuildForm(request)

    tempuser = user.get_by_name(username)
    flashdecks = []
    if tempuser is None:
        return render_template('error.html')
    if current_user.is_authenticated:
        flashdecks = tempuser.flashdecks
    if request.method == "POST":
        if form.validate():
            deck_name = form.get_Info()['deck_name']
            side_info = form.get_Info()['side_info']
            newDeck = flashdeck(deck_name,side_info)
        
        for deck in current_user.flashdecks:
            if deck.name == newDeck.name:
                flash('You already have a deck with that name')
                return render_template('deckbook.html', user=tempuser, decks = flashdecks, form = Markup(form.get_html()) )
        

        
        db.session.add(newDeck)
        db.session.commit()
        current_user.flashdecks.append(newDeck)
        db.session.commit()

        new_event = event.makeDeckEvent(user = current_user, flashdeck=newDeck)
        db.session.add(new_event)
        current_user.events.append(new_event)

        db.session.commit()
        db.session.flush()

        return redirect('/flashdeck_profile/'+str(newDeck.id)+'')

    print tempuser.flashdecks 
    return render_template('deckbook.html', user=tempuser, decks = flashdecks, form = Markup(form.get_html()) )

@app.route("/profile/<username>/favorite_decks", methods=["GET","POST"])
@login_required
def favorite_decks(username = None):
    form = deckBuildForm(request)

    tempuser = user.get_by_name(username)
    favorite_decks = []
    if tempuser is None:
        return render_template('error.html')
    if current_user.is_authenticated:
        favorite_decks = tempuser.favorite_decks
    if request.method == "POST":
        if form.validate():
            deck_name = form.get_Info()['deck_name']
            side_info = form.get_Info()['side_info']
            newDeck = flashdeck(deck_name,side_info)
        
        for deck in current_user.favorite_decks:
            if deck.name == newDeck.name:
                flash('You already have a deck with that name')
                return render_template('favorite_decks.html', user=tempuser, decks = favorite_decks, form = Markup(form.get_html()) )
        current_user.favorite_decks.append(newDeck)
        db.session.add(newDeck)
        db.session.commit()

        return redirect('/flashdeck_profile/'+str(newDeck.id)+'')
        
    return render_template('favorite_decks.html', user=tempuser, decks = favorite_decks, form = Markup(form.get_html()) )

@app.route("/add_deck_to_favorites/<flashdeck_id>", methods=["GET","POST"])
@login_required
def add_deck_to_favorites(flashdeck_id = None):
    deck = flashdeck.get_by_id(flashdeck_id)
    if deck is None:
        flash('Not A Valid Deck!')
        redirect('/profile/'+str(current_user.username))
    has_deck = False
    for tempdeck in current_user.favorite_decks:
        if tempdeck.id == deck.id:
            flash('You already have favorited this deck!')
            has_deck = True
    for tempdeck in current_user.flashdecks:
        if tempdeck.id == deck.id:
            flash('You cannot favorite your own deck!')
            has_deck = True
    if not has_deck:
        current_user.favorite_decks.append(deck)
        db.session.commit()
        new_event = event.favoriteDeckEvent(user=current_user,flashdeck=deck)
        current_user.events.append(new_event)
        db.session.add(new_event)
        db.session.commit()
    
    return redirect('/flashdeck_profile/'+str(flashdeck_id))


@app.route("/remove_deck_from_favorites/<flashdeck_id>", methods=["GET","POST"])
@login_required
def remove_deck_from_favorites(flashdeck_id = None):
    deck = flashdeck.get_by_id(flashdeck_id)
    if deck is None:
        flash('Not A Valid Deck!')
        redirect('/profile/'+str(current_user.username))
    has_deck = False
    for tempdeck in current_user.favorite_decks:
        if tempdeck.id == deck.id:
            flash('You already have favorited this deck!')
            has_deck = True
    for tempdeck in current_user.flashdecks:
        if tempdeck.id == deck.id:
            flash('You cannot favorite your own deck!')
            has_deck = True
    if has_deck:
        current_user.favorite_decks.remove(deck)
        db.session.commit()
        new_event = event.unfavoriteDeckEvent(user=current_user,flashdeck=deck)
        current_user.events.append(new_event)
        db.session.add(new_event)
        db.session.commit()
    
    return redirect('/flashdeck_profile/'+str(flashdeck_id))

@app.route("/login",methods=["GET","POST"])
def login(): 
    if current_user.is_authenticated:
        flash('You cannot login when you are currently logged in.')
        return redirect('/profile')
    form = loginForm(request=request)
    next = ('/profile' if not request.args.get('next') else request.args.get('next'))
    resend = False
    submit_url = request.url.replace(request.url.split('/login')[0],'',1)
    if request.method == 'POST':
        temp_user = None
        if form.validate(): 
            username = form.get_Info()['username']
            password = form.get_Info()['password']
            temp_user = user.get_by_name(username)
        
        if temp_user is not None and temp_user.check_password(password):
            if temp_user.is_confirmed:
                login_user(temp_user)
            else:
                flash('Your account has not been verified yet.')
                resend = True
                return render_template('loginPage.html',form = Markup(form.get_html()), submit_url = submit_url, resend = resend)
        else:
            flash('Invalid username or password. Please try logging in again.')

        return redirect(next)


    return render_template('loginPage.html',form = Markup(form.get_html()), submit_url = submit_url, resend = resend)


@app.route("/resend_email",methods=["GET","POST"])
def resend_email(): 
    form = recover_password_Form(request=request)
    # next = ('/profile' if not request.args.get('next') else request.args.get('next'))
    # resend = False
    submit_url = request.url.replace(request.url.split('/resend_email')[0],'',1)

    if request.method == 'POST':
        temp_user = None
        if form.validate(): 
            email = form.get_Info()['email']
            temp_user = user.get_by_name_or_email(email=email)
        
        if temp_user is not None:
            if temp_user.is_confirmed:
                flash('You have already confirmed your account and can login.')
                return redirect('/login')
            else:
              #   msg = Message(
              # 'Welcome To MemFlash',
              #  sender='memflash.dev@gmail.com',
              #  recipients=temp_user.email)
                serial_datetime = url_time_serializer.dumps(temp_user.username, salt='account-activate')
                confirmationLink = request.environ['HTTP_ORIGIN']+"/confirm/ACTIVATE/"+serial_datetime
                temp_message = render_template('confirmation_email.html', signupName = temp_user.username, confirmationLink = confirmationLink)
                # mail.send(msg)
                send_mail_from_app(subject = 'Email Confirmation', message = temp_message, destination = temp_user.email)
                flash('We are resending your confirmation email.')
                return redirect('/')
        else:
            flash('Invalid email. Please try again.')

    return render_template('resend_email.html',form = Markup(form.get_html()), submit_url=submit_url)


@app.route("/recover_password",methods=["GET","POST"])
def recover_password(): 
    if current_user.is_authenticated:
        flash('You cannot recover a password when you are currently logged in.')
        return redirect('/profile')
    form = recover_password_Form(request=request)
    # next = ('/profile' if not request.args.get('next') else request.args.get('next'))
    if request.method == 'POST':
        temp_user = None
        if form.validate(): 
            email = form.get_Info()['email']
            temp_user = user.get_by_name_or_email(email=email)
        if temp_user is not None:
            if temp_user.is_confirmed:
                # msg = Message(
                #   'Recover MemFlash Password',
                #    sender='memflash.dev@gmail.com',
                #    recipients=
                #    [temp_user.email])
                serial_datetime = url_time_serializer.dumps(temp_user.username, salt='recover-password')
                recoveryLink = request.environ['HTTP_ORIGIN']+"/password_reset/"+serial_datetime
                temp_message = render_template('recover_password_email.html', username = temp_user.username, recoveryLink = recoveryLink)
                # mail.send(msg)
                send_mail_from_app(subject = 'Password Recovery', message = temp_message, destination = temp_user.email)
                flash('A password recovery email will be sent to your email.')

            else:
                flash('Your account has not been verified yet.')
        else:
            flash('Invalid email. Please try again.')
            return redirect('recover_password')

        return redirect('/')
    else:
        submit_url = request.url.replace(request.url.split('/recover_password')[0],'',1)

    return render_template('recover_password.html',form = Markup(form.get_html()), submit_url = submit_url)

@app.route("/password_reset/<confirmation_hash>",methods=["GET","POST"])
def password_reset(confirmation_hash=None): 

    link_data = url_time_serializer.loads(confirmation_hash, salt='recover-password')
    temp_user = user.get_by_name(link_data)
    form = updatePasswordForm(request=request)
    submit_url = request.url.replace(request.url.split('/password_reset/'+str(confirmation_hash))[0],'',1)
    # next = ('/profile' if not request.args.get('next') else request.args.get('next'))
    if request.method == 'POST':
        if form.validate(): 
            password = form.get_Info()['password']
        if temp_user is not None:
            if temp_user.is_confirmed:
                temp_user.set_password(password)
                db.session.commit()
                flash('Your Password has been updated.')
                if not current_user.is_authenticated:
                    return redirect('/login')
                else:
                    return redirect('/profile')
            else:
                flash('Your account has not been verified yet.')
                return redirect('/')
        else:
            flash('Invalid hash. Please try again.')
            return redirect('/')

    return render_template('recover_password.html',form = Markup(form.get_html()), submit_url = submit_url)





@app.route("/flashdeck_profile/<flashdeck_id>", methods=["GET", "POST"])
@login_required
def flashdeck_profile(flashdeck_id = None):
    deck = flashdeck.get_by_id(flashdeck_id)
    smarttesterform = smartTesterForm(flashdeck = deck)
    form = cubeBuildForm(deck_info=deck.getSideInfo(),request=request)
    if deck is None:
        flash('That is not a valid deck ID!')
        return redirect('/profile/'+str(current_user.username)+'/deckbook')
    updateform = deckUpdateForm(deck=deck)
    if request.method == "POST":
        if form.validate():
            cube = None
            cube = deck.add_cube(cube_info=form.get_Info(), db=db)
            new_event = event.newCardEvent(user=current_user, flashdeck=deck, flashcube = cube )
            current_user.events.append(new_event)
            db.session.add(new_event)
            db.session.commit()
            return redirect('/flashdeck_profile/'+str(flashdeck_id))

    username = current_user.username
    deckusers = list()
    for user in deck.user:
        deckusers.append(user.username)

    tempuser = deck.user[0]
    random_test_url=url_for('random_card_tester', flashdeck_id = deck.id)
    form_data = Markup(form.get_html())    
    update_form_data = Markup(updateform.get_html())
    
    cubes = deck.flashcubes
    tempsmartdeckprofile = current_user.get_smartdeckprofile(flashdeck = deck)
    knowledge_dict = tempsmartdeckprofile.get_id_knowledge_dict()
    print knowledge_dict

    return render_template('flashdeck.html',flashcube_count = len(deck.flashcubes), knowledge_dict=knowledge_dict, user=tempuser, random_test_url=random_test_url , flashdeck = deck,  flashCubeForm= form_data,  deckUpdateForm=update_form_data, smartTesterForm=Markup(smarttesterform.get_html()))

@app.route("/flashdeck_update/<flashdeck_id>", methods=["GET", "POST"])
@login_required
def flashdeck_update(flashdeck_id = None):
    deck = flashdeck.get_by_id(flashdeck_id)
    form = deckUpdateForm(request=request)
    if request.method == "POST":
        if form.validate():
            data = form.get_Info()
            deck.name = data['deck_name']
            deck.self_description = data['self_description']
            if data['profile_photo'] is not None:
                deck.profile = data['profile_photo']
            db.session.commit()
            new_event = event.updateDeckEvent(user=current_user, flashdeck=deck)
            current_user.events.append(new_event)
            db.session.add(new_event)
            db.session.commit()
            # deck.add_cube(cube_info=form.get_Info(), db=db)
    
    return redirect('/flashdeck_profile/'+str(flashdeck_id))

    
@app.route("/faq", methods=["GET", "POST"])
@login_required
def faq():
    return render_template('faq.html', user=current_user)

    

            
# need to remove from favorite decks of others
@app.route("/delete_flashdeck/<deck_id>")
@login_required
def delete_flashdeck(deck_id = None):
    deck = flashdeck.get_by_id(deck_id)
    if deck is None:
        flash('That is not a valid deck!')
    elif current_user.username != deck.user[0].username:
        flash('You are not the owner of that deck!')
    else:
        deck.delete_cubes(db)
        flashdeck_name = deck.name
        db.session.delete(deck)
        db.session.commit()
        new_event = event.deleteDeckEvent(user=current_user, flashdeck_name = flashdeck_name)
        current_user.events.append(new_event)
        db.session.add(new_event)
        db.session.commit()
    return redirect('/profile/'+current_user.username+'/deckbook')


@app.route("/flashcube_profile/<flashcube_id>", methods=["GET", "POST"])
@login_required
def flashcube_profile(flashcube_id = None):
    cube = flashcube.get_by_id(flashcube_id)
    deck = cube.flashdeck[0]
    tempuser = deck.user[0] 
    return render_template('flashcube.html', user=tempuser , flashdeck = deck, flashcube = cube)

@app.route("/delete_flashcube/<flashcube_id>")
@login_required
def delete_flashcube(flashcube_id = None):
    cube = flashcube.get_by_id(flashcube_id)
    redirect_url = '/profile/'+current_user.username+'/deckbook'
    if cube is None:
        flash('That is not a valid cube!')
    elif current_user.username != cube.flashdeck[0].user[0].username:
        flash('You are not the owner of that deck!')
    else:
        redirect_url = '/flashdeck_profile/'+ str(cube.flashdeck[0].id)
        flashdeck = cube.flashdeck[0]
        db.session.delete(cube)
        new_event = event.deleteCardEvent(user=current_user, flashdeck=flashdeck)
        current_user.events.append(new_event)
        db.session.add(new_event)
        db.session.commit()
    return redirect(redirect_url)
 


@app.route("/random_card_tester", methods=["GET", "POST"])
@login_required
def random_card_tester():
    if 'flashdeck_id' in request.values and flashdeck.get_by_id(request.values['flashdeck_id']):
        flashdeck_id = request.values['flashdeck_id']
    else:
        flash('Need To specify a valid deck to be test on!')
        return redirect('/profile/'+current_user.username+'/deckbook')
    
    deck = flashdeck.get_by_id(flashdeck_id) 
    if len(deck.flashcubes) <2:
        flash('Need To specify a valid deck to be test on!')
        return redirect('/profile/'+current_user.username+'/deckbook')

    if 'selected_side' in request.values:
        selected_side = request.values['selected_side']
    else:
        selected_side = deck.getSideInfo()[0]['side_name']

    if 'flashcube_id' in request.values:
        flashcube_id = request.values['flashcube_id']
    else:
        flashcube_id=str(random.choice(deck.flashcubes).id)
        return redirect(url_for('random_card_tester',  selected_side=selected_side, flashdeck_id = flashdeck_id, flashcube_id=flashcube_id))
    
    new_cube_id=str(random.choice(deck.flashcubes).id)

    while (new_cube_id == flashcube_id):


        new_cube_id=str(random.choice(deck.flashcubes).id)
    cube = flashcube.get_by_id(new_cube_id)

    tempuser = deck.user[0]

    

    return render_template('random_card_tester.html', user = tempuser, selected_side= selected_side, flashcube=cube,  flashdeck = deck)
    
@app.route("/smart_card_tester/<flashdeck_id>", methods=["GET", "POST"])
@login_required
def smart_card_tester(flashdeck_id = None):

    # getting question_side from input
    if 'answer_type' in request.values:
        answer_type = (request.values['answer_type'])
    else:
        flash('Need To specify a valid answer type to be tested on!')
        return redirect('/profile/'+current_user.username+'/deckbook')

    # getting flashdeck_id from input
    if flashdeck_id is not None and flashdeck.get_by_id(flashdeck_id):
        deck = flashdeck.get_by_id(flashdeck_id)
    else:
        flash('Need To specify a valid deck to be test on!')
        return redirect('/profile/'+current_user.username+'/deckbook')
    
    if len(deck.flashcubes) <5:
        flash('Need To specify a valid deck to be test on!')
        return redirect('/profile/'+current_user.username+'/deckbook')

    tempsmartdeckprofile = current_user.get_smartdeckprofile(flashdeck = deck)

    # getting question_side from input
    if 'question_side' in request.values:
        question_side = int(request.values['question_side'])
    else:
        flash('Need To specify a valid question side to be tested on!')
        return redirect('/profile/'+current_user.username+'/deckbook')

    if question_side <0 or question_side >= len(deck.getSideInfo()):
        flash('Need To specify a valid question side to be tested on!')
        return redirect('/profile/'+current_user.username+'/deckbook')

    # getting answer_side from input
    if 'answer_side' in request.values:
        answer_side = int(request.values['answer_side'])
    else:
        flash('Need To specify a valid answer side to be tested on!')
        return redirect('/profile/'+current_user.username+'/deckbook')

    if answer_side <0 or answer_side >= len(deck.getSideInfo()):
        flash('Need To specify a valid question side to be tested on!')
        return redirect('/profile/'+current_user.username+'/deckbook')


    # getting flashcube_id from input
    if 'flashcube_id' in request.values:
        flashcube_id = request.values['flashcube_id']
    else:
        # replace this with smart tester "random cube" stuff
        flashcube_id=str(tempsmartdeckprofile.get_random_card().id)
        return redirect(url_for('smart_card_tester', answer_side=answer_side, question_side=question_side, flashdeck_id = flashdeck_id, flashcube_id=flashcube_id, answer_type=answer_type))

    smart_card_profile = tempsmartdeckprofile.get_smartcard_from_cube(flashcube_id = flashcube_id)

    if smart_card_profile is None:
        flash('Need To specify a valid flashcube!')
        return redirect('/profile/'+current_user.username+'/deckbook')
    if len(smart_card_profile.fake_cubes) < 1:
        print('updating')
        smart_card_profile.update_fake_cubes()
        db.session.commit()


    if 'known' in request.values:
        known = request.values['known']
        # replace this with smart tester "random cube" stuff
        if known == 'True':
            smart_card_profile.known()
        else: 
            smart_card_profile.unknown()
        smart_card_profile.update_fake_cubes()
        db.session.commit()



        flashcube_id=str(tempsmartdeckprofile.get_random_card(last_card_index = int(flashcube_id)).id)
        return redirect(url_for('smart_card_tester', answer_side=answer_side, question_side=question_side, flashdeck_id = flashdeck_id, flashcube_id=flashcube_id, answer_type=answer_type))
        
    # new_cube_id=str(random.choice(deck.flashcubes).id)

    # while (new_cube_id == flashcube_id):
        # flashcube_id=str(random.choice(deck.flashcubes).id)
    # cube = flashcube.get_by_id(new_cube_id)
    # smartcard = smartcardprofile.get_by_cube_id(cube.id)
    # print(smartcard)
   
    tempuser = deck.user[0]
    smarttesterform = smartTesterForm(flashdeck = deck)
    flash_cube = flashcube.get_by_id(id_number=flashcube_id)
    url = url_for('smart_card_tester', answer_side=answer_side, question_side=question_side, flashdeck_id = flashdeck_id, flashcube_id=flashcube_id)
    
    # print(temp_profile)
    fake_cubes = smart_card_profile.fake_cubes

    cube = flashcube.get_by_id(flashcube_id)
    print( fake_cubes[0])

    return render_template('smart_card_tester.html', user = tempuser, side =flash_cube.sides[deck.getSideInfo()[question_side]['side_name']], flashdeck = deck, smartTesterForm = Markup(smarttesterform.get_html()), url=url, answer_type=answer_type, fake_cubes=fake_cubes, cube = cube,answer_side_name = deck.getSideInfo()[answer_side]['side_name'])

@app.route("/reset_memory/<flashdeck_id>", methods=["GET", "POST"])
@login_required
def reset_memory(flashdeck_id = None):
    deck = flashdeck.get_by_id(flashdeck_id)
    if deck is None:
        flash('That is not a valid deck ID!')
        return redirect('/profile/'+str(current_user.username)+'/deckbook')
    tempsmartdeckprofile = current_user.get_smartdeckprofile(flashdeck = deck)
    tempsmartdeckprofile.reset_memory()
    db.session.commit()
    return redirect('/flashdeck_profile/'+str(flashdeck_id))


@app.route("/signup", methods=['POST','GET'])
def signup():
    if current_user.is_authenticated:
        flash('You cannot signup when you are currently logged in.')
        return redirect('/profile')
    form = signupForm(request)
    info = form.get_Info()
    if request.method == 'POST' and form.validate():
        
        signupName = info['username']
        signupPassword = info['password']
        signupEmail = info['email']
        
        userquery = user.get_by_name_or_email(signupName,signupEmail)
        if (userquery is not None):
            flash('A user with that name or email already exists. Please choose another.')
            return redirect('/signup')


        else:
            newUser = user(signupName, signupEmail, signupPassword)
            db.session.add(newUser)
            db.session.commit()
            flash('Your account has been created. We have sent a verification email to you. To use your account, you must click the link in that email.')
            # msg = Message(
            #   'Welcome To MemFlash',
            #    sender='memflash.dev@gmail.com',
            #    recipients=
            #    [signupEmail])
            serial_datetime = url_time_serializer.dumps(newUser.username, salt='account-activate')
            confirmationLink = request.environ['HTTP_ORIGIN']+"/confirm/ACTIVATE/"+serial_datetime
            temp_message = render_template('confirmation_email.html', signupName = newUser.username, confirmationLink = confirmationLink)
            # mail.send(msg)
            send_mail_from_app(subject = 'Email Confirmation', message = temp_message, destination = newUser.email)
            return redirect('/')


    return render_template('signup.html', current_user = current_user, form = Markup(form.get_html()) )
        
@app.route("/confirm/<action>", methods = ['GET', 'POST'])
@app.route("/confirm/<action>/<confirmation_hash>", methods = ['GET', 'POST'])
def confirm(action=None, confirmation_hash = None):
    form = emailVerificationForm(request)
    confirmation = "INVALID_HASH"
    if action == "ACTIVATE" and confirmation_hash is not None:
        link_data = url_time_serializer.loads(confirmation_hash, salt='account-activate')
        tempUser = user.get_by_name(link_data)
        print(tempUser)
        if tempUser is None:
            confirmation = "INVALID_HASH"
        elif tempUser.is_confirmed:
            confirmation = "ALREADY_VERIFIED"
        elif (tempUser.registered_on - datetime.datetime.now()).total_seconds() < 86400:
            tempUser.confirmed_on = datetime.datetime.now()
            tempUser.is_confirmed = True
            db.session.commit()
            confirmation = "CONFIRMED"
        else:
            confirmation = "TIMEOUT"
    elif action == "ACTIVATE":
        confirmation = "INVALID_HASH"
    elif action == "RESEND":       
        if request.method == "POST" and form.validate():
            tempUser = user.get_by_name_and_email(request.get_Info()['username'], request.get_Info()['email'])
            if (tempUser is None):
                print('failure')
                flash('You have either entered an invalid username or email. Please Try again.')
                return redirect('/confirm/RESEND')
            else:
                tempUser.registered_on = datetime.datetime.now()
                db.session.commit()
                # msg = Message(
                #   'Hello',
                #    sender='memflash.dev@gmail.com',
                #    recipients=
                #    [tempUser.email])
                serial_datetime = url_time_serializer.dumps(tempUser.username, salt='account-activate')
                print(url_time_serializer.loads(serial_datetime, salt='account-activate'))
                confirmationLink = request.environ['HTTP_ORIGIN']+"/confirm/ACTIVATE/"+serial_datetime
                temp_message = render_template('confirmation_email.html', signupName = tempUser.username, confirmationLink = confirmationLink)
                # mail.send(msg)
                send_mail_from_app(subject = 'Email Confirmation', message = temp_message, destination = temp_user.email)
                flash('New confirmation email has been sent')
            # login_user(newUser)
            return redirect('/')
        else:
            confirmation = "RESEND"
    else:
        return redirect ('/')
    return render_template('confirm.html', confirmation = confirmation, form = form)

if __name__ == "__main__":
    app.run(debug=True)
  

