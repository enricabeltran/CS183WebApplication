# -*- coding: utf-8 -*-
db.define_table('addresses',
    Field('streetAddress'),
    Field('city'),
    Field('zipCode'),
    Field('state'),
    )

#update with appropriate fields
db.define_table('hours',
    Field('enter something here')
)

db.define_table('restaurants',
    Field('accountID', unique=True),
    Field('name', required=True),
    Field('email'),
    Field('phone', required=True),
    Field('addressId', db.addresses.id),
    Field('hoursId', db.hours.id),
    Field('culinaryStyle'),           # Should we limit options? Make a set of available culinary Style-reference culinary Styles in seamless app
    Field('description', 'text'),
    Field('priceRange', writable=False),   # We should pull this from outside source--not from user
    # I DONT THINNK WE NEED NEXT TWO, menu table references restaurantID and each dish has its own image in the menu table
    #Field('menu'),
    #Field('images')
    )

db.define_table('users',
    Field('accountID', unique=True),
    Field('name', required = True),
    Field('email', required = True),
    Field('phone', required = True),
    Field('paymentInformation'),      # Should be reference to external table
    Field('addressId', db.addresses.id), 
    )


#update with appropriate fields
db.define_table('hours',
    Field('enter something here')
)

#holds all the different dishes of all restaurants 
db.define_table('menu',
    Field('restaurantID', db.restaurants.id),
    Field('dishName'),
    Field('description'),
    Field('image', 'upload'),
    Field('tagCount'), #dishes are limited to 5 tags....we dont really need to implement this though? maybe if there is extra time?? to be honest, friends, i'm kind of getting lost in everything, THERE ARE SO MANY LITTLE DETAILS, LOOK AT ALL THESE TABLES!!
    )

#holds all tags for all dishes 
db.define_table('menuTags',
    Field('menuID', db.menu.id),
    Field('tag'),
    )

STATES = ['Alabama', 'Alaska','Arizona', 'Arkansas', 'California','Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine','Maryland','Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota','Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington','West Virginia', 'Wisconsin', 'Wyoming']

db.addresses.requires = IS_IN_SET(STATES)

db.users.phone.requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.users.email.requires = IS_EMAIL()

db.restaurant.phone.requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.restaurants.email.requires = IS_EMAIL()
