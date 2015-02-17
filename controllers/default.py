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
    
    #if user is logged in
    if(db.auth_user != None):
        #user has not been added to user or restaurant talbe
        if(db.auth_user.infoObtained == False):
            if(db.auth_user.accountType == 'User'):
                form = SQLFORM(db.users)
                if form.process().accepted:
                    db.auth_user.infoObtained = True
                    session.flash("inserted into table")
                    redirect(URL('default', 'main'))
            #elif(db.auth_user.accountType == 'Restaurant Representative'):
            else:
                form = SQLFORM(db.restaurants)
                if form.process().accepted:
                    db.auth_user.infoObtained = True
                    session.flash("inserted into table")
                    redirect(URL('default', 'restaurants'))
    else:
        startAsRestaurant = A('Start As Restuarant', _class='btn', _href=URL('default', 'login', args=['restaurant']))
        startAsUser = A('Start As User', _class='btn', _href=URL('default', 'login', args=['user']))
    return dict(startAsRestaurant=startAsRestaurant, startAsUser=startAsUser)

def login():
    #need to figure out how to implement auth_group
    
    destination = 'error'
    form = ''
    register = False
    if(request.args(1) and request.args(1)=='register'):
        register = True
        form = auth.register()
    elif (request.args(0) and request.args(0) == 'user'):
        form = auth.login()
        destination = 'main'
    elif (request.args(0) and request.args(0) == 'restaurant'):
        form = auth.login()
        destination = 'restaurants'
        
    return dict(destination=destination, form=form, register=register)



def restaurants():
    return dict()

def main():
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
