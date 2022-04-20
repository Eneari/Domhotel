
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, SPAN
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from pydal.validators import IS_NOT_EMPTY, IS_INT_IN_RANGE, IS_IN_SET, IS_IN_DB, IS_NOT_IN_DB, IS_EXPR



import os
from py4web import action, Field, DAL
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma,TextareaWidget
from yatl.helpers import A
from py4web.utils.grid import Column
from .utils import Authorized


from py4web import Flash

flash = Flash()
@action("rooms/unauthorized")
@action.uses(flash, "rooms/unauthorized.html")
def unhautorized():
    return dict()



# exposed as /examples/html_grid
@action("rooms/category")
@action("rooms/category/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/category.html")
def category_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/category" , user['id']) :
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
      #  [T('By Amount'), lambda value: db.payrolls.amount == (value)],
        [T('By Name')  , lambda value: db.staff.name.contains(value)],
    ]
    
    query = db.rooms_category.id > 0
    orderby = [db.rooms_category.id]
    #columns = [field for field in db.payrolls if field.readable]
   
    
    columns = [
        db.rooms_category.category,
       # db.rooms_category.price,
       # db.rooms_category.currency,
        db.rooms_category.maintenance_time,
        db.rooms_category.placers,
    ]
    
    #columns.insert(0, Column("Custom", lambda row: A("click me")))
    
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=[],
                field_id=db.rooms_category.id,
   #             left=[
   #         db.months.on(db.months.id == db.payrolls.month_id),
   #         db.staff.on(db.staff.id == db.payrolls.id),
   #     ],
                orderby=orderby,
                headings = [ T("Category"), T("Mant. Time (min)"), T("Placers")],
                show_id=False,
                T=T,
                **grid_param)
                
    grid.param.new_action_button_text = T("New")
    grid.param.new_submit_value = T("Submit")
    grid.param.details_action_button_text = T("Details")
    grid.param.details_submit_value = T("Return")
    grid.param.edit_action_button_text  = T("Edit")
    grid.delete_action_button_text = T("Delete")
    

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T)


# exposed as /examples/html_grid
@action("rooms/rooms")
@action("rooms/rooms/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/rooms.html")
def rooms_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/rooms" , user['id']) :
        redirect(URL('unauthorized'))
        
    # update room reservation status
    from .utils import UpdateStatus
    UpdateStatus()
    
        
    if (path == None or  'edit' in path or 'new' in path or 'delete' in path) :

        
        #db.rooms.status.requires=IS_IN_DB(db(db.status.sel_rooms == True), 'status.id', '%(status)s')
        db.rooms.status.writable = False

        
        #  controllers and used for all grids in the app
        grid_param = dict(
            rows_per_page=5,
            include_action_button_text=True,
            search_button_text="Filter",
            formstyle=FormStyleBulma,
            grid_class_style=GridClassStyleBulma,
    )
            
                                   
        search_queries = [
            [T('By Number')  , lambda value: db.rooms.number.contains(value)],
            [T('By Status'), lambda value: db.rooms_status.status.contains(value)],
            [T('By Category'), lambda value: db.rooms_category.category.contains(value)],

        ]
        
        query = db.rooms.id > 0
        orderby = [db.rooms.number]
        #columns = [field for field in db.payrolls if field.readable]
       
        
        columns = [
            db.rooms.number,
            db.rooms.description,
            db.rooms_category.category,
            db.status.status,
            
        ]
        
        #columns.insert(0, Column("Custom", lambda row: A("click me")))
        
        grid = Grid(path,
                    query,
                    columns=columns,
                    search_queries=search_queries,
                    field_id=db.rooms.id,
                   left=[
                    db.rooms_category.on(db.rooms_category.id == db.rooms.category),
                    db.status.on(db.status.id == db.rooms.status),
                    ],
                    orderby=orderby,
                    headings = [ T("Number"), T("Description"), T("Category"), T("Status")],
                    show_id=False,
                    T=T,
                    **grid_param)
                    

        grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

        return dict(grid=grid, T=T )
    
    elif ( 'details' in path):
        
        lista = path.split("/")
        
        id = lista[len(lista)-1]
        
        redirect(URL("rooms/rooms_detail/"+id))

