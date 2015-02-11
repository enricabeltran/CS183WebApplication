# -*- coding: utf-8 -*-
db.define_table('restaurants',
    Field('account_ID', unique=True),
    Field('name'),
    Field('email'),
    Field('phone'),
    Field('address'),                 # Should be reference to external table
    Field('culinaryStyle'),
    Field('priceRange'),
    Field('menu'),                    # Should be reference to external table
    Field('images'),                  # Should be reference to external table
    Field('description', 'text'),
    )

db.define_table('users',
    Field('account_ID', unique=True),
    Field('name'),
    Field('email'),
    Field('phone'),
    Field('paymentInformation'),      # Should be reference to external table
    Field('address'),                 # Should be reference to external table
    )
