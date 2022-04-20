
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
import pytz

flash = Flash()
@action("maintenance/unauthorized")
@action.uses(flash, "maintenance/unauthorized.html")
def unhautorized():
    return dict()



# exposed as /html_grid
@action("maintenance/cleaning_list")
@action("maintenance/cleaning_list/<lista:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/cleaning_list.html")
def cleaning_grid(lista=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning_list" , user['id']) :
        redirect(URL('unauthorized'))
    
  
    # update room reservation status
    from .utils import UpdateStatus
    UpdateStatus()
    
    post_action_buttons = [
        lambda row: GridActionButton(
            url=(URL("maintenance/cleaning/"+str( row.maintenance.id))),
            text= T("Clean"),
            icon= "fa fa-broom" ,
            
        ) 
    ]
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
                headings = [T("Room"),T("Description"), T("Category"), T("Check In"), T("Check Out")],
                show_id=True,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                post_action_buttons = post_action_buttons,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T, language=language.language )



# exposed as /html_grid
@action("maintenance/on_cleaning")
@action("maintenance/on_cleaning/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/on_cleaning.html")
def on_cleaning_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
    
    
    post_action_buttons = [
        lambda row: GridActionButton(
            url=(URL("maintenance/cleaning_confirm/"+str( row.maintenance.id))),
            text= T("Cleaned"),
            icon= "fa fa-check" ,
            
        ) ,
        lambda row: GridActionButton(
            url=(URL("maintenance/cleaning_addTime/"+str( row.maintenance.id))),
            text= T("More Time"),
            icon= "fa fa-plus" ,
            
        ) 
    ]
    
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
        [T('By Category'), lambda value: db.rooms_category.category.contains(value)],
    ]
    
    query = db.maintenance.status == 3
    orderby = [db.maintenance.check_out]
    #columns = [field for field in db.payrolls if field.readable]
   
    db.maintenance.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')
            
    columns = [
        db.rooms.number,
        db.rooms.description,
        db.rooms_category.category,
        db.maintenance.check_out,
        db.maintenance.start_maintenance,
        db.maintenance.stop_maintenance,
        db.maintenance.add_time,

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
                headings = [T("Room"),T("Description"), T("Category"), T("Check Out"),T('Start Cleaning'),T('End Cleaning'),T("Add.Time")],
                show_id=True,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                post_action_buttons = post_action_buttons,
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
        [T('By Category'), lambda value: db.rooms_category.category.contains(value)],
    ]
    
    query = db.maintenance.status == 6
    orderby = [db.maintenance.check_out]
    #columns = [field for field in db.payrolls if field.readable]
   
    db.maintenance.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')
            
    columns = [
        db.rooms.number,
        db.rooms.description,
        db.rooms_category.category,
        db.maintenance.check_out,
        db.maintenance.start_maintenance,
        db.maintenance.stop_maintenance,
        db.maintenance.add_time,

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
                headings = [ T("Room"),T("Description"), T("Category"), T("Check Out"),T('Start Cleaning'),T('End Cleaning'),T("Add.Time")],
                show_id=True,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T , language=language.language)



@action("maintenance/cleaning")
@action("maintenance/cleaning/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/cleaning.html")
def cleaning(path=None):
    
    print(path)
    print(len(path))
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
        
    if len(path) < 30 :
        
        room = db((db.maintenance.id == path) & (  db.maintenance.room == db.rooms.id  ) &
                (db.rooms.category == db.rooms_category.id) & (db.maintenance.status == db.status.id) ).select(
                    db.rooms.number,db.rooms.description,db.rooms_category.category, 
                    db.rooms_category.maintenance_time,
                    db.maintenance.check_in, db.maintenance.check_out,db.status.status,
                    db.maintenance.last_update,db.maintenance.created_by).first()
        
        start  = datetime.datetime.now(pytz.timezone('Africa/Abidjan'))
        stop = start +datetime.timedelta(minutes = room.rooms_category.maintenance_time)
        start  = datetime.datetime.strftime(start, "%d/%m/%Y %H:%M")
        stop  = datetime.datetime.strftime(stop, "%d/%m/%Y %H:%M")
        
        return dict(T=T,  language=language.language, room=room, start =start, stop=stop)
    
    else :
        
        lista = path.split("/")
        maintenance_id = lista[0]
        room_number = lista[1]
        date_start = lista[2]
        date_stop  = lista[3]
        date_start = date_start.replace('-','/')
        date_stop = date_stop.replace('-','/')
        plug= True if lista[4]=='true' else False
        ligth= True if lista[5]=='true' else False
        
        db(db.rooms.number == room_number).update(status = 3)
        db(db.maintenance.id == maintenance_id).update(status = 3,
            start_maintenance=datetime.datetime.strptime(date_start,"%d/%m/%Y %H:%M"),
            stop_maintenance=datetime.datetime.strptime(date_stop,"%d/%m/%Y %H:%M"),
            plug = plug, ligth=ligth)


        redirect(URL('maintenance/cleaning_list'))


