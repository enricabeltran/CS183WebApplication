from datetime import datetime
# -*- coding: utf-8 -*-

DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

HOURS = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
MINUTES = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56','57','58','59']

# Just a random partial list of restaurant culinary styles that can be used for the culinaryStyle list.
CUISINES = ['African', 'American', 'Argentinian', 'BBQ', 'Belgian', 'Brazilian', 'Breakfast/Brunch', 'Cajun and Creole', 'Cambodian', 'Caribbean', 'Chinese', 'Costa Rican', 'Cuban', 'Deli', 'Dessert', 'English', 'Filipino', 'French', 'German', 'Greek', 'Haitian', 'Halal', 'Hawaiian', 'Indian', 'Indonesian', 'Irish', 'Italian', 'Jamaican', 'Japanese', 'Juices', 'Korean', 'Kosher', 'Lebanese', 'Malaysian', 'Mediterranean', 'Mexican', 'Moroccan', 'Pakistani', 'Peruvian', 'Polish', 'Portuguese', 'Russian', 'Salads', 'Sandwiches/Wraps', 'Scandinavian', 'Seafood', 'Smoothies/Shakes', 'Southern and Soul', 'Spanish', 'Sri-Lankan', 'Steakhouse', 'Taiwanese', 'Thai', 'Turkish', 'Vegan/Vegetarian', 'Venezuelan', 'Vietnamese',]


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
    Field('cuisineType'),
    Field('description', 'text'),
    Field('priceRange'),              # We should pull this from outside source--not from user

    )
db.restaurants.ownerID.readable = db.restaurants.ownerID.writable = False
db.restaurants.addressID.readable = db.restaurants.addressID.writable = False
db.restaurants.cuisineType.requires = IS_IN_SET(CUISINES)
db.restaurants.phone.requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.restaurants.email.requires = IS_EMAIL()



#some resturants may have odd hours on different days 
"""Su: Closed
M-Th: 10am-2pm 5pm -9pm
F-Sa: 10 am - 3 pm 5pm- 11 pm""" #ect. -E
db.define_table('hours',
    Field('restaurantID', db.restaurants),
    Field('dayOfWeek'),
    Field('openAtHour', requires=IS_IN_SET(HOURS)),
    Field('openAtMinute', requires=IS_IN_SET(MINUTES)),
    Field('closedAtHour', requires=IS_IN_SET(HOURS)),
    Field('closedAtMinute',requires=IS_IN_SET(HOURS)),
)
db.hours.dayOfWeek.requires = IS_IN_SET(DAYS)


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
    Field('category', writable= True),
    Field('description', 'text', requires = IS_NOT_EMPTY()),
    Field('price', requires = IS_FLOAT_IN_RANGE(0, 1000)),
    Field('image', 'upload', requires=IS_EMPTY_OR(IS_IMAGE())),
    )
db.menuItems.restaurantID.readable = db.menuItems.restaurantID.writable = False
db.menuItems.dishName.label = 'Dish Name'
db.menuItems.category.label = 'Category (i.e. Lunch Combos, Appetizers, Desserts, ect.)'
db.menuItems.price.label = 'Price'
db.menuItems.image.label = 'Picture Image'
db.menuItems.id.readable = False
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

# VERIFY_IS_RESTAURANT and VERIFY_IS_USER can be used to quickly determine whether a user is of the restaurant type or user type.
# If the verification succeeds, nothing happens. If it fails, users are redirected to default/main and restaurant owners are redirected to
# default/restaurants. NOTE: This can also be used to check the status of users other than the one who is currently logged in.
def VERIFY_IS_RESTAURANT(userID):
    user = db(db.auth_user.id == userID).select().first()
    if(user == None):
        redirect(URL('default','index'))
    elif(user.accountType != 'Restaurant Representative'):
        redirect(URL('default', 'main'))

def VERIFY_IS_USER(userID):
    user = db(db.auth_user.id == userID).select().first()
    if(user == None):
        redirect(URL('default', 'index'))
    elif(user.accountType != 'User'):
        redirect(URL('default', 'restaurants'))
