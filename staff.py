
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated


import os
from py4web import action, Field, DAL
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from py4web.utils.grid import Column

from pydal.tools.tags import Tags
from .utils import Authorized



from py4web import Flash

flash = Flash()
@action("staff/unauthorized")
@action.uses(flash, "staff/unauthorized.html")
def unhautorized():
    return dict()



# exposed as /examples/html_grid
@action("staff/list")
@action("staff/list/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "staff/list.html")
def staff_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("staff/list" , user['id']) :
        redirect(URL('unauthorized'))
        
    if  path != None and "new" in path :
        
        #print("FLASHHHHHHHHH")
        flash.set("Hello World", _class="info", sanitize=True)
        
    if Authorized("staff/edit" , user['id']) :
        editable = True
    else :
        editable = False
        
    if Authorized("staff/delete" , user['id']) :
        deletable = True
    else :
        deletable = False
        
    if Authorized("staff/create" , user['id']) :
        create = True
    else :
        create = False
        
    #  controllers and used for all grids in the app
    grid_param = dict(
        rows_per_page=5,
        include_action_button_text=True,
        search_button_text="Filter",
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma)
                               
    search_queries = [
        [T('By Name'), lambda value: db.staff.name.contains(value)],
        [T('By Email'), lambda value: db.staff.email.contains(value)],
        [T('By Telephon'), lambda value: db.staff.telephon.contains(value)],
        [T('By Address'), lambda value: db.staff.address.contains(value)|(db.staff.address == value)],
    ]

    query = db.staff.id > 0
    orderby = [db.staff.name]
    columns = [field for field in db.staff if field.readable]
    #columns.insert(0, Column("Custom", lambda row: A("click me")))
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                orderby=orderby,
                show_id=True,
                deletable=deletable,
                editable=editable,
                create=create,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)
    
        
    return dict(grid=grid, T=T , language=language.language)
