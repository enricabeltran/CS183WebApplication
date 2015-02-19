#linking tables the commented out way gives the error: <type 'exceptions.SyntaxError'> keyed tables can only reference other keyed tables (for now)
# -*- coding: utf-8 -*-
db.define_table('addresses',
    Field('streetAddress'),
    Field('city'),
    Field('zipCode'),
    Field('usState'),
    )

#update with appropriate fields
# What is this supposed to be? - Sam
db.define_table('hours',
    Field('enter something here')
)

# Just a random partial list of restaurant culinary styles that can be used for the culinaryStyle list.
STYLES = ['American', 'Chinese', 'Japanse', 'Korean', 'Vietnamese', 'Mongolian', 'Mexican', 'Cuban', 'Indian', 'British', 'French', 'Italian', 'German']

db.define_table('restaurants',
    Field('ownerID'),                 # Each restaurant has an owner, the ID of a particular user account.
    Field('name', required=True),
    Field('email'),
    Field('phone', required=True),
    Field('addressId'), #db.addresses.id),
    Field('hoursId'), #db.hours.id),
    Field('culinaryStyle'),           # Should we limit options? Make a set of available culinary Style-reference culinary Styles in seamless app
    Field('description', 'text'),
    Field('priceRange'),              # We should pull this from outside source--not from user
    # I DONT THINNK WE NEED NEXT TWO, menu table references restaurantID and each dish has its own image in the menu table
    #Field('menu'),
    #Field('images')
    )
db.restaurants.ownerID.readable = db.restaurants.ownerID.writable = False
db.restaurants.addressId.readable = db.restaurants.addressId.writable = False
db.restaurants.hoursId.readable = db.restaurants.hoursId.writable = False

# I suspect we don't actually need a separate users table, my bad. - Sam
db.define_table('users',
    Field('accountID', unique=True),
    Field('name', required = True),
    Field('email', required = True),
    Field('phone', required = True),
    Field('paymentInformation'),      # Should be reference to external table
    Field('addressId'), #db.addresses.id),
    )


# Each menuItem describes a single menu item. It includes the ID of the restaurant that owns it. A restaurant menu is formed by querying the menuItem table for all items
# matching the appropriate ID. This cuts down on the number of sub-tables required.
db.define_table('menuItems',
    Field('restaurantID'),
    Field('dishName', required = True),
    Field('description', required = True),
    Field('price', required = True),
    Field('image', 'upload'),
    Field('tagCount'), # Dishes are limited to 5 tags. This wont be too hard, for each menuItem we just need to check how many Tags get returned for a given menuID query.
                       # If 5 are found, we prevent the restaurant owner from adding more. If more than 5 are found, we can just trim off tags arbitrarily.
    )
db.menuItems.restaurantID.readable = db.menuItems.restaurantID.writable = False

# Each element of menuTags is a short, textual tag belonging to a single menuItem. To build a list of tags, query menuTags for a given menuItem tag.
db.define_table('menuTags',
    Field('menuID'),
    Field('tag'),
    )
db.menuTags.menuID.readable = db.menuTags.menuID.writable = False

STATES = ['Alabama', 'Alaska','Arizona', 'Arkansas', 'California','Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine','Maryland','Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota','Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington','West Virginia', 'Wisconsin', 'Wyoming']

db.addresses.requires = IS_IN_SET(STATES)

db.users.phone.requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.users.email.requires = IS_EMAIL()

db.restaurants.phone.requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.restaurants.email.requires = IS_EMAIL()
