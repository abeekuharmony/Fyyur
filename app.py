#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]
  selected= Venue.query.with_entities(Venue.state,Venue.city,Venue.id).distinct()
  for select in selected:
    city_state = {
        "city" : select.city,
        "state": select.state,
        "venues":[]
    }
    venues = db.session.query(Venue).filter(Venue.state == select.state).filter(Venue.city == select.city).all()
    for venue in venues:
      city_state["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))

        })
    data.append(city_state)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term','')
  venues = db.session.query(Venue).filter( Venue.name.ilike(f"%{search_term}%") |
   Venue.city.ilike(f"%{search_term}%") | Venue.state.ilike(f"%{search_term}%")).all() 
  response = { "count": len(venues), "data": [] } 

  for venue in venues: 
    shows=db.session.query(Show).filter_by(venue_id=venue.id).all()
    temp = {} 
    temp["id"] = venue.id
    temp["name"] = venue.name 
    num_upcoming_shows = 0  

    for show in shows:
      if show.start_time > datetime.now(): 
        num_upcoming_shows =num_upcoming_shows+ 1
      temp["num_upcoming_shows"] = num_upcoming_shows

    response["data"].append(temp)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  setattr(venue, "genres", venue.genres.split(","))
  #get past shows
  past_shows= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  
  past = [] 
  for show in past_shows:
    past.append({
          "artist_id": show.artist_id,
          "artist_name": show.artists.name,
          "artist_image_link":show.artists.image_link,
          "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S") 
      })   
    setattr(venue, "past_shows", past) 
    setattr(venue,"past_shows_count", len(past)) 

    #upcoming_shows
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all() 
    show = [] 
    for show in upcoming_shows: 
      show.append({
          "artist_id": show.artist_id,
          "artist_name": show.artists.name,
          "artist_image_link":show.artists.image_link,
          "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S") 
      }) 
  
    setattr(venue, "upcoming_shows", show)  
    setattr(venue,"upcoming_shows_count", len(show)) 
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate:
    try:
      name=form.name.data
      city=form.city.data
      state=form.state.data
      address=form.address.data
      phone=form.phone.data
      image_link=form.image_link.data
      facebook_link=form.facebook_link.data
      website_link=form.website_link.data
      seeking_description=form.seeking_description.data
      venue = Venue(name=name,city=city, state=state,address=address,phone=phone,genres=", ".join(request.form.get('genres')), image_link=image_link, facebook_link=facebook_link, 
        website_link=website_link,seeking_venue=request.form.get('seeking_venue'),seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit();
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback() 
      flash('An error occurred. Venue ' + request.form['name'] + ' was not listed.')    
    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue ')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  try:
    venue=Venue.query.filter_by(id=venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue Deleted Successfully')
  except:  
    flash('An error occurred')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists= db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term','')
  artists = db.session.query(Artist).filter( Artist.city.ilike(f"%{search_term}%") |
   Artist.name.ilike(f"%{search_term}%") | Artist.state.ilike(f"%{search_term}%")).all() 
  response = { 
      "count": len(artists), 
      "data": [] 
      } 

  for artist in artists: 
    shows=db.session.query(Show).filter_by(artist_id=artist.id).all()
    temp = {} 
    temp["id"] = artist.id
    temp["name"] = artist.name 
    upcoming_shows = 0  

    for show in artist.shows:
      if show.start_time > datetime.now(): 
        upcoming_shows =upcoming_shows+ 1
      temp["upcoming_shows"] = upcoming_shows

    response["data"].append(temp)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  setattr(artist, "genres", artist.genres.split(","))
  
  past_shows= db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  
  shows = []
  for show in past_shows:
    shows.append({
          "venue_id":show_venue_id,
          "venue_name":show.venues.name,
          "venue_image_link":show.venues.image_link,
          "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

      })
  setattr(artist, "past_shows", shows)
  setattr(artist, "past_shows_count", len(shows))

  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()

  upcoming = []
  for show in upcoming_shows:
    upcoming.append({
          "venue_id":show_venue_id,
          "venue_name":show.venues.name,
          "venue_image_link":show.venues.image_link,
          "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
  setattr(artist, "upcoming_shows", upcoming)
  setattr(artist, "upcoming_shows_count", len(upcoming))
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  form.genres.data = artist.genres.split(",")
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate:
    try:
      artist = Artist.query.filter_by(id=artist_id).first()
      
      artist.name = form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.image_link=form.image_link.data
      artist.facebook_link=form.facebook_link.data
      artist.website_link=form.website_link.data
      if request.form.get('seeking_venue'):
        seeking_venue=1
      else:
        seeking_venue = 0
      artist.seeking_venue=seeking_venue
      artist.seeking_description=form.seeking_description.data
      artist.genres=", ".join(request.form.get('genres'))
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      flash('An insertion error occurred. Artist ' + request.form['name'] + ' was not listed.')
    finally:
      db.session.close()
  else:
    flash('An error occurred.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if form.validate:
    try:
      venue = Venue.query.filter_by(id=venue_id).first()
      venue.name = form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.phone=form.phone.data
      venue.address=form.address.data
      venue.image_link=form.image_link.data
      venue.facebook_link=form.facebook_link.data
      venue.website_link=form.website_link.data
      venue.genres=", ".join(request.form.get('genres'))
      if request.form.get('seeking_venue'):
        seeking_venue=1
      else:
        seeking_venue = 0
      venue.seeking_venue=seeking_venue
      venue.seeking_description=form.seeking_description.data
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      flash('An insertion error occurred.')
    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue ')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate:
    try:
      artist = Artist(name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        genres=", ".join(form.genres.data))
      db.session.add(artist)
      db.session.commit();
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash('An error occurred.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
          'venue_id':show.venues.id,
          'venue_name':show.venues.name,
          'artist_id':show.artists.id,
          'artist_name':show.artists.name,
          'artist_image_link':show.artists.image_link,
          'start_time':show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist = Artist.query.filter(Artist.id==request.form.get('artist_id')).count()
  venue = Artist.query.filter(Venue.id==request.form.get('venue_id')).count()
  
  form = ShowForm(request.form)
  if form.validate:
    try:
        new_shows = Show(artist_id=request.form.get('artist_id'),venue_id=request.form.get('venue_id'),start_time=request.form.get('start_time'))
        db.session.add(new_shows)
        db.session.commit();
        flash('Show was successfully listed!')
      
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
  else:
    flash('An error occurred.')
    
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
