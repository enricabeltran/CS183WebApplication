import os
from gluon.tools import Mail
import json
import math
from pygeocoder import Geocoder
import pygeolib
# -*- coding: utf-8 -*-

def index():
    startAsRestaurant = ''
    startAsUser = ''

    #if user/rep is logged in
    if(auth.user != None):
        if(db.auth_user.accountType == 'User'):
            redirect(URL('default', 'main'))
        else:
            redirect(URL('default', 'restaurants'))
    else:
         startAsRestaurant = A('Start As Restuarant', _class='btn', _href=URL('default', 'login', args=['restaurant']))
         startAsUser = A('Start As User', _class='btn', _href=URL('default', 'login', args=['user']))

    return dict(startAsRestaurant=startAsRestaurant, startAsUser=startAsUser)

def login():

    destination = 'error'
    form = ''
    register = False
    #sends user to the correct login/register page
    if(request.args(1) and request.args(1)=='register'):
        register = True
        t = ''
        if(request.args(0)=='user'):
            t = 'User'
        else:
            t = 'Restaurant Representative'
        db.auth_user.accountType.default = t
        form = auth.register()
    elif (request.args(0) and request.args(0) == 'user'):
        form = auth.login()
        destination = 'main'
    elif (request.args(0) and request.args(0) == 'restaurant'):
        form = auth.login()
        destination = 'restaurants'

    return dict(destination=destination, form=form, register=register)




@auth.requires_login()
def restaurants():
    VERIFY_IS_RESTAURANT(auth.user.id)

    ownedRestaurants = db(db.restaurants.ownerID == auth.user.id).select() # Oh boy, I really don't remember the syntax for queries...
    ownerName = auth.user.first_name
    addRestaurantButton = A('Add A Restaurant', _class='btn', _href=URL('default', 'addRest'))

    return dict(ownedRestaurants=ownedRestaurants, ownerName=ownerName, addRestaurantButton=addRestaurantButton)

@auth.requires_login()
def addRest():
    VERIFY_IS_RESTAURANT(auth.user.id)

    STATES = ['Alabama', 'Alaska','Arizona', 'Arkansas', 'California','Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine','Maryland','Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota','Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington','West Virginia', 'Wisconsin', 'Wyoming']

    CUISINES = ['African', 'American', 'Argentinian', 'BBQ', 'Belgian', 'Brazilian', 'Breakfast/Brunch', 'Cajun and Creole', 'Cambodian', 'Caribbean', 'Chinese', 'Costa Rican', 'Cuban', 'Deli', 'Dessert', 'English', 'Filipino', 'French', 'German', 'Greek', 'Haitian', 'Halal', 'Hawaiian', 'Indian', 'Indonesian', 'Irish', 'Italian', 'Jamaican', 'Japanese', 'Juices', 'Korean', 'Kosher', 'Lebanese', 'Malaysian', 'Mediterranean', 'Mexican', 'Moroccan', 'Pakistani', 'Peruvian', 'Polish', 'Portuguese', 'Russian', 'Salads', 'Sandwiches/Wraps', 'Scandinavian', 'Seafood', 'Smoothies/Shakes', 'Southern and Soul', 'Spanish', 'Sri-Lankan', 'Steakhouse', 'Taiwanese', 'Thai', 'Turkish', 'Vegan/Vegetarian', 'Venezuelan', 'Vietnamese',]
    
    form = SQLFORM.factory(Field('restaurantName',
                                 label='Restaurant Name',
                                 ),
                           Field('cuisineType',
                                 label='Cuisine',
                                 requires = IS_IN_SET(CUISINES)
                                 ),
                           Field('phone',
                                 label='Business Phone',
                                 requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Enter a phone number as '(XXX)XXX-XXXX'. Country code is optional.")
                                 ),
                           Field('email',
                                 label='Business Email',
                                 requires = IS_EMAIL()
                                 ),
                           Field('streetAddress',
                                 label = 'Address',
                                 requires = IS_NOT_EMPTY(),
                                 ),
                           Field('city',
                                 label = 'City',
                                 requires = IS_NOT_EMPTY(),
                                 ),
                           Field('zipCode',
                                 label = 'Zip Code',
                                 requires = IS_NOT_EMPTY(),
                                ),
                           Field('usState',
                                 label = 'U.S. State',
                                 requires = IS_IN_SET(STATES),
                                 ),
                           Field('description', 'text',
                                 label='Restaurant Description',
                                 ),
                          )
    if form.process().accepted:
        try:
            geoQuery = Geocoder.geocode(form.vars.streetAddress + ', ' + form.vars.city + ', ' + form.vars.usState + ', ' + form.vars.zipCode)
            coords = geoQuery[0].coordinates
        except pygeolib.GeocoderError:
            coords = (None, None)
        db.restaurants.insert(ownerID = auth.user.id,
                              cuisineType = form.vars.cuisineType,
                              restaurantName = form.vars.restaurantName,
                              phone = form.vars.phone,
                              email = form.vars.email,
                              description = form.vars.description,
                              coordX = coords[0],
                              coordY = coords[1],
                              addressID =  db.addresses.insert(userID = auth.user.id,
                                                               streetAddress = form.vars.streetAddress,
                                                               city = form.vars.city,
                                                               zipCode = form.vars.zipCode,
                                                               usState = form.vars.usState,
                                                              )
                              )
        redirect(URL('default', 'restaurants'))

    return dict(form=form)

