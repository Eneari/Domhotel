
from py4web import action, request, abort, redirect, URL, response
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from pydal.validators import IS_NOT_EMPTY, IS_INT_IN_RANGE, IS_IN_SET, IS_IN_DB, IS_NOT_IN_DB, IS_DATETIME,IS_DATE_IN_RANGE



import os
from py4web import action, Field, DAL
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from py4web.utils.grid import Column

from pydal.tools.tags import Tags
from .utils import Authorized

# exposed as /examples/html_grid
@action("control/control")
@action("control/control/<path:path>", method=["POST", "GET"])
@action.uses(session, db, T ,"control/control.html")
def control_grid(path=None) :
    
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #print(language.language)
    
    T.select(language.language)

    if not Authorized("control/control" , user['id']) :
        redirect(URL('unauthorized'))
    
    
     #  controllers and used for all grids in the app
    grid_param = dict(
        rows_per_page=5,
        include_action_button_text=True,
        search_button_text="Filter",
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
    )
        
                               
    search_queries = [
        [T('By Room')  , lambda value: db.rooms.number.contains(value)],
        [T('By Description') , lambda value: db.rooms.description.contains(value)],
        [T('By Key'), lambda value: db.room_control.key.contains(value)],
    ]
    
    query = db.room_control.id > 0
    orderby = [db.room_control.id]
    #columns = [field for field in db.payrolls if field.readable]
    
    db.room_control.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')

    
    columns = [
        db.rooms.number,
        db.rooms.description,
        db.room_control.key,
        db.room_control.type,      
        
    ]
    
    #columns.insert(0, Column("Custom", lambda row: A("click me")))
    
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                field_id=db.room_control.id,
                left=[
                db.rooms.on(db.rooms.id == db.room_control.room),
                ],
                orderby=orderby,
                #headings = [ T("Room"),T("Description"), T("Formula"), T("Price"), SPAN(_class='fa fa-coins '),T("Total"), T("Check In"), T("Check Out")],
                headings = [ T("Room"),T("Description"), T("Key"), T("Type")],
                show_id=False,
                deletable=True,
                editable=True,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T , language=language.language)
