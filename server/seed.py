# seed.py

from app import app, db
from models import User, Profile, Movie, Review, Favorite, Watchlist
from werkzeug.security import generate_password_hash
from faker import Faker

fake = Faker()

# Create an application context
with app.app_context():
    # Clear existing data
    db.session.query(User).delete()
    db.session.query(Profile).delete()
    db.session.query(Movie).delete()
    db.session.query(Review).delete()
    db.session.query(Favorite).delete()
    db.session.query(Watchlist).delete()

    # Create some users with profiles
    for _ in range(10):
        username = fake.unique.user_name()
        password = generate_password_hash(fake.password())
        
        user = User(username=username, password=password)
        db.session.add(user)

        profile = Profile(photo_url=fake.image_url())
        user.profile = profile  # Establish the relationship
        db.session.add(profile)

    db.session.commit()

    # Create some movies
    movies = [Movie(title=fake.sentence(nb_words=3)) for _ in range(10)]
    db.session.add_all(movies)
    db.session.commit()

    # Now that users and movies have been committed, their id attributes are set
    # Create some reviews
    for user in User.query.all():
        for movie in Movie.query.all():
            review = Review(user_id=user.id, movie_id=movie.id, rating=fake.random_int(min=1, max=5), text=fake.text(max_nb_chars=200))
            db.session.add(review)

    # Create some favorites
    for user in User.query.all():
        for movie in Movie.query.all():
            favorite = Favorite(user_id=user.id, movie_id=movie.id)
            db.session.add(favorite)

    # Create some watchlist items
    for user in User.query.all():
        for movie in Movie.query.all():
            watchlist = Watchlist(user_id=user.id, movie_id=movie.id)
            db.session.add(watchlist)

    # Commit the changes
    db.session.commit()
