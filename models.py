#import 
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#models
class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))    
    seeking_venue = db.Column(db.Boolean(),nullable=False,default=False)    
    seeking_description = db.Column(db.Text)
    past_shows = db.Column(db.Integer,nullable=True)
    upcoming_shows = db.Column(db.Integer,nullable=True)
    shows = db.relationship('Show', backref="Venue", cascade="all,delete-orphan", lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))    
    seeking_venue = db.Column(db.Boolean(),nullable=False,default=False)    
    seeking_description = db.Column(db.Text)
    past_shows = db.Column(db.Integer,nullable=True)
    upcoming_shows = db.Column(db.Integer,nullable=True)
    shows = db.relationship('Show', backref="Artist", cascade="all,delete-orphan", lazy=True)


class Show(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  artist_id= db.Column(db.Integer(),db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer(),db.ForeignKey('Venue.id'))
  start_time = db.Column(db.DateTime(),nullable=False)
  artists=db.relationship('Artist')
  venues = db.relationship('Venue', backref="Show")



