
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, SPAN
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated


import os
from py4web import action, Field, DAL
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from py4web.utils.grid import Column
from .utils import Authorized


from py4web import Flash

flash = Flash()
@action("payrolls/unauthorized")
@action.uses(flash, "payrolls/unauthorized.html")
def unhautorized():
    return dict()



# exposed as /examples/html_grid
@action("payrolls/list")
@action("payrolls/list/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "payrolls/list.html")
def example_html_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("payrolls/list" , user['id']) :
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
        [T('By Code')  , lambda value: db.payrolls.code.contains(value)],
        [T('By Month') , lambda value: db.months.description.contains(value)],
        [T('By Amount'), lambda value: db.payrolls.amount == (value)],
        [T('By Name')  , lambda value: db.staff.name.contains(value)],
    ]
    
    query = db.payrolls.id > 0
    orderby = [db.payrolls.id]
    #columns = [field for field in db.payrolls if field.readable]
   
    
    columns = [
        db.payrolls.code,
        db.months.description,
        db.payrolls.amount,
        #db.payrolls.currency,
        db.staff.name,
        db.payrolls.generated,
    ]
    
    #columns.insert(0, Column("Custom", lambda row: A("click me")))
    
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                field_id=db.payrolls.id,
                left=[
            db.months.on(db.months.id == db.payrolls.month_id),
            db.staff.on(db.staff.id == db.payrolls.id),
        ],
                orderby=orderby,
                headings = [ T("Code"),T("Month"),T("Amount"), T("Name"), T("Generated At")],
                show_id=False,
                T=T,
                **grid_param)
                

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T , language=language.language)
