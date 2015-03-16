import os
# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    form = ''
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
    return dict(startAsRestaurant=startAsRestaurant, startAsUser=startAsUser, form=form)

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

    form = SQLFORM.factory(Field('restaurantName',
                                 label='Restaurant Name',
                                 ),
                           Field('phone',
                                 label='Business Phone',
                                 requires = IS_MATCH('^1?(-?\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Enter a phone number as '(XXX)XXX-XXXX'. Country code is optional.")
                                 ),
                           Field('email',
                                 label='Business Email',
                                 requires = IS_EMAIL()
                                 ),
                           Field('description', 'text',
                                 label='Restaurant Description',
                                 ),
                          )
    if form.process().accepted:
        db.restaurants.insert(ownerID = auth.user.id,
                               restaurantName = form.vars.restaurantName,
                               phone = form.vars.phone,
                               email = form.vars.email,
                               description = form.vars.description,
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

    name = ''
    email = ''
    phone = ''
    desc = ''
    menu = ''
    restID = -1
    tags = [] # I'm not sure this is even used... -Sam
    tagForms = []

    restaurant = db(db.restaurants.id == request.args(0)).select().first()
    if restaurant is not None:
        name = restaurant.restaurantName
        email = restaurant.email
        phone = restaurant.phone
        desc = restaurant.description
        menu = db(db.menuItems.restaurantID == request.args(0)).select()
        restID = restaurant.id

        editDescForm = SQLFORM.factory(Field('description', 'text',
                                             requires = IS_NOT_EMPTY(),
                                             default=desc,
                                            ),
                                      )
        if editDescForm.process(formname='editDescForm').accepted:
            restaurant.update_record(description = editDescForm.vars.description)
            redirect(URL('default', 'manage', args=[request.args(0)]))

        editDescForm.elements('.w2p_fl', replace=None) # This removes the auto-generated labels from the form fields

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
                tagForms=tagForms,
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

def main():
    VERIFY_IS_USER(auth.user.id)

    return dict()

#This page will display the public info for a restaurant
#This page will navigate to an ordering page 
def restaurantPage():
    #args(0) is the restaurant_id
    #args(1) is optional--menu_id from which the user navigated from 

    restaurant = db(db.restaurants.id == request.args(0)).select().first()


    name = ''
    email = ''
    phone = ''
    desc = ''
    menu = ''
    restID = -1
    tags = []

    if restaurant is not None:
        name = restaurant.restaurantName
        email = restaurant.email
        phone = restaurant.phone
        desc = restaurant.description
        menu = db(db.menuItems.restaurantID == request.args(0)).select(orderby=db.menuItems.category)
        restID = restaurant.id

    cancelButton = A('Return To Main Page', _class='btn', _href=URL('default', 'main'))

    return dict(name=name, email=email, phone=phone, desc=desc, menu=menu, restID=restID, cancelButton=cancelButton)


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