@auth.requires_login()
def deleteRest():
    VERIFY_IS_RESTAURANT(auth.user.id)

    db(db.restaurants.id == request.args(0)).delete()
    redirect(URL('default', 'restaurants'))

# Controller for managing a restaurant
@auth.requires_login()
def manage():
    VERIFY_IS_RESTAURANT(auth.user.id)

    DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    CUISINES = ['African', 'American', 'Argentinian', 'BBQ', 'Belgian', 'Brazilian', 'Breakfast/Brunch', 'Cajun and Creole', 'Cambodian', 'Caribbean', 'Chinese', 'Costa Rican', 'Cuban', 'Deli', 'Dessert', 'English', 'Filipino', 'French', 'German', 'Greek', 'Haitian', 'Halal', 'Hawaiian', 'Indian', 'Indonesian', 'Irish', 'Italian', 'Jamaican', 'Japanese', 'Juices', 'Korean', 'Kosher', 'Lebanese', 'Malaysian', 'Mediterranean', 'Mexican', 'Moroccan', 'Pakistani', 'Peruvian', 'Polish', 'Portuguese', 'Russian', 'Salads', 'Sandwiches/Wraps', 'Scandinavian', 'Seafood', 'Smoothies/Shakes', 'Southern and Soul', 'Spanish', 'Sri-Lankan', 'Steakhouse', 'Taiwanese', 'Thai', 'Turkish', 'Vegan/Vegetarian', 'Venezuelan', 'Vietnamese',]
    HOURS = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
    MINUTES = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56','57','58','59']

    name = ''
    email = ''
    phone = ''
    desc = ''
    menu = ''
    cuisine = ''
    hours = []
    restID = -1
    tags = [] # I'm not sure this is even used... -Sam
    tagForms = []
    addHoursForm = ''

    restaurant = db(db.restaurants.id == request.args(0)).select().first()
    address = db(db.addresses.id == restaurant.addressID).select().first()
    if restaurant is not None:
        name = restaurant.restaurantName
        email = restaurant.email
        phone = restaurant.phone
        desc = restaurant.description
        coordX = restaurant.coordX
        coordY = restaurant.coordY
        menu = db(db.menuItems.restaurantID == request.args(0)).select()
        hours = db(db.hours.restaurantID == request.args(0)).select()
        restID = restaurant.id
        address = db(db.addresses.id == restaurant.addressID).select().first()
        cuisine = restaurant.cuisineType

        editDescForm = SQLFORM.factory(Field('description', 'text',
                                             requires = IS_NOT_EMPTY(),
                                             default=desc,
                                            ),
                                      )
        if editDescForm.process(formname='editDescForm').accepted:
            restaurant.update_record(description = editDescForm.vars.description)
            redirect(URL('default', 'manage', args=[request.args(0)]))

        editDescForm.elements('.w2p_fl', replace=None) # This removes the auto-generated labels from the form fields
        editCuisineForm = SQLFORM.factory(Field('cuisineType',
                                             requires = IS_IN_SET(CUISINES),
                                             label = 'Cuisine',
                                             default=restaurant.cuisineType,
                                            ),
                                      )
        if editCuisineForm.process(formname='editCuisineForm').accepted:
            restaurant.update_record(cuisineType = editCuisineForm.vars.cuisineType)
            redirect(URL('default', 'manage', args=[request.args(0)]))

        editAddressForm = SQLFORM.factory(Field('streetAddress',
                                 label = 'Address',
                                 default = address.streetAddress,
                                 requires = IS_NOT_EMPTY(),
                                 ),
                           Field('city',
                                 label = 'City',
                                 default = address.city,
                                 requires = IS_NOT_EMPTY(),
                                 ),
                           Field('zipCode',
                                 label = 'Zip Code',
                                 default = address.zipCode,
                                 requires = IS_NOT_EMPTY(),
                                ),
                           Field('usState',
                                 label = 'U.S. State',
                                 default = address.usState,
                                 requires = IS_IN_SET(STATES),
                                 ),
                       )
        if editAddressForm.process(formname='editAddressForm').accepted:
            addString = editAddressForm.vars.streetAddress + ', ' + editAddressForm.vars.city + ', ' + editAddressForm.vars.usState + ', ' + editAddressForm.vars.zipCode
            try:
                geoQuery = Geocoder.geocode(addString)
                coords = geoQuery[0].coordinates
            except pygeolib.GeocoderError:
                coords = (None, None)

            session.flash = coords
            if address is not None:
                address.update_record(streetAddress = editAddressForm.vars.streetAddress,
                                      city = editAddressForm.vars.city,
                                      zipCode = editAddressForm.vars.zipCode,
                                      usState = editAddressForm.vars.usState,
                                     )
            else:
                db.addresses.insert(streetAddress = editAddressForm.vars.streetAddress,
                                    city = editAddressForm.vars.city,
                                    zipCode = editAddressForm.vars.zipCode,
                                    usState = editAddressForm.vars.usState,
                                    userID = auth.user.id,
                                    #restaurantID = request.args(0),
                                   )
            restaurant.update_record(coordX = coords[0],
                                     coordY = coords[1],
                                    )
            redirect(URL('default', 'manage', args=[request.args(0)]))


        addHoursForm = SQLFORM.factory(Field('dayOfWeek',
                                             requires = IS_IN_SET(DAYS),
                                             default = 'Sunday',
                                             label = 'Day',
                                             ),
                                       Field('openAtHour',
                                             requires = IS_IN_SET(HOURS),
                                             label = 'Opens at (hour)',
                                             ),
                                       Field('openAtMinute',
                                             requires = IS_IN_SET(MINUTES),
                                             label = 'Opens at (minute)',
                                             ),
                                       Field('closedAtHour',
                                             requires = IS_IN_SET(HOURS),
                                             label = 'Closes at (hour)',
                                             ),
                                       Field('closedAtMinute',
                                             requires = IS_IN_SET(MINUTES),
                                             label = 'Closes at (minute)',
                                             ),
                                       )

        def earlier(openHour,openMinute, closeHour, closeMinute):
            if int(openHour) == int(closeHour):
                return int(openMinute)<int(closeMinute)
            else:
                return int(openHour)<int(closeHour)

        def getMin(hoursList):
            minIndex = 0
            for i in range(0, len(hoursList)):
                if earlier(hoursList[minIndex].openAtHour, hoursList[minIndex].openAtMinute, hoursList[i].openAtHour, hoursList[i].openAtMinute):
                    minIndex = i
            return minIndex

        def sortHours(hoursList):
            sortedHours = hoursList
            for i in range(0, len(sortedHours)):
                minIndex = getMin(sortedHours)
                tempHours = sortedHours[i]
                sortedHours[i] = sortedHours[minIndex]
                sortedHours[minIndex] = tempHours
            return sortedHours

        sun = []
        mon = []
        tue = []
        wed = []
        thu = []
        fri = []
        sat = []
        for x in range(0, len(hours)):
            if hours[x].dayOfWeek == "Sunday":
                sun.append(hours[x])
            elif hours[x].dayOfWeek == "Monday":
                mon.append(hours[x])
            elif hours[x].dayOfWeek == "Tuesday":
                tue.append(hours[x])
            elif hours[x].dayOfWeek == "Wednesday":
                wed.append(hours[x])
            elif hours[x].dayOfWeek == "Thursday":
                thu.append(hours[x])
            elif hours[x].dayOfWeek == "Friday":
                fri.append(hours[x])
            else:
                sat.append(hours[x])
            pass
        pass
        sun = sortHours(sun)
        mon = sortHours(mon)
        tue = sortHours(tue)
        wed = sortHours(wed)
        thu = sortHours(thu)
        fri = sortHours(fri)
        sat = sortHours(sat)

        if addHoursForm.process(formname='addHoursForm').accepted:
            if earlier(int(addHoursForm.vars.openAtHour), int(addHoursForm.vars.openAtMinute), int(addHoursForm.vars.closedAtHour), addHoursForm.vars.closesAtMinute):
                db.hours.insert(restaurantID = request.args(0),
                                    dayOfWeek = addHoursForm.vars.dayOfWeek,
                                    openAtHour = addHoursForm.vars.openAtHour,
                                    openAtMinute = addHoursForm.vars.openAtMinute,
                                    closedAtHour = addHoursForm.vars.closedAtHour,
                                    closedAtMinute = addHoursForm.vars.closedAtMinute,
                                   )
                redirect(URL('default', 'manage', args=[request.args(0)]))
            else:
                session.flash="Invalid time range. Please make sure your opening time is earlier than your closing time."
                redirect(URL('default', 'manage', args=[request.args(0)]))

        editContactForm = SQLFORM.factory(Field('phone',
                                                label='New Business Phone',
                                                default = phone,
                                                requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',
                                                                    error_message="Enter a phone number as '(XXX)XXX-XXXX'. Country code is optional.")
                                               ),
                                          Field('email',
                                                label='New Business Email',
                                                default = email,
                                                requires = IS_EMAIL()
                                               ),
                                         )
        if editContactForm.process(formname='editContactForm').accepted:
            restaurant.update_record(phone=editContactForm.vars.phone, email=editContactForm.vars.email)
            redirect(URL('default', 'manage', args=[request.args(0)]))
        # Finally, let's generate an 'addTag' form for each menu item...
        for i in range(0, len(menu)):
            tempForm = SQLFORM.factory(Field('tag', requires = IS_NOT_EMPTY()),
                                      )
            if tempForm.process(formname='tagForm'+str(i)).accepted:
                db.menuTags.insert(menuID = menu[i].id,
                                   tag = tempForm.vars.tag,
                                  )
                redirect(URL('default', 'manage', args=[request.args(0)]))
            tagForms.append(tempForm)

        db.menuItems.restaurantID.default = request.args(0)
        menuItemForm = SQLFORM(db.menuItems,upload=URL('download'))
        if menuItemForm.process().accepted:
            session.flash = T("Added")
            redirect(URL('default', 'manage', args=[request.args(0)]))

    newMenuItemButton = A('Create a New Menu Item', _class='btn', _href=URL('default', 'createMenuItem', args=[restID]))
    cancelButton = A('Return To Restaurants', _class='btn', _href=URL('default', 'restaurants'))
    return dict(name=name,
                email=email,
                phone=phone,
                desc=desc,
                menu=menu,
                restID=restID,
                newMenuItemButton=newMenuItemButton,
                cancelButton=cancelButton,
                editDescForm=editDescForm,
                editContactForm=editContactForm,
                address=address,
                coordX=coordX,
                coordY=coordY,
                editAddressForm=editAddressForm,
                tagForms=tagForms,
                menuItemForm=menuItemForm,
                addHoursForm=addHoursForm,
                hours=hours,
                editCuisineForm=editCuisineForm,
                cuisine=cuisine,
                sun=sun,
                mon=mon,
                tue=tue,
                wed=wed,
                thu=thu,
                fri=fri,
                sat=sat,
               )

