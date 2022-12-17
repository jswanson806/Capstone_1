from app import db

from models import User

db.drop_all()
db.create_all()

User.query.delete()

# Add users

su1 = User.signup(first_name='Beckham', 
            last_name='Swanson', 
            email='Beckham@email.com',
            username='su1', 
            password='password'
            )
su2 = User.signup(first_name='Margot', 
            last_name='Swanson', 
            email='Margot@email.com',
            username='su2',
            password='password'
            )
su3 = User.signup(first_name='Lily', 
            last_name='Swanson', 
            email='Lily@email.com',
            username='su3',
            password='password'
            )

db.session.add_all([su1, su2, su3])
db.session.commit()