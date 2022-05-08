
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, SPAN, BUTTON, INPUT
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from pydal.validators import IS_NOT_EMPTY, IS_INT_IN_RANGE, IS_IN_SET, IS_IN_DB, IS_NOT_IN_DB, IS_DATETIME,IS_DATE_IN_RANGE


import os
from py4web import action, Field, DAL
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from py4web.utils.grid import Column
from .utils import Authorized


from py4web import Flash

import datetime

flash = Flash()
@action("maintenance/unauthorized")
@action.uses(flash, "maintenance/unauthorized.html")
def unhautorized():
    return dict()



# exposed as /html_grid
@action("maintenance/cleaning")
@action("maintenance/cleaning/<lista:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/cleaning.html")
def cleaning_grid(lista=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
    
    if (lista != None ) :
        print("lista-----")
        #print(request)
        print(lista)
        
        idx = lista.split('/')
        
        print(len(idx))
        data_stop = idx.pop(len(idx)-1)
        data_start = idx.pop(len(idx)-1)
        data_start = data_start.replace('-','/')
        data_stop = data_stop.replace('-','/')

        print ( data_start)
        print(data_stop)
        print(idx)

        
        # update maintenance & rooms status ---
        for elm in idx :
            print(elm)
            db(db.rooms.number == elm).update(status = 3)
            row = db((db.maintenance.room == db.rooms.id) & (db.rooms.number == elm)).select(db.maintenance.id).first()
            db(db.maintenance.id == row.id).update(status = 3,
                            start_maintenance=datetime.datetime.strptime(data_start,"%d/%m/%Y %H:%M"),
                            stop_maintenance=datetime.datetime.strptime(data_stop,"%d/%m/%Y %H:%M"))
       
        
    # update room reservation status
    from .utils import UpdateStatus
    UpdateStatus()
    
   
    # show list -------------------
      
        
    #  controllers and used for all grids in the app
    grid_param = dict(
        rows_per_page=10,
        include_action_button_text=True,
        search_button_text="Filter",
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
    )
        
                               
    search_queries = [
        [T('By Room')  , lambda value: db.rooms.number.contains(value)],
        [T('By Description') , lambda value: db.rooms.description.contains(value)],
        [T('By Formula'), lambda value: db.formula.name.contains(value)],
    ]
    
    query = db.maintenance.status == 5
    orderby = [db.maintenance.check_out]
    #columns = [field for field in db.payrolls if field.readable]
   
    db.maintenance.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')
            
    columns = [
        db.rooms.number,
        db.rooms.description,
        db.rooms_category.category,
        db.maintenance.check_in,
        db.maintenance.check_out,
    ]
    
    #columns.insert(0, Column("Select", lambda row: A("click me")))
    columns.insert(0, Column("Select", lambda row: INPUT(_type='checkbox', _name='test', _value='', value='b')))

    path = None
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                field_id=db.maintenance.id,
                left=[
                db.rooms.on(db.rooms.id == db.maintenance.room),
                db.rooms_category.on(db.rooms_category.id == db.rooms.category),

                ],
                orderby=orderby,
                headings = [T("Select"), T("Room"),T("Description"), T("Category"), T("Check In"), T("Check Out")],
                show_id=True,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T , language=language.language)



# exposed as /html_grid
@action("maintenance/on_cleaning")
@action("maintenance/on_cleaning/<lista:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/on_cleaning.html")
def on_cleaning_grid(lista=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
    
    if (lista != None ) :
        print("lista-----")
        #print(request)
        print(lista)
        
        idx = lista.split('/')
        
        print(len(idx))
        data_stop = idx.pop(len(idx)-1)
        data_stop = data_stop.replace('-','/')

        print(data_stop)
        print(idx)
    
    # update maintenance & rooms status ---
        for elm in idx :
            print(elm)
            db(db.rooms.number == elm).update(status = 1)
            row = db((db.maintenance.room == db.rooms.id) & (db.rooms.number == elm)).select(db.maintenance.id).first()
            db(db.maintenance.id == row.id).update(status = 6,
                            stop_maintenance=datetime.datetime.strptime(data_stop,"%d/%m/%Y %H:%M"))
    
    # show list -------------------
      
        
    #  controllers and used for all grids in the app
    grid_param = dict(
        rows_per_page=10,
        include_action_button_text=True,
        search_button_text="Filter",
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
    )
        
                               
    search_queries = [
        [T('By Room')  , lambda value: db.rooms.number.contains(value)],
        [T('By Description') , lambda value: db.rooms.description.contains(value)],
        [T('By Formula'), lambda value: db.formula.name.contains(value)],
    ]
    
    query = db.maintenance.status == 3
    orderby = [db.maintenance.check_out]
    #columns = [field for field in db.payrolls if field.readable]
   
    db.maintenance.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')
            
    columns = [
        db.rooms.number,
        db.rooms.description,
        db.rooms_category.category,
        db.maintenance.check_in,
        db.maintenance.check_out,
        db.maintenance.start_maintenance,
        db.maintenance.stop_maintenance,

    ]
    
    #columns.insert(0, Column("Select", lambda row: A("click me")))
    columns.insert(0, Column("Select", lambda row: INPUT(_type='checkbox', _name='test', _value='', value='b')))

    path = None
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                field_id=db.maintenance.id,
                left=[
                db.rooms.on(db.rooms.id == db.maintenance.room),
                db.rooms_category.on(db.rooms_category.id == db.rooms.category),

                ],
                orderby=orderby,
                headings = [T("Select"), T("Room"),T("Description"), T("Category"), T("Check In"), T("Check Out"),T('Start Clean'),T('End Clean')],
                show_id=True,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T , language=language.language)
    
    
    
# exposed as /html_grid
@action("maintenance/cleaned")
#@action("maintenance/cleaneing/<lista:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/cleaned.html")
def cleaned_grid():
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
    
   
    # update room reservation status
    #from .utils import UpdateStatus
    #UpdateStatus()
    
   
    # show list -------------------
      
        
    #  controllers and used for all grids in the app
    grid_param = dict(
        rows_per_page=10,
        include_action_button_text=True,
        search_button_text="Filter",
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
    )
        
                               
    search_queries = [
        [T('By Room')  , lambda value: db.rooms.number.contains(value)],
        [T('By Description') , lambda value: db.rooms.description.contains(value)],
        [T('By Formula'), lambda value: db.formula.name.contains(value)],
    ]
    
    query = db.maintenance.status == 6
    orderby = [db.maintenance.check_out]
    #columns = [field for field in db.payrolls if field.readable]
   
    db.maintenance.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')
            
    columns = [
        db.rooms.number,
        db.rooms.description,
        db.rooms_category.category,
        db.maintenance.check_in,
        db.maintenance.check_out,
        db.maintenance.start_maintenance,
        db.maintenance.stop_maintenance,
    ]
    
    #columns.insert(0, Column("Select", lambda row: A("click me")))
    #columns.insert(0, Column("Select", lambda row: INPUT(_type='checkbox', _name='test', _value='', value='b')))

    path = None
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                field_id=db.maintenance.id,
                left=[
                db.rooms.on(db.rooms.id == db.maintenance.room),
                db.rooms_category.on(db.rooms_category.id == db.rooms.category),

                ],
                orderby=orderby,
                headings = [ T("Room"),T("Description"), T("Category"), T("Check In"), T("Check Out"),T('Start Clean'),T('End Clean')],
                show_id=True,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T , language=language.language)

