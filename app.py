#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# SQL Alchemy Logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(500))
    
class Artist(db.Model):
    __tablename__ = 'artist'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(500))

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),
                        nullable=False)

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'),
                        nullable=False)

    show_artist = db.relationship("Artist")
    show_venue = db.relationship("Venue")

    starttime = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  list_of_cities = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []
  upcoming_shows = []
  
  for city in list_of_cities:
    venues=Venue.query.filter((Venue.city==city.city) & (Venue.state==city.state))
    for venue in venues:
      shows=Show.query.filter_by(venue_id=venue.id)
      for show in shows:
        if show.starttime > datetime.now():
          upcoming_shows.append(show)
    entry = {
      'city': city.city,
      'state' : city.state,
      'venues' : venues,
      'num_upcoming_shows' : len(upcoming_shows)
    }
    data.append(entry)       

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  searchterm = '%' + request.form.get('search_term', '') + '%'

  list_of_venues = Venue.query.filter(Venue.name.ilike(searchterm)).all()
  venues = []
  upcoming_shows = []

  for venue in list_of_venues:
    shows=Show.query.filter_by(venue_id=venue.id)
    for show in shows:
      if show.starttime > datetime.now():
        upcoming_shows.append(show)
    venues.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(upcoming_shows)
    })
  response = {
      'count': len(list_of_venues),
      'data' : venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)

  past_shows = []
  upcoming_shows = []

  list_of_shows = Show.query.filter(Show.venue_id==venue.id).all()

  for show in list_of_shows:
    artist = Artist.query.get(show.artist_id)
    entry = {
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.starttime.strftime("%m/%d/%Y, %H:%M:%S")
    }
    if show.starttime > datetime.now():
      upcoming_shows.append(entry)
    else:
      past_shows.append(entry)

  data={
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    data = request.form
    venue = Venue(name=data.get('name'),
                  city=data.get('city'),
                  state=data.get('state'),
                  address=data.get('address'),
                  phone=data.get('phone'),
                  genres=data.getlist('genres'),
                  image_link=data.get('image_link'),
                  facebook_link=data.get('facebook_link'))
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + data.get('name') + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.get('name') + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    # on successful delete, flash success
    flash('Venue ' + venue_id + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  searchterm = '%' + request.form.get('search_term', '') + '%'

  list_of_artists = Artist.query.filter(Artist.name.ilike(searchterm)).all()
  artists = []
  upcoming_shows = []

  for artist in list_of_artists:
    shows=Show.query.filter_by(artist_id=artist.id)
    for show in shows:
      if show.starttime > datetime.now():
        upcoming_shows.append(show)
    artists.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(upcoming_shows)
    })
  response = {
      'count': len(list_of_artists),
      'data' : artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real venue data from the venues table, using venue_id
  
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []

  list_of_shows = Show.query.filter(Show.artist_id==artist.id).all()

  for show in list_of_shows:
    venue = Venue.query.get(show.venue_id)
    entry = {
      'venue_id': venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.starttime.strftime("%m/%d/%Y, %H:%M:%S")
    }
    if show.starttime > datetime.now():
      upcoming_shows.append(entry)
    else:
      past_shows.append(entry)

  data={
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  data = Artist.query.get(artist_id)

  form.genres.default = data.genres
  form.process()

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    data = request.form

    artist = Artist.query.get(artist_id)

    artist.name=data.get('name')
    artist.city=data.get('city')
    artist.state=data.get('state')
    artist.phone=data.get('phone')
    artist.genres=data.getlist('genres')
    if data.get('seeking_venue') != None:
      artist.seeking_venue=True 
    else:
      artist.seeking_venue= False
    artist.seeking_description=data.get('seeking_description')
    artist.website=data.get('website')
    artist.image_link=data.get('image_link')
    artist.facebook_link=data.get('facebook_link')
    
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + data.get('name') + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.get('name') + ' could not be updated.')
  finally:
    db.session.close()

  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  data = Venue.query.get(venue_id)

  form.genres.default = data.genres
  form.process()

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    data = request.form

    venue = Venue.query.get(venue_id)

    venue.name=data.get('name')
    venue.city=data.get('city')
    venue.state=data.get('state')
    venue.phone=data.get('phone')
    venue.genres=data.getlist('genres')
    if data.get('seeking_talent') != None:
      venue.seeking_talent=True 
    else:
      venue.seeking_talent= False
    venue.seeking_description=data.get('seeking_description')    
    venue.website=data.get('website')
    venue.image_link=data.get('image_link')
    venue.facebook_link=data.get('facebook_link')
    
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + data.get('name') + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.get('name') + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:

    data = request.form

    artist = Artist(name=data.get('name'),
                    city=data.get('city'),
                    state=data.get('state'),
                    phone=data.get('phone'),
                    genres=data.getlist('genres'),
                    image_link=data.get('image_link'),
                    facebook_link=data.get('facebook_link'))
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + data.get('name') + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.get('name') + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
    
  data=[]

  list_of_shows = Show.query.all()

  for show in list_of_shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    entry = {
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.starttime.strftime("%m/%d/%Y, %H:%M:%S")
    }
    data.append(entry)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    data = request.form
    show = Show(artist_id=data.get('artist_id'),
                venue_id=data.get('venue_id'),
                starttime=data.get('start_time'))
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show for Artist ID ' + data.get('artist_id') + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show for Artist ID ' + data.get('artist_id') + ' could not be listed.')
  finally:
    db.session.close()
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
