from datetime import datetime
# -*- coding: utf-8 -*-

DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

# Just a random partial list of restaurant culinary styles that can be used for the culinaryStyle list.
STYLES = ['American', 'Chinese', 'Japanse', 'Korean', 'Vietnamese', 'Mongolian', 'Mexican', 'Cuban', 'Indian', 'British', 'French', 'Italian', 'German']

STATES = ['Alabama', 'Alaska','Arizona', 'Arkansas', 'California','Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine','Maryland','Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota','Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington','West Virginia', 'Wisconsin', 'Wyoming']

#addresses holds all the addresses of restruants and users
#we cannnot link db.auth table to addresses table, therefore addresses must link to db.auth
db.define_table('addresses',
    Field('streetAddress'),
    Field('city'),
    Field('zipCode'),
    Field('usState'),
    Field('userID', db.auth_user),
    )
db.addresses.usState.requires = IS_IN_SET(STATES)

db.define_table('restaurants',
    Field('ownerID',db.auth_user),                 # Each restaurant has an owner, the ID of a particular user account.
    Field('restaurantName', required=True),
    Field('email', required=False),
    Field('phone', required=True),
    Field('addressID', db.addresses),
    Field('culinaryStyle'),
    Field('description', 'text'),
    Field('priceRange'),              # We should pull this from outside source--not from user

    )
db.restaurants.ownerID.readable = db.restaurants.ownerID.writable = False
db.restaurants.addressID.readable = db.restaurants.addressID.writable = False
db.restaurants.culinaryStyle.requires = IS_IN_SET(STYLES)
db.restaurants.phone.requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.restaurants.email.requires = IS_EMAIL()

#some resturants may have odd hours on different days 
"""Su: Closed
M-Th: 10am-2pm 5pm -9pm
F-Sa: 10 am - 3 pm 5pm- 11 pm""" #ect. -E
db.define_table('hours',
    Field('restaurantID', db.restaurants),
    Field('dayOfWeek'),
    Field('openAt', 'datetime'),
    Field('closedAt','datetime'),
)
db.hours.dayOfWeek.requires = IS_IN_SET(DAYS)
db.hours.openAt.default = datetime.utcnow()
db.hours.closedAt.default = datetime.utcnow()

#add phone field to auth table 
db.define_table('users',
    Field('phone', required = True),
    Field('addressId'), #db.addresses.id),
)

# Each menuItem describes a single menu item. It includes the ID of the restaurant that owns it. A restaurant menu is formed by querying the menuItem table for all items
# matching the appropriate ID. This cuts down on the number of sub-tables required.
db.define_table('menuItems',
    Field('restaurantID', db.restaurants),
    Field('dishName', requires = IS_NOT_EMPTY()),
    Field('description', 'text', requires = IS_NOT_EMPTY()),
    Field('price', requires = IS_FLOAT_IN_RANGE(0, 1000)),
    Field('image', 'upload'),
    )
db.menuItems.restaurantID.readable = db.menuItems.restaurantID.writable = False

# Each element of menuTags is a short, textual tag belonging to a single menuItem. To build a list of tags, query menuTags for a given menuItem tag.
# Dishes are limited to 5 tags. This wont be too hard, for each menuItem we just need to check how many Tags get returned for a given menuID query.
# If 5 are found, we prevent the restaurant owner from adding more. If more than 5 are found, we can just trim off tags arbitrarily.
db.define_table('menuTags',
    Field('menuID', db.menuItems),
    Field('tag', requires = IS_NOT_EMPTY()),
    )
db.menuTags.menuID.readable = db.menuTags.menuID.writable = False

# Taggable returns true if and only if the menuItem associated with the passed-in ID has less than 5 associated tags.
def taggable(menuItemID):
    taggable = False

    if len(db(db.menuTags.menuID == menuItemID).select()) < 5:
        taggable = True

    return taggable