@auth.requires_login()
def createMenuItem():
    VERIFY_IS_RESTAURANT(auth.user.id)

    restaurantName = db(db.restaurants.id == request.args(0)).select(db.restaurants.restaurantName).first().restaurantName

    db.menuItems.restaurantID.default = request.args(0)
    form = SQLFORM(db.menuItems,upload=URL('download'))
    if form.process().accepted:
        session.flash = T("Added")
        redirect(URL('default', 'manage', args=[request.args(0)]))

    cancelButton = A('Cancel', _class='btn', _href=URL('default', 'manage', args = [request.args(0)]))

    return dict(form=form, cancelButton=cancelButton, restaurantName=restaurantName)

@auth.requires_login()
def editMenuItem():
    VERIFY_IS_RESTAURANT(auth.user.id)
    #ADD CODE TO VERIFY THAT THE USER OWNS THIS MENU ITEM
    dish = db(db.menuItems.id == request.args(1)).select().first() #item to be edited

    form = SQLFORM(db.menuItems, record = dish, upload=URL('download'))
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'manage', args=[request.args(0)]))

    cancelButton = A('Cancel', _class='btn', _href=URL('default', 'manage', args = [request.args(0)]))

    return dict(form=form, cancelButton=cancelButton, dish=dish)

@auth.requires_login()
def deleteMenuItem():
    VERIFY_IS_RESTAURANT(auth.user.id)
    #ADD CODE TO VERIFY THAT THE USER OWNS THIS MENU ITEM

    db(db.menuItems.id == request.args(0)).delete()

    redirect(URL('default', 'manage', args = [request.args(1)]))