# exposed as /examples/html_grid
@action("rooms/rooms_detail")
@action("rooms/rooms_detail/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/rooms_detail.html")
def rooms_details(path=None):
    
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/rooms_detail" , user['id']) :
        redirect(URL('unauthorized'))
        
    room = db((db.rooms.id == path) & (  db.rooms.category == db.rooms_category.id  ) &
            (db.rooms.status == db.status.id)
        ).select(db.rooms.number,db.rooms.description,db.rooms_category.category, db.status.status).first()
    
    return dict( T=T , room=room)


# exposed as /examples/html_grid
@action("rooms/status")
@action("rooms/status/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/status.html")
def status_grid(path=None):
    
    print(path)
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/status" , user['id']) :
        redirect(URL('unauthorized'))
        
    # update room reservation status
    from .utils import UpdateStatus
    UpdateStatus()
        


    if (path == None ) :

        #  controllers and used for all grids in the app
        grid_param = dict(
            rows_per_page=5,
            include_action_button_text=True,
            search_button_text="Filter",
            formstyle=FormStyleBulma,
            grid_class_style=GridClassStyleBulma,
    )
            
                                   
        search_queries = [
            [T('By Number')  , lambda value: db.rooms.number.contains(value)],
            [T('By Description')  , lambda value: db.rooms.description.contains(value)],
            [T('By Category')  , lambda value: db.rooms_category.category.contains(value)],
            [T('By Status'), lambda value: db.status.status.contains(value)],
        ]
        
        query = db.rooms.id > 0
        orderby = [db.rooms.number]
        #columns = [field for field in db.payrolls if field.readable]
        db.rooms.status.writable = False

        
        columns = [
            db.rooms.number,
            db.rooms.description,
            db.rooms_category.category,
            db.status.status,
        ]
            
        grid = Grid(path,
                    query,
                    columns=columns,
                    search_queries=search_queries,
                    field_id=db.rooms.id,
                    left=[
                    db.status.on(db.rooms.status == db.status.id),
                    db.rooms_category.on(db.rooms.category == db.rooms_category.id),
                    ],
                    orderby=orderby,
                    headings = [ T("Room"), T("Description") ,T("Category") ,T("Status")],
                    show_id=False,
                    create=False,
                    deletable=False,
                    T=T,
                    **grid_param)
                    

        grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

        return dict(grid=grid, T=T )
    
    elif ( 'details' in path):
        
        lista = path.split("/")
        
        id = lista[len(lista)-1]
        
        redirect(URL("rooms/status_details/"+id))
    
    elif ( 'edit' in path):
        
        lista = path.split("/")
        
        id = lista[len(lista)-1]
        
        redirect(URL("rooms/status_edit/"+id))

# exposed as /examples/html_grid
@action("rooms/status_details")
@action("rooms/status_details/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/status_details.html")
def status_details(path=None):
    
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/status_details" , user['id']) :
        redirect(URL('unauthorized'))
        
    room = db((db.rooms.id == path) & (  db.rooms.category == db.rooms_category.id  ) &
            (db.rooms.status == db.status.id)
        ).select(db.rooms.number,db.rooms.description,db.rooms_category.category, db.status.status).first()
    
    return dict( T=T , room=room)

