"""
This file defines the database models
"""

from .common import db, Field, T, auth
from pydal.validators import *

import datetime
import pytz



# set local config
import locale

locale.setlocale(locale.LC_ALL, 'Italian')
locale.getdefaultlocale()


### Define your table below

# config table 
db.define_table('config', 
        Field('code',"string"),
        Field('value',"string"))


# months table 
db.define_table('months', 
        Field('description', requires=IS_NOT_EMPTY(), label=T('Month'), format='%(month)s'))

# time table 
db.define_table('time', 
        Field('time', requires=IS_NOT_EMPTY(), label=T('Time'), format='%(time)s'),
        Field('multiplier', 'integer' ) )



# Staff table 
db.define_table('staff', 
        Field('name', requires=IS_NOT_EMPTY(), label=T('Name'), format='%(name)s'),
        Field('email', label=T('E-mail'), format='%(email)s', requires=IS_EMAIL(error_message=T('invalid email!'))),
        Field('telephon', label=T('Telephon N'), format='%(telephon num)s'),
        Field('address', label=T('Address'), format='%(address)s'))
        
# Payrolls table 
db.define_table('payrolls', 
        Field('code', "string", length=20,   requires=IS_NOT_EMPTY(), label=T('Code'), format='%(code)s'),
        Field('month_id', "reference months", label=T('Month'),  requires=IS_IN_DB(db, 'months.id','%(description)s',orderby=db.months.id)),
        Field('amount', "decimal(6,2)",label=T('Amount'),represent=lambda v: locale.format_string('%.0f CFA', v, grouping=True, monetary=True) if v is not None else '' ),
        Field('currency', "string", length=3,label=T('Currency'), default="CFA",),
        Field('staff_id', "reference staff", label=T('Name'), format='%(name)s', requires=IS_IN_DB(db, 'staff.id', '%(name)s', orderby=db.staff.name)) ,
        Field('generated',"datetime", label=T('Generated'), requires=IS_DATETIME(format='%Y-%m-%d %H:%M:%S' ) ) )

db.payrolls.currency.readable = True
db.payrolls.currency.writable = False


# Rooms category table 
db.define_table('rooms_category', 
        Field('category', "string", length=20,   requires=IS_NOT_EMPTY(), label=T('Category'), format='%(category)s'),
       # Field('price', "decimal(6,2)", label=T('Price')),  
       # Field('currency', "string", length=3,label=T('Currency'), default="CFA",),
        Field('maintenance_time', "integer", label=T('Maintenance Time'),  requires=IS_NOT_EMPTY() ) ,
        Field('placers', "integer", label=T('Placers'),  requires=IS_NOT_EMPTY() ) )

#db.rooms_category.currency.readable = True
#db.rooms_category.currency.writable = False

# Rooms status table a
db.define_table('status', 
        Field('status', "string", length=20,   requires=IS_NOT_EMPTY(), label=T('Status'), format='%(status)s') ,
        Field('maintenance', "boolean") ,
        Field('sel_formula', "boolean") ,
        Field('sel_rooms', "boolean") 

        )


# Rooms  table 
db.define_table('rooms', 
        Field('number', "string", length=20,   requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'rooms.number', error_message='Room alredy inserted ')], label=T('Number'), format='%(number)s'),
        Field('description', "string", length=20,    label=T('Description'), format='%(description)s'),
        Field('category', "reference rooms_category", label=T('Category'), requires=IS_IN_DB(db, 'rooms_category.id', '%(category)s', orderby=db.rooms_category.category)) ,
        Field('status', "reference status", label=T('Status'), requires=IS_IN_DB(db, 'status.id', '%(status)s', orderby=db.status.status) ,default=1)  )

# Rooms  status table 
#db.define_table('rooms_status', 
#        Field('room', db.rooms,  required=True, requires=IS_IN_DB(db, 'rooms.id', '%(number)s', orderby=db.rooms.number)) ,  
#        Field('status', "reference status", label=T('Status'), requires=IS_IN_DB(db, 'status.id', '%(status)s', orderby=db.status.status) ,default=1)  )
   
# Formula table 
db.define_table('formula', 
        #Field('name',   requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'formula.name', error_message='Formula alredy inserted ')], label=T('Name'), format='%(name)s'),
        Field('name',   requires=IS_NOT_EMPTY(), label=T('Name'), format='%(name)s'),
        Field('category', "reference rooms_category", requires=IS_IN_DB(db, 'rooms_category.id', '%(category)s', orderby=db.rooms_category.category)) ,  
        Field('duration', "integer", label=T('Stay duration'), requires=IS_INT_IN_RANGE(0, 100,
                        error_message='Duration invalid!') ,default=0),
        Field('time', "reference time", label=T('Time'), requires=IS_IN_DB(db, 'time.id', '%(time)s')  ),
        Field('tariff', "decimal(6,2)", label=T('Tariff'), requires=IS_INT_IN_RANGE(0, 1000000,
                        error_message='Tariff invalid!') ,represent=lambda v: locale.format_string('%.0f CFA', v, grouping=True, monetary=True) if v is not None else '' ),
       # Field('currency', "string", length=3,label=T('Currency'), default="CFA",),
        Field('next_status', "reference status", requires=IS_IN_DB(db, 'status.id', '%(status)s'),label=T('Next Status')) ,  
        Field('plug', "boolean", label=T('Plug') ) ,
        Field('plug_add_time', "integer", label=T('Plug Additional Minuts'),requires = IS_INT_IN_RANGE(0, 30,
                        error_message='Additional time too large!'),default=0 ) ,
        Field('ligth', "boolean", label=T('Ligth') ) ,
        Field('ligth_add_time', "integer", label=T('Ligth Additional Minuts'),requires = IS_INT_IN_RANGE(0, 30,
                        error_message='Additional time too large!'),default=0 ) ,
        Field('ac', "boolean", label=T('Ac') ) ,
        Field('ac_add_time', "integer", label=T('Ac Additional Minuts'),requires = IS_INT_IN_RANGE(0, 30,
                        error_message='Additional time too large!') ,default=0) ,
                        
        migrate='formula.table'
)
    