@auth.requires_login()
def tag():
    VERIFY_IS_RESTAURANT(auth.user.id)

    form = SQLFORM.factory(Field('tag', requires = IS_NOT_EMPTY()),
                          )
    if form.process().accepted:
        db.menuTags.insert(menuID = request.args(0),
                           tag = form.vars.tag,
                          )

        redirect(URL('default', 'manage', args=[request.args(1)]))

    cancelButton = A('Cancel', _class='btn', _href=URL('default', 'manage', args = [request.args(1)]))

    return dict(form=form, cancelButton=cancelButton)

@auth.requires_login()
def removetag():
    VERIFY_IS_RESTAURANT(auth.user.id)

    db(db.menuTags.id == request.args(0)).delete()

    redirect(URL('default', 'manage', args = [request.args(1)]))

@auth.requires_login()
def removehours():
    VERIFY_IS_RESTAURANT(auth.user.id)

    db(db.hours.id == request.args(0)).delete()

    redirect(URL('default', 'manage', args = [request.args(1)]))

def main():
    VERIFY_IS_USER(auth.user.id)
    def withinRadius(restaurant, userLocation, radius):
        R = 6371000
        latRad1 = math.radians(float(restaurant.coordX))
        latRad2 = math.radians(float(userLocation[0]))
        deltaLat = math.radians(float(userLocation[0])-float(restaurant.coordX))
        deltaLong = math.radians(float(userLocation[1])-float(restaurant.coordY))

        a = math.sin(deltaLat/2)*math.sin(deltaLat/2)+math.cos(latRad1)*math.cos(latRad2)*math.sin(deltaLong/2)*math.sin(deltaLong/2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a));

        d = R*c;
        return d<(radius*1000)

    restaurants = db(db.restaurants.id > 0).select()
    userLocation = (request.args(0), request.args(1))
    radius = request.args(2)
    closeBy = []

    if userLocation[0] is not None and userLocation[1] is not None:
        for i in range(0, len(restaurants)):
            if withinRadius(restaurants[i], userLocation, radius):
                closeBy.append(restaurants[i])

    return dict(restaurants=closeBy)