# exposed as /examples/html_grid
@action("rooms/status_edit")
@action("rooms/status_edit/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/status_edit.html")
def status_edit(path=None):
    
    print("status_edit")
    
    print(path)
    room = db((db.rooms.id == path) & (  db.rooms.category == db.rooms_category.id  ) &
            (db.rooms.status == db.status.id)
        ).select(db.rooms.number,db.rooms.description,db.rooms_category.category, db.status.status).first()
       
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/status_edit" , user['id']) :
        redirect(URL('unauthorized'))
   
    db.rooms.id.readable = False
    db.rooms.id.writable = False

    db.rooms.number.readable = False
    db.rooms.number.writable = False
    
    db.rooms.description.readable = False
    db.rooms.description.writable = False

    db.rooms.category.writable = False
    db.rooms.category.readable = False
    
    db.rooms.status.readable = True
    db.rooms.status.writable = False

    
    #db.rooms.category.requires=IS_IN_DB(db, 'rooms_category.id', '%(category)s') 

    form = Form(db.rooms, path, deletable=False, formstyle=FormStyleBulma)
    
    if form.accepted:
        # Do something with form.vars['product_name'] and form.vars['product_quantity']
        redirect(URL('rooms/status'))


    return dict( room=room, form=form , T=T )

    

# exposed as /examples/html_grid
@action("rooms/formula")
@action("rooms/formula/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/formula.html")
def formula_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/formula" , user['id']) :
        redirect(URL('unauthorized'))
        
    if (path == None or  'edit' in path or 'new' in path or 'delete' in path) :
        #  controllers and used for all grids in the app
        grid_param = dict(
            rows_per_page=10,
            include_action_button_text=True,
            search_button_text="Filter",
            formstyle=FormStyleBulma,
            grid_class_style=GridClassStyleBulma,
        )
            
                                   
        search_queries = [
            [T('By Name')  , lambda value: db.formula.name.contains(value)],
            [T('By Category')  , lambda value: db.rooms_category.category.contains(value)],
            [T('By Duration')  , lambda value: db.formula.duration.contains(value)],
            [T('By Tariff'), lambda value: db.formula.tariff == (value)],
        ]
        
        query = db.formula.id > 0
        orderby = [db.formula.name|db.formula.category]
        #columns = [field for field in db.payrolls if field.readable]
        db.formula.next_status.requires=IS_IN_DB(db(db.status.sel_formula == True), 'status.id', '%(status)s')
        
        columns = [
            db.formula.name,
            db.rooms_category.category,
            db.formula.duration,
            db.time.time,
            db.formula.tariff,
            db.status.status,
            #db.formula.currency,
        ]
        
        #columns.insert(0, Column("Custom", lambda row: A("click me")))
        
        grid = Grid(path,
                    query,
                    columns=columns,
                    search_queries=search_queries,
                    orderby=orderby,
                    field_id=db.formula.id,
                    left=[
                    db.rooms_category.on(db.rooms_category.id == db.formula.category),
                    db.time.on(db.time.id == db.formula.time),
                    db.status.on(db.status.id == db.formula.next_status ),
                    ],
                    headings = [ T("Name"), T("Category"), T("Duration") , T('Time'), T("Tariff"),T("Next Status")],
                    show_id=False,
                    T=T,
                    **grid_param)
                    

        grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

        return dict(grid=grid, T=T )
    
    
    elif ( 'details' in path):
        
        lista = path.split("/")
        
        id = lista[len(lista)-1]
        
        redirect(URL("rooms/formula_details/"+id))
    
    
# exposed as /examples/html_grid
@action("rooms/formula_details")
@action("rooms/formula_details/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "rooms/formula_detail.html")
def formula_detail(path=None):
    
    
    user = auth.get_user() or redirect(URL('auth/login'))
    #language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #T.select(language.language)

    if not Authorized("rooms/status_details" , user['id']) :
        redirect(URL('unauthorized'))
        
    formula = db((db.formula.id == path) & (  db.formula.category == db.rooms_category.id  ) &
        (  db.formula.time == db.time.id  )).select(
        db.formula.name,db.rooms_category.category, db.formula.duration,
        db.formula.time,db.formula.time,db.formula.tariff,db.formula.plug,
        db.formula.plug_add_time,db.formula.ligth,db.formula.ligth_add_time,
        db.formula.ac,db.formula.ac_add_time,db.time.time).first()
    
    return dict( T=T , formula=formula )
        