@action("maintenance/cleaning_confirm")
@action("maintenance/cleaning_confirm<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/cleaning_confirm.html")
def cleaning_confirm(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
        
    if len(request.query) == 0 :
        lista = path.split("/")
        maintenance_id = lista[1]
        
        room = db((db.maintenance.id == maintenance_id) & (  db.maintenance.room == db.rooms.id  ) &
               (db.rooms.category == db.rooms_category.id) & (db.maintenance.status == db.status.id) ).select(
                    db.rooms.number,db.rooms.description,db.rooms_category.category, 
                    db.rooms_category.maintenance_time,
                    db.maintenance.check_in, db.maintenance.check_out,db.status.status,
                    db.maintenance.last_update,db.maintenance.created_by,
                    db.maintenance.start_maintenance,db.maintenance.stop_maintenance,
                    db.maintenance.room,db.maintenance.add_time,db.maintenance.id).first()
        
      
        return dict(T=T,  language=language.language, room=room)
    
    else :
        
        db(db.maintenance.id == request.query["id"]).update(status=6 )
        db(db.rooms.id == request.query["room_id"]).update(status=1 )


        redirect(URL('maintenance/on_cleaning'))
        

@action("maintenance/cleaning_addTime")
@action("maintenance/cleaning_addTime<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "maintenance/cleaning_addTime.html")
def cleaning_addTime(path=None):
      
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("maintenance/cleaning" , user['id']) :
        redirect(URL('unauthorized'))
        
    if len(request.query) == 0 :
        lista = path.split("/")
        maintenance_id = lista[1]
        
        room = db((db.maintenance.id == maintenance_id) & (  db.maintenance.room == db.rooms.id  ) &
                (db.rooms.category == db.rooms_category.id) & (db.maintenance.status == db.status.id) ).select(
                    db.rooms.number,db.rooms.description,db.rooms_category.category, 
                    db.rooms_category.maintenance_time,
                    db.maintenance.check_in, db.maintenance.check_out,db.status.status,
                    db.maintenance.last_update,db.maintenance.created_by,
                    db.maintenance.start_maintenance,db.maintenance.stop_maintenance,
                    db.maintenance.plug,db.maintenance.ligth,db.maintenance.id).first()
        
        return dict(T=T,  language=language.language, room=room)
    
    else :
       
        old_add_time = db(db.maintenance.id == request.query["id"]).select(db.maintenance.add_time).first()
        
        db(db.maintenance.id == request.query["id"]).update(
            stop_maintenance=datetime.datetime.strptime(request.query["data_stop"],"%d/%m/%Y %H:%M"),
            plug = True if request.query["plug"]=='true'  else False,
            ligth= True if request.query["ligth"]=='true' else False,
            add_time = int(request.query["add_time"]) + old_add_time.add_time
            )


        redirect(URL('maintenance/on_cleaning'))


        
class GridActionButton:
   def __init__(
      self,
      url,
      text=None,
      icon=None,
      onclick=None,
      additional_classes="",
      message="",
      append_id=False,
      ignore_attribute_plugin=False
   ):
      self.url = url
      self.text = text
      self.icon = icon
      self.onclick = onclick
      self.additional_classes = additional_classes
      self.message = message
      self.append_id = append_id
      self.ignore_attribute_plugin = ignore_attribute_plugin
      
      
      
      