#This page will display the public info for a restaurant
#This page will navigate to an ordering page
def restaurantPage():
    #args(0) is the restaurant_id
    restaurant = db(db.restaurants.id == request.args(0)).select().first()

    name = ''
    email = ''
    phone = ''
    desc = ''
    menu = ''
    cuisine = ''
    restID = -1
    tags = []
    hours = []
    sun = []
    mon = []
    tue = []
    wed = []
    thu = []
    fri = []
    sat = []

    if restaurant is not None:
        name = restaurant.restaurantName
        email = restaurant.email
        phone = restaurant.phone
        desc = restaurant.description
        menu = db(db.menuItems.restaurantID == request.args(0)).select(orderby=db.menuItems.category)
        restID = restaurant.id
        cuisine = restaurant.cuisineType

        hours = db(db.hours.restaurantID == request.args(0)).select()

        def earlier(openHour,openMinute, closeHour, closeMinute):
            if int(openHour) == int(closeHour):
                return int(openMinute)<int(closeMinute)
            else:
                return int(openHour)<int(closeHour)

        def getMin(hoursList):
            minIndex = 0
            for i in range(0, len(hoursList)):
                if earlier(hoursList[minIndex].openAtHour, hoursList[minIndex].openAtMinute, hoursList[i].openAtHour, hoursList[i].openAtMinute):
                    minIndex = i
            return minIndex

        def sortHours(hoursList):
            sortedHours = hoursList
            for i in range(0, len(sortedHours)):
                minIndex = getMin(sortedHours)
                tempHours = sortedHours[i]
                sortedHours[i] = sortedHours[minIndex]
                sortedHours[minIndex] = tempHours
            return sortedHours

        for x in range(0, len(hours)):
            if hours[x].dayOfWeek == "Sunday":
                sun.append(hours[x])
            elif hours[x].dayOfWeek == "Monday":
                mon.append(hours[x])
            elif hours[x].dayOfWeek == "Tuesday":
                tue.append(hours[x])
            elif hours[x].dayOfWeek == "Wednesday":
                wed.append(hours[x])
            elif hours[x].dayOfWeek == "Thursday":
                thu.append(hours[x])
            elif hours[x].dayOfWeek == "Friday":
                fri.append(hours[x])
            else:
                sat.append(hours[x])
            pass
        pass
        sun = sortHours(sun)
        mon = sortHours(mon)
        tue = sortHours(tue)
        wed = sortHours(wed)
        thu = sortHours(thu)
        fri = sortHours(fri)
        sat = sortHours(sat)

    cancelButton = A('Return To Main Page', _class='btn', _href=URL('default', 'main'))

    return dict(cuisine=cuisine,
                name=name,
                email=email,
                phone=phone,
                desc=desc,
                menu=menu,
                restID=restID,
                cancelButton=cancelButton,
                sun=sun,
                mon=mon,
                tue=tue,
                wed=wed,
                thu=thu,
                fri=fri,
                sat=sat,
               )