#db.formula.currency.readable = True
#db.formula.currency.writable = False



# Reservation table 
db.define_table('reservation', 
        Field('room', "reference rooms", requires=IS_IN_DB(db, 'rooms.id', '%(number)s', orderby=db.rooms.number)) ,  
        Field('formula',"reference formula", requires=IS_IN_DB(db, 'formula.id', '%(name)s', orderby=db.formula.name)),
        Field('check_in', "datetime" ,represent=lambda v: datetime.datetime.strftime(v, "%d/%m/%Y %H:%M") if v is not None else ''),
        Field('check_out', "datetime" ,represent=lambda v: datetime.datetime.strftime(v, "%d/%m/%Y %H:%M") if v is not None else ''),
        #Field('total_amount', "float" ,represent=lambda v: '{:,}'.format(v) if v is not None else ''),
        Field('total_amount', "float" ,represent=lambda v: locale.format_string('%.0f CFA', v, grouping=True, monetary=True) if v is not None else ''),
        Field('total_nigth', "integer" ),
        Field('last_update', "datetime" ,label=T("Last Update"), default=datetime.datetime.now(pytz.timezone('Africa/Abidjan'))),
        Field('created_by', db.auth_user, label=T("Created by")),
        Field('completed', "boolean" , default = "False"),
        )

# Maintenance table 
db.define_table('maintenance', 
        Field('reservation', "reference reservation", requires=IS_IN_DB(db, 'reservation.id', '%(reservation)s')) ,  
        Field('room', "reference rooms", requires=IS_IN_DB(db, 'rooms.id', '%(number)s', orderby=db.rooms.number)) ,  
        Field('check_in', "datetime" ,represent=lambda v: datetime.datetime.strftime(v, "%d/%m/%Y %H:%M") if v is not None else ''),
        Field('check_out', "datetime" ,represent=lambda v: datetime.datetime.strftime(v, "%d/%m/%Y %H:%M") if v is not None else ''),
        Field('status', "reference status", label=T('Status'), requires=IS_IN_DB(db, 'status.id', '%(status)s', orderby=db.status.status) ,default=1)  ,
        Field('last_update', "datetime" ,label=T("Last Update"), default=datetime.datetime.utcnow()),
        Field('created_by', db.auth_user, label=T("Actualizado Por")),
        Field('start_maintenance', "datetime" ,represent=lambda v: datetime.datetime.strftime(v, "%d/%m/%Y %H:%M") if v is not None else ''),
        Field('stop_maintenance', "datetime" ,represent=lambda v: datetime.datetime.strftime(v, "%d/%m/%Y %H:%M") if v is not None else ''),
        Field('plug', "boolean" ),
        Field('ligth', "boolean" ),
        Field('add_time', "integer" ,default=0),

        )    
        

# Rooms controls table 
db.define_table('room_control', 
        Field('key') , 
        Field('type') , 
        Field('room', "reference rooms", requires=IS_IN_DB(db, 'rooms.id', '%(number)s', orderby=db.rooms.number)) ,  
) ,  


# profiles table 
db.define_table('user_profiles', 
        Field('profile', requires=IS_NOT_EMPTY(), label=T('Profile'), format='%(profile)s',error_message='prova'),
        Field('level', 'integer', requires=IS_NOT_EMPTY(), label=T('Level'), format='%(level)s'))

# user role 
db.define_table('user_roles', 
        Field('user_id', "reference auth_user", requires=IS_IN_DB(db, 'auth_user.id', '%(username)s'), 
        label=T('User'), format='%(role)s', error_message='prova' ),
        Field('profile_id', 'reference user_profiles', requires=IS_IN_DB(db, 'user_profiles.id', '%(profile)s'), label=T('Profile'), format='%(profile)s') )

        
# user language table 
db.define_table('user_language', 
        Field('user_id', 'integer', requires =  IS_IN_DB(db, 'auth_user.id', '%(user_name)s')),
        Field('language', 'string', requires=IS_NOT_EMPTY() ,default="fr", label=T('Language'), format='%(language)s'))

# application auth level table 
db.define_table('app_level', 
        Field('path', requires =  IS_NOT_EMPTY()),
        Field('min_level', "integer", requires=IS_NOT_EMPTY(), format='%(min_level)s'))

   
#
## always commit your models to avoid problems later
#
db.commit()
#
