"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior

"""

#    profiles levels :
#
#   root    :   100
#   owner   :   30
#   manager :   20
#   employee    10
#
#
# --------------------------------


from py4web import action, request, abort, redirect
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated

from pydal.validators import IS_NOT_EMPTY, IS_INT_IN_RANGE, IS_IN_SET, IS_IN_DB, IS_NOT_IN_DB
from py4web import Flash




from .utils import Authorized

from .staff import *
from .payrolls import *
from .rooms import *
from .proto import *
from .reservation import *
from .maintenance import *
from .control import *



#authorized = Authorized()

#@unauthenticated("index", "index.html")
@action('index')
@action.uses(session, flash, auth, 'index.html')
def index():
    user = auth.get_user() or redirect(URL('auth/login'))
    
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()

    T.select(language.language)
    
    #flash.set("Hello World", _class="info", sanitize=True)
   
    return dict(T=T, language=language.language)
    
    
#@unauthenticated("index", "index.html")
@action('language',method=["POST", "GET"])
@action.uses(session, auth , 'language.html')
def language():
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)
    
    form = Form([
        Field('Language', label=T('Language'),requires=IS_IN_SET(["en","fr","it"])),
        ], formstyle=FormStyleBulma, keep_values=True)
    if form.accepted:
        # Do something with form.vars['product_name'] and form.vars['product_quantity']
        language = form.vars['Language']
       
        db.user_language.update_or_insert(db.user_language.user_id == user['id'],user_id=user['id'], language=language)        
        db.commit()
        
        T.select(language)
        
        redirect(URL('index'))
    if form.errors:
        # display message error
        redirect(URL('not_accepted'))
    return dict(form=form , T=T, language=language.language)

@action("accepted")
def accepted():
    return "form_example accepted"


@action("not_accepted")
def not_accepted():
    return "form_example NOT accepted"
    

# exposed as /examples/html_grid
@action("user")
@action("user/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T, "user.html")
def user_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)
    
    
    if not Authorized("user" , user['id']) :
        redirect(URL('unauthorized'))
        
        
    if ( path == None or "delete" in path or "detail" in path) :
    
        #  controllers and used for all grids in the app
        grid_param = dict(
            rows_per_page=5,
            include_action_button_text=True,
            search_button_text="Filter",
            formstyle=FormStyleBulma,
            grid_class_style=GridClassStyleBulma)
                               
        search_queries = [
            [T('By UserName'), lambda value: db.auth_user.username.contains(value)],
            [T('By Name'), lambda value: db.auth_user.firstname(value)],
        #    ['By Telephon', lambda value: db.staff.telephon.contains(value)],
         #   ['By Address', lambda value: db.staff.address.contains(value)|(db.staff.address == value)],
        ]
        query = db.auth_user.id > 0
        orderby = [db.auth_user.username]
        columns = [field for field in db.auth_user if field.readable]
        #columns.insert(0, Column("Custom", lambda row: A("click me")))
        grid = Grid(path,
                    query,
                    columns=columns,
                    search_queries=search_queries,
                    orderby=orderby,
                    show_id=False,
                    T=T,
                    **grid_param)

        grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)
        
        return dict(grid=grid, T=T, language=language.language)

        
    elif ( path == "new" ) :
        
        redirect(URL('auth/register'))
        
    elif ( "edit" in path) :
            
        redirect(URL('auth/profile'))

    
# exposed as /examples/html_grid ---------------------------
@action("profile")
@action("profile/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T, "profile.html")
def profile_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("profile" , user['id']) :
        redirect(URL('unauthorized'))
        
    
    db.user_roles.profile_id.label=T("Profile" )
    db.user_roles.user_id.label=T("User" )

    db.user_roles.user_id.requires  =  [IS_NOT_IN_DB(db, 'user_roles.user_id', error_message='Utente già inserito '),
                                        IS_IN_DB(db, 'auth_user.id', '%(username)s', error_message='Utente inesistente o vuoto ')]
                                    

    db.user_roles.profile_id.requires  =  IS_IN_DB(db, 'user_profiles.id', '%(profile)s')
    
    columns = [
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.user_profiles.profile,
       
    ]
   
    #  controllers and used for all grids in the app
    grid_param = dict(
        rows_per_page=5,
        include_action_button_text=True,
        search_button_text=T("Filter"),
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma)
        
                               
    search_queries = [
        [T('By UserName'),   lambda value: db.auth_user.username.contains(value)],
        [T('By First Name'), lambda value: db.auth_user.first_name.contains(value)],
        [T('By Last Name'),  lambda value: db.auth_user.last_name.contains(value)],
        [T('By Profile'),    lambda value: db.user_profiles.profile.contains(value)],


        #['By Telephon', lambda value: db.staff.telephon.contains(value)],
        #['By Address', lambda value: db.staff.address.contains(value)|(db.staff.address == value)],
    ]

    query = db.user_roles.id > 0
    orderby = [db.user_roles.user_id]
    #columns = [field for field in db.auth_user_tag_default if field.readable]
    #columns.insert(0, Column("Custom", lambda row: A("click me")))
    columns=columns
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                 left=[
            db.auth_user.on(db.user_roles.user_id == db.auth_user.id),
            db.user_profiles.on(db.user_roles.profile_id == db.user_profiles.id),
        ],
                orderby=orderby,
                show_id=False,
                headings = [T("Username"),T("First Name"), T("Last Name"), T('Profile')],
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

    return dict(grid=grid, T=T, language=language.language)


@action("unauthorized")
@action.uses("unauthorized.html")
def unhautorized():
    return dict(T=T)