def order():
    name = "Error: Restaurant Not Specified" 
    menu = []
    cart = []
    subtotal = 0.0
    backButton = A("Back", _class='btn', _href=URL('default', 'restaurantPage')) # This should check if the user came from the restaurantPage (somehow), and take then back accordingly--think the way we are set up right now, people will only be order by navigating through the restaurantPage
    #args(0) restaurantID
    #args(1) orderID
    
    if request.args(0) is not None:
        restaurant = db(db.restaurants.id == request.args(0)).select().first()
        name = restaurant.restaurantName
        menu = db(db.menuItems.restaurantID == restaurant.id).select()
        cart = db(db.orderItem.orderID == request.args(1)).select()
        for i in range(0,len(cart)):
            dish = db(db.menuItems.id == cart[i].menuID).select().first()
            subtotal += float(dish.price)
            
    return dict(name=name, menu=menu, cart=cart, backButton=backButton, subtotal=subtotal)

def addToOrder():
    #args(0) is restaurant
    #args(1) order number
    #args(2) menuItem
    db.orderItem.insert(orderID=request.args(1), menuID=request.args(2))
    redirect(URL('default', 'order', args = [request.args(0),request.args(1)]))
    
    return dict()


def deleteFromOrder():
    #args(0) is restaurant
    #args(1) order number
    #args(2) is orderItemID
    db(db.orderItem.id == request.args(2)).delete()
    redirect(URL('default', 'order', args = [request.args(0),request.args(1)]))
    
    return dict()

def confirmOrder():
    #args(0) orderID
    #args(1) restuarantID
    mail = Mail()
    mail.settings.server = 'smtp.gmail.com:587'
    mail.settings.sender = 'feedrinc@gmail.com'
    mail.settings.login = 'feedrinc:cs183webapps'
    restaurant = db(db.restaurants.id == request.args(1)).select().first()
    order = db(db.orders.id == request.args(0)).select().first()
    cart = []
    customer = ''
    customerName =auth.user.first_name +' '+auth.user.last_name
    subtotal = 0.0
    if order is not None:
        cart = db(db.orderItem.orderID == request.args(0)).select()
        for i in range(0,len(cart)):
            dish = db(db.menuItems.id == cart[i].menuID).select().first()
            subtotal += float(dish.price)
    contactForm = editAddressForm = SQLFORM.factory(Field('phone',
                                                          label = 'Phone',
                                                          requires = IS_NOT_EMPTY()),
                           Field('email',
                                 label = 'Email',
                                 default = auth.user.email,
                                 requires = IS_NOT_EMPTY()
                                 ),
                           Field('streetAddress',
                                 label = 'Address',
                                 requires = IS_NOT_EMPTY(),
                                 ),
                           Field('city',
                                 label = 'City',
                                 requires = IS_NOT_EMPTY(),
                                 ),
                           Field('zipCode',
                                 label = 'Zip Code',
                                 requires = IS_NOT_EMPTY(),
                                ),
                           Field('usState',
                                 label = 'U.S. State',
                                 requires = IS_IN_SET(STATES),
                                 ),
                           Field('confirm', 'boolean',
                                 label = 'Confirm?',
                                 default = False,
                                 ),
                       )
    if contactForm.process(formname='contactForm').accepted:
        if(contactForm.vars.confirm!=True):
            session.flash = 'Please click on confirm checkbox'
            redirect(URL('default', 'confirmOrder', args=[request.args(0),request.args(1)]))
        else:
            order.update(addressID =
                db.addresses.insert(streetAddress = contactForm.vars.streetAddress,
                                    city =  contactForm.vars.city,
                                    zipCode = contactForm.vars.zipCode,
                                    usState = contactForm.vars.usState,
                                    userID = auth.user.id,
                                   )
                        )
            m = 'Contents of Order #'+request.args(0)+'\n'
            for i in range(0, len(cart)):
                dish = db(db.menuItems.id == cart[i].menuID).select().first()
                m = m + dish.dishName +'\t $'+dish.price+'\n'
            m = m +'\n Subtotal: $'+str(subtotal) + '\n'
            m = m +'Customer Order Information: \n'+ customerName +'\n' + contactForm.vars.email +'\n' + contactForm.vars.phone +'\n' +contactForm.vars.streetAddress+'\n'+contactForm.vars.city+'n'+conactForm.vars.zipCode+'\n'+contactForm.vars.usState
            
            mail.send(to=[restaurant.email],
                        subject='New: Order#'+request.args(0),
                        # If reply_to is omitted, then mail.settings.sender is used
                        message=m )
            mail.send(to=[contactForm.vars.email],
                        subject='Order#'+request.args(0)+' Sent!',
                        # If reply_to is omitted, then mail.settings.sender is used
                        message= 'This is what we sent to the restaurant!:\n' + m )
            redirect(URL('default', 'orderSent', args=[request.args(0),request.args(1)]))

    
            
        
    return dict(cart=cart, subtotal=subtotal, restaurant=restaurant, contactForm=contactForm)

def orderSent():
    #args(0) orderID
    #args(1) restuarantID
    restaurant = db(db.restaurants.id == request.args(1)).select().first()
    order = db(db.orders.id ==request.args(0)).select().first()
    cart = db(db.orderItem.orderID == request.args(0)).select()
    return dict(restaurant=restaurant, order=order, cart=cart)

def startOrder():
        #args(0) ->restuarantID
        orderNum = db.orders.insert(userID= auth.user.id,
                                    restaurantID = request.args(0))
        redirect(URL('default', 'order', args=[request.args(0),orderNum]))
        return dict()

def about():
	return dict()
	
def contact():
	return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
