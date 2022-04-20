
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, SPAN, BUTTON
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
@action("reservation/unauthorized")
@action.uses(flash, "reservation/unauthorized.html")
def unhautorized():
    return dict()



# exposed as /examples/html_grid
@action("reservation/reservation")
@action("reservation/reservation/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation.html")
def reservation_grid(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    #print(language.language)
    
    T.select(language.language)

    if not Authorized("reservation/reservation" , user['id']) :
        redirect(URL('unauthorized'))
        
    # update room reservation status
    from .utils import UpdateStatus
    UpdateStatus()
        
    post_action_buttons = [
        lambda row: GridActionButton(
            url=(URL("reservation/reservation_delete/"+str( row.reservation.id))),
            text= T("Cancel"),
            icon= "fa fa-trash" ,
            completed = row.reservation.completed
        ) 
    ]
        
    # show list -------------------
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
            [T('By Room')  , lambda value: db.rooms.number.contains(value)],
            [T('By Description') , lambda value: db.rooms.description.contains(value)],
            [T('By Formula'), lambda value: db.formula.name.contains(value)],
        ]
        
        query = db.reservation.id > 0
        orderby = [~db.reservation.check_out]
        #columns = [field for field in db.payrolls if field.readable]
        
       
        db.reservation.room.requires=IS_IN_DB(db, 'rooms.id', '%(number)s - %(description)s')
        db.reservation.formula.requires=IS_IN_DB(db, 'formula.id', '%(name)s - %(tariff)s - %(currency)s')
        db.reservation.completed.readable = False
        db.reservation.check_in.requires=IS_DATETIME(format='%d/%m/%Y %H:%M' )
        
        columns = [
            db.rooms.number,
            db.rooms.description,
            db.formula.name,
            db.formula.tariff,
            #db.formula.currency,
            db.reservation.total_nigth,
            db.reservation.total_amount,
            #Column("check_in", lambda row: datetime.datetime.strftime(row.reservation.check_in, "%d/%m/%Y %H:%M")),
            #datetime.datetime.strftime(db.reservation.check_in, "%d/%m/%Y %H:%M"),
            db.reservation.check_in,
            db.reservation.check_out,
            db.reservation.completed
        ]
        
        #columns.insert(0, Column("Custom", lambda row: A("click me")))
        
        grid = Grid(path,
                    query,
                    columns=columns,
                    search_queries=search_queries,
                    field_id=db.reservation.id,
                    left=[
                    db.rooms.on(db.rooms.id == db.reservation.room),
                    db.formula.on(db.formula.id == db.reservation.formula),
                    db.rooms_category.on(db.rooms_category.id == db.rooms.category),

                    ],
                    orderby=orderby,
                    #headings = [ T("Room"),T("Description"), T("Formula"), T("Price"), SPAN(_class='fa fa-coins '),T("Total"), T("Check In"), T("Check Out")],
                    headings = [ T("Room"),T("Description"), T("Formula"), T("Price"),T("Nigth"),T("Total"), T("Check In"), T("Check Out")],
                    show_id=False,
                    deletable=False,
                    editable=False,
                    post_action_buttons = post_action_buttons,
                    T=T,
                    **grid_param)

        grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)

        return dict(grid=grid, T=T , language=language.language)
    
    elif ( 'new' in path):
        
        redirect(URL("reservation/reservation_1"))
    elif ( 'delete' in path):
        lista = path.split("/")
        
        id = lista[len(lista)-1]
                
        redirect(URL("reservation/reservation_delete/"+id))
    elif ( 'detail' in path):
        lista = path.split("/")
        
        id = lista[len(lista)-1]
                
        redirect(URL("reservation/reservation_detail/"+id))
    


# exposed as /examples/html_grid
@action("reservation/reservation_1")
@action("reservation/reservation_1/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_1.html")
def reservation_1(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation" , user['id']) :
        redirect(URL('unauthorized'))
        
        
    pre_action_buttons = [
    lambda row: GridActionButton(
        url=(URL("reservation/reservation_2/"+str( row.rooms.id))),
        #url=(URL("reservation/reservation_2/")),

        text= T("Select"),
        icon= "fa fa-check-circle" 
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
    
    query = db.rooms.status == 1
    orderby = [db.rooms.id]    

    columns = [
        db.rooms.number,
        db.rooms.description,
        db.rooms_category.category
    ]
    
    #columns.insert(0, Column("Custom", lambda row: A("click me")))
    
    grid = Grid(path,
                query,
                columns=columns,
                search_queries=search_queries,
                field_id=db.rooms.id,
                left=[
                
                db.rooms_category.on(db.rooms_category.id == db.rooms.category),

                ],
                orderby=orderby,
                headings = [ T("Room"),T("Description"),T("Category") ],
                show_id=False,
                deletable=False,
                editable=False,
                create=False,
                details=False,
                pre_action_buttons = pre_action_buttons,
                T=T,
                **grid_param)

    grid.formatters['thing.color'] = lambda color: I(_class="fa fa-circle", _style="color:"+color)
   
    return dict(grid=grid, T=T , language=language.language)



# exposed as /examples/html_grid
@action("reservation/reservation_2")
@action("reservation/reservation_2/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_2.html")
def reservation_2(path=None):
    
      
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_delete" , user['id']) :
        redirect(URL('unauthorized'))
        
    lista = path.split("/")
        
    room_id = lista[len(lista)-1]
    
    room_category = db(db.rooms.id == room_id).select(db.rooms.category).first() 
    
    room = db((db.rooms.id == room_id) & (db.rooms.category == db.rooms_category.id) 
            ).select(db.rooms.number,db.rooms.description,db.rooms_category.category).first()
       
    
    form =  Form( [Field('Formula',"reference formula" ,requires=IS_IN_DB(db(db.formula.category == room_category.category), 'formula.id', '%(name)s - %(tariff)s CFA') )],
                 formstyle=FormStyleBulma)
    attrs = {
            "_onclick": "window.history.back(); return false;",
            "_class": "button is-default",
            }
    form.param.sidecar.append(BUTTON(T("Cancel"), **attrs))
    
    if form.accepted :
        redirect(URL("reservation/reservation_3/"+str(room_id)+"/"+str(form.vars['Formula']))),
    
    
    return dict(form=form , T=T, room=room)
    
@action("reservation/reservation_3")
@action("reservation/reservation_3/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_3.html")
def reservation_3(path=None):
    
      
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_delete" , user['id']) :
        redirect(URL('unauthorized'))
        
    lista = path.split("/")
        
    formula_id = lista[len(lista)-1]
    room_id = lista[len(lista)-2]
    
    room_category = db(db.rooms.id == room_id).select(db.rooms.category).first() 
  
    
    room = db((db.rooms.id == room_id) & (db.rooms.category == db.rooms_category.id) 
            ).select(db.rooms.number,db.rooms.description,db.rooms_category.category).first()
    
    room_number = room.rooms.number
    
    formula = db(db.formula.id == formula_id).select(db.formula.name, db.formula.tariff,
                db.formula.duration, db.formula.time,
                db.formula.plug, db.formula.plug_add_time,
                db.formula.ligth, db.formula.ligth_add_time,
                db.formula.ac, db.formula.ac_add_time).first()
    
    # ---------------------  definisco check in e out ----------------
    chk_in_time  = db(db.config.code == "check_in_time").select(db.config.value).first()
    chk_out_time = db(db.config.code == "check_out_time").select(db.config.value).first()
    
    import pytz
   
    date = datetime.datetime.now(pytz.timezone('Africa/Abidjan'))

    #date = datetime.datetime.utcnow()
    ora = date.hour
    
    # se la permanenza < di 24 ore check in = ora di sistema, check out = chech in + tempo previsto da formula
    # se la permanenza > di 24 ore chech in ore 12 o maggiore check out = chech in + tempo previsto tagliato alle 11
    
    #formula_time = db(db.formula.id==formula_id).select(db.formula.duration,db.formula.time).first()
    #print(formula.duration)
    
    moltiplica  = db(db.time.id==formula.time).select(db.time.multiplier).first()
    
    #print (moltiplica.multiplier)
    
    total_minuts = formula.duration * moltiplica.multiplier
    
    if total_minuts >= 1440  :
    
        if ora < int(chk_in_time.value) :
            check_in = date.replace(hour=int(chk_in_time.value),minute=0,second=0,microsecond=0)
        else :
            check_in = date.replace(second=0,microsecond=0)
            
        check_out = check_in + datetime.timedelta(minutes=total_minuts)
        check_out = check_out.replace(hour=int(chk_out_time.value),minute=0,second=0,microsecond=0)
        
    else :
        
        check_in = date.replace(second=0,microsecond=0)
        check_out = check_in + datetime.timedelta(minutes=total_minuts)
        check_out = check_out.replace(second=0,microsecond=0)
        
    
    
    # in caso di formula  >= 24 ore preimposto i possibili check out per permanenze prolungate
    if total_minuts >= 1440  :
        
        check_out_day = check_out.day
    
        chk_out_list = [check_out,check_out.replace(day=check_out_day+1),check_out.replace(day=check_out_day+2),check_out.replace(day=check_out_day+3)]
        
        chk_out_list = [datetime.datetime.strftime(check_out, "%d/%m/%Y %H:%M")]
        for counter  in range(1, 5):
            next_date = check_out.replace(day=check_out_day+counter)
            chk_out_list.append( datetime.datetime.strftime(next_date, "%d/%m/%Y %H:%M"))
            
    else :
        chk_out_list = [datetime.datetime.strftime(check_out, "%d/%m/%Y %H:%M")]

    #print(chk_out_list)

    check_in_s = datetime.datetime.strftime(check_in, "%d/%m/%Y %H:%M")
    check_out_s = datetime.datetime.strftime(check_out, "%d/%m/%Y %H:%M")
    
    form =  Form( [Field('check_out' ,requires=IS_IN_SET(chk_out_list) ,default=chk_out_list[0] , label = T("Check Out") ) ] ,
                 formstyle=FormStyleBulma) 
    attrs = {
            "_onclick": "window.history.back(); return false;",
            "_class": "button is-default",
            }
    form.param.sidecar.append(BUTTON(T("Cancel"), **attrs))
    
    if form.accepted :
        redirect(URL("reservation/reservation_4/"+str(room_id)+"-"+str(formula_id)+"-"+(check_in_s)+"-"+str(form.vars['check_out'])))
    
    
    return dict(form=form , T=T, room=room, formula=formula, check_in_s=check_in_s)
    
    
    
  
# exposed as /examples/html_grid
@action("reservation/reservation_4")
@action("reservation/reservation_4/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_4.html")
def reservation_4(path=None):
    
      
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_delete" , user['id']) :
        redirect(URL('unauthorized'))
        
    lista = path.split("-")
   
    
    room_id    = lista[0]
    formula_id = lista[1]
    check_in   = lista[2]
    check_out  = lista[3]
    
    room_category = db(db.rooms.id == room_id).select(db.rooms.category).first() 
  
    
    room = db((db.rooms.id == room_id) & (db.rooms.category == db.rooms_category.id) 
            ).select(db.rooms.number,db.rooms.description,db.rooms_category.category).first()
    
    room_number = room.rooms.number
    
    formula = db(db.formula.id == formula_id).select(db.formula.name, db.formula.tariff,
                db.formula.duration, db.formula.time,
                db.formula.plug, db.formula.plug_add_time,
                db.formula.ligth, db.formula.ligth_add_time,
                db.formula.ac, db.formula.ac_add_time).first()
    
    
    
    start = datetime.datetime.strptime(check_in,"%d/%m/%Y %H:%M")
    stop = datetime.datetime.strptime(check_out,"%d/%m/%Y %H:%M")
    
    moltiplica  = db(db.time.id==formula.time).select(db.time.multiplier).first()
    
    #print (moltiplica.multiplier)
    
    total_minuts = formula.duration * moltiplica.multiplier
    
    if total_minuts >= 1440  :
    
        import math
        print(check_in)
        print(check_out)
        print(start)
        print(stop)
        print( abs((stop-start).days ))
        print( abs((stop-start).total_seconds() ))
        total_nigth = math.ceil( (stop-start).total_seconds() / 86400)
        print( total_nigth)
        total_amount = total_nigth * formula.tariff
    else :
        
        total_nigth = 0
        total_amount =  formula.tariff

    print( total_nigth)
    print( total_amount)    
        
    #-  room control settings  --------------

    plug = '1' if formula.plug else '0'
    plug_start =  check_in if plug=="1" else None
    plug_stop  =  datetime.datetime.strftime(stop+datetime.timedelta(minutes=formula.plug_add_time),
                                                        "%d/%m/%Y %H:%M") if plug=="1" else None

    ligth = '1' if formula.ligth else '0'
    ligth_start =  check_in if ligth=="1" else None
    ligth_stop  =  datetime.datetime.strftime(stop+datetime.timedelta(minutes=formula.ligth_add_time),
                                                         "%d/%m/%Y %H:%M") if ligth=="1" else None
    
    ac = '1' if formula.ac else '0'
    ac_start =  check_in if ac=="1" else None
    ac_stop  =  datetime.datetime.strftime(stop+datetime.timedelta(minutes=formula.ac_add_time),
                                                      "%d/%m/%Y %H:%M") if ac=="1" else None
   
    
    controls = {'room':room.rooms.number, "plug":plug,"plug_start":plug_start,"plug_stop":plug_stop,
                "ligth":ligth,"ligth_start":ligth_start, "ligth_stop" : ligth_stop,
                "ac":ac,"ac_start":ac_start, "ac_stop" : ac_stop }
                
    #print(controls)
    
    import json
    
    
    # Serializing json  
    json_object = json.dumps(controls, indent = 0) 
    #print(json_object)


    #----------------------------------------
   
    
    form =  Form( [Field('conferma' , readable=False, writable=False)] ,
                 formstyle=FormStyleBulma,
                 readonly = False,
                 form_name="prova")
    attrs = {
            "_onclick": "window.history.back(); return false;",
            "_class": "button is-default",
            }
    form.param.sidecar.append(BUTTON(T("Cancel"), **attrs))
    form.structure.find('[type=submit]')[0]['_onclick'] = 'sendControl( ' +json_object+')'
    
    username = db(db.auth_user.id == user['id'] ).select(db.auth_user.first_name,db.auth_user.last_name).first()

    
    if form.accepted :
        print("accepted")
        
        db.reservation.insert(room=room_id, formula = formula_id, 
                    check_in=datetime.datetime.strptime(check_in,"%d/%m/%Y %H:%M"),
                    check_out=datetime.datetime.strptime(check_out,"%d/%m/%Y %H:%M"),
                    created_by=user['id'] ,total_amount = total_amount,
                    total_nigth = total_nigth)
        
        row = db(db.rooms.id==room_id).select().first()
        
        row.update_record(status=2)
        
        flash.set("Reservation correctly inserted", _class="info", sanitize=True)
        
        redirect(URL('reservation/reservation'))
        
    
    return dict(form=form , T=T, room=room, formula=formula, check_in=check_in, check_out=check_out,
                    controls=controls,total_nigth=total_nigth,total_amount=total_amount,username=username,)
     

#-----------------------------------------------------------------------------------------------
@action("reservation/reservation_new" , method=["POST", "GET"])
@action("reservation/reservation_new/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_new.html")
def reservation_new(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_delete" , user['id']) :
        redirect(URL('unauthorized'))
        
        
    
   
    db.rooms.id.readable = False
    db.rooms.id.writable = False

    db.rooms.number.readable = True
    db.rooms.number.writable = False
    
    db.rooms.description.readable = True
    db.rooms.description.writable = False

    db.rooms.category.readable = True
    db.rooms.category.writable = False

    
    db.rooms.status.readable = True
    
    db.reservation.last_update.readable = False
    db.reservation.last_update.writable = False

    
    
    db.reservation.room.requires=IS_IN_DB(db(db.rooms.status == 1), 'rooms.id', '%(number)s - %(description)s')
    db.reservation.formula.requires=IS_IN_DB(db, 'formula.id', '%(name)s - %(tariff)s - %(currency)s')
    #db.reservation.check_in.requires=IS_DATETIME(format=T('%d/%m/%Y %H:%M'),error_message='must be DD/MM/YYYY HH:MM !' ,null = '01/01/2002 10:10')
    #db.rooms.category.requires=IS_IN_DB(db, 'rooms_category.id', '%(category)s') 

    #form = Form(db.reservation, deletable=False, formstyle=FormStyleBulma)
    
    form =  Form( [Field('Room',requires=IS_IN_DB(db(db.rooms.status == 1), 'rooms.id', '%(number)s - %(description)s') ),
                 Field('Formula',requires=IS_IN_DB(db, 'formula.id', '%(name)s - %(tariff)s - %(currency)s') )] ,
                 formstyle=FormStyleBulma)
    attrs = {
            "_onclick": "window.history.back(); return false;",
            "_class": "button is-default",
            }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))
    
    if form.accepted:
        
        print(form.vars)
        date = datetime.datetime.utcnow()
        ora = date.hour
        
        # se la permanenza < di 24 ore check in = ora di sistema, check out = chech in + tempo previsto da formula
        # se la permanenza > di 24 ore chech in ore 12 o maggiore check out = chech in + tempo previsto tagliato alle 11
        
        formula_time = db(db.formula.id==form.vars['Formula']).select(db.formula.duration,db.formula.time).first()
        print(formula_time.duration)
        
        moltiplica  = db(db.time.id==formula_time.time).select(db.time.multiplier).first()
        
        print (moltiplica.multiplier)
        
        total_minuts = formula_time.duration * moltiplica.multiplier
        
        if total_minuts >= 1440  :
        
            if ora < 12 :
                check_in = date.replace(hour=12,minute=0,second=0,microsecond=0)
            else :
                check_in = date
                
            check_out = check_in + datetime.timedelta(minutes=total_minuts)
            check_out = check_out.replace(hour=11,minute=0,second=0,microsecond=0)
            
        else :
            
            check_in = date.replace(second=0,microsecond=0)
            check_out = check_in + datetime.timedelta(minutes=total_minuts)
            check_out = check_out.replace(second=0,microsecond=0)

            
        print(check_in)
        print(check_out)

       

        row = db(db.rooms.id==form.vars['Room']).select().first()
        
        #row.update_record(status=2)
        
        flash.set("Reservation correctly inserted", _class="info", sanitize=True)
        
        redirect(URL('reservation/reservation'))


    return dict( form=form , T=T ,  language=language.language)


@action("reservation/reservation_delete" , method=["POST", "GET"])
@action("reservation/reservation_delete/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_delete.html")
def reservation_delete(path=None):
    
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_delete" , user['id']) :
        redirect(URL('unauthorized'))
        
        
    room = db((db.reservation.id == path) & (  db.reservation.room == db.rooms.id  ) &
            (db.rooms.category == db.rooms_category.id) &
            (db.reservation.formula == db.formula.id)
        ).select(db.rooms.number,db.rooms.description,db.rooms_category.category, 
                db.formula.name, db.formula.tariff,db.reservation.check_in, db.reservation.check_out,
                db.reservation.last_update, db.reservation.created_by).first()
       
   
    username = db(db.auth_user.id == room.reservation.created_by).select(db.auth_user.first_name,db.auth_user.last_name).first()
    
    #----------   send controls
    controls = {'room':room.rooms.number,
                "plug":"0",
                "ligth":"0",
                "ac":"0" }
                
    #print(controls)
    
    import json
    
    
    # Serializing json  
    json_object = json.dumps(controls, indent = 0) 

   
    #form = Form(db.reservation, 
    #            record=path,
    #            readonly=True,
    #            deletable=False,
     #           formstyle=FormStyleBulma)
    
     
    form = Form([Field('delete','boolean',requires=IS_NOT_EMPTY())],
                keep_values=True,
                
                formstyle=FormStyleBulma)
    attrs = {
            "_onclick": "window.history.back(); return false;",
            "_class": "button is-default",
            }
    form.param.sidecar.append(BUTTON("Cancel", **attrs))
    
    
    form.validation=check_time_reserve(form,path)
    #form.structure.find('[type=submit]')[0]['_class'] = 'btn-primary'
    #form.structure.find('[type=submit]')[0]['_onclick'] = 'sendControl( ' +json_object+')'
    form.structure.find('[type=submit]')[0]['_onclick'] = 'delReserve( ' +room.rooms.number+')'
    #form.structure.find('[class=btn-primary]')[0]['_onclick'] = "return confirm('Confirm to delete ?;')"
    
    if form.accepted:
       
        # Do something with form.vars['product_name'] and form.vars['product_quantity']
        room_id = db(db.reservation.id==path).select(db.reservation.room).first()
        
        row = db(db.rooms.id==room_id.room).select().first()
        
        row.update_record(status=1)
        
        row = db(db.reservation.id==path).select().first()
        
        row.delete_record()
        
       
        flash.set("Reservation correctly deleted", _class="info", sanitize=True)
        
        redirect(URL('reservation/reservation'))


    return dict( room=room, form=form , T=T ,  language=language.language, username = username)

@action("reservation/reservation_checkout" , method=["POST", "GET"])
@action("reservation/reservation_checkout/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_checkout.html")
def reservation_checkout(path=None):
  
    
    room = db((db.reservation.id == path) & (  db.reservation.room == db.rooms.id  ) &
            (db.rooms.category == db.rooms_category.id) &
            (db.reservation.formula == db.formula.id)
        ).select(db.rooms.number,db.rooms.description,db.rooms_category.category, 
                db.formula.name, db.formula.tariff,db.reservation.check_in, db.reservation.check_out,
                db.reservation.last_update).first()
       
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_checkout" , user['id']) :
        redirect(URL('unauthorized'))
    
    

   
    #form = Form(db.reservation, 
    #            record=path,
     #           readonly=False,
    #            deletable=False,
    #            formstyle=FormStyleBulma)
                
    form = Form([Field('CheckOut','datetime', label='Check Out',
                requires=IS_DATETIME() )],
                keep_values=True,
                
                formstyle=FormStyleBulma)
    
    ##form.validation=check_time_reserve(form,path)
    #form.structure.find('[type=submit]')[0]['_class'] = 'btn-primary'
    #form.structure.find('[class=btn-primary]')[0]['_onclick'] = "return confirm('Confirm to delete ?;')"
    
    if form.accepted:
       
        # Do something with form.vars['product_name'] and form.vars['product_quantity']
        room_id = db(db.reservation.id==path).select(db.reservation.room).first()
        
        row = db(db.rooms.id==room_id.room).select().first()
        
        row.update_record(status=1)
        
        print(form.vars["CheckOut"] )
        
        data = form.vars["CheckOut"] 
        
        
        
        row = db(db.reservation.id==path).select().first()
        
        row.update_record(check_out = data )

        
       
        flash.set("Reservation correctly deleted", _class="info", sanitize=True)
        
        redirect(URL('reservation/reservation'))


    return dict( room=room, form=form , T=T ,  language=language.language)


@action("reservation/reservation_detail" , method=["POST", "GET"])
@action("reservation/reservation_detail/<path:path>", method=["POST", "GET"])
@action.uses(session, db, auth, T,flash, "reservation/reservation_detail.html")
def reservation_detail(path=None):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    language = db(db.user_language.user_id == user['id']).select(db.user_language.language).first()
    
    T.select(language.language)

    if not Authorized("reservation/reservation_detail" , user['id']) :
        redirect(URL('unauthorized'))
        
    #---   init  ------
    
    room = db((db.reservation.id == path) & (  db.reservation.room == db.rooms.id  ) &
            (db.rooms.category == db.rooms_category.id) &
            (db.reservation.formula == db.formula.id)
        ).select(db.rooms.number,db.rooms.description,db.rooms_category.category, 
                db.formula.name,db.formula.id, db.formula.tariff,db.reservation.check_in, db.reservation.check_out,
                db.reservation.last_update,db.reservation.created_by,db.reservation.total_nigth,
                db.reservation.total_amount).first()
                
    formula = db(db.formula.id == room.formula.id).select(
                db.formula.plug, db.formula.plug_add_time,
                db.formula.ligth, db.formula.ligth_add_time,
                db.formula.ac, db.formula.ac_add_time).first()
                    
    username = db(db.auth_user.id == room.reservation.created_by).select(db.auth_user.first_name,db.auth_user.last_name).first()
        
    #-  room control settings  --------------
    
    check_in = room.reservation.check_in
    check_out = room.reservation.check_out
    
    plug = formula.plug
    plug_start =  datetime.datetime.strftime(check_in,  "%d/%m/%Y %H:%M") if plug else None
    plug_stop  =  datetime.datetime.strftime(check_out+datetime.timedelta(minutes=formula.plug_add_time),
                                                        "%d/%m/%Y %H:%M") if plug else None
    
    ligth = formula.ligth
    ligth_start =  datetime.datetime.strftime(check_in,  "%d/%m/%Y %H:%M") if ligth else None
    ligth_stop  =  datetime.datetime.strftime(check_out+datetime.timedelta(minutes=formula.ligth_add_time),
                                                         "%d/%m/%Y %H:%M") if ligth else None
    
    ac = formula.ac
    ac_start =  datetime.datetime.strftime(check_in,  "%d/%m/%Y %H:%M") if ac else None
    ac_stop  =  datetime.datetime.strftime(check_out+datetime.timedelta(minutes=formula.ac_add_time),
                                                      "%d/%m/%Y %H:%M") if ac else None
    
    controls = {"plug":plug,"plug_start":plug_start,"plug_stop":plug_stop,
                "ligth":ligth,"ligth_start":ligth_start, "ligth_stop" : ligth_stop,
                "ac":ac,"ac_start":ac_start, "ac_stop" : ac_stop }
                
    #print(controls)

    return dict( room=room,  T=T ,  language=language.language, username=username, controls=controls)

#-----------------------------------------------------------------------------------------------------
def check_time_reserve(form,reserve_id):
    
    user = auth.get_user() or redirect(URL('auth/login'))
    user_id = user['id']
    
    role = db(db.user_roles.user_id==user_id).select(db.user_roles.profile_id).first()
    
    level= db(db.user_profiles.id==role.profile_id).select(db.user_profiles.level).first()
   
    row = db(db.reservation.id==reserve_id).select(db.reservation.last_update,db.reservation.completed).first()
    
    import pytz
   
    date = datetime.datetime.now(pytz.timezone('Africa/Abidjan'))
    
    print(date)
    print(row.last_update)
    
    d = row.last_update.replace(tzinfo=None)  # remove timezone info


    diff = date.replace(tzinfo=None) - d
    
    if row.completed :
        form.errors['delete'] = T('Reserve completed cannot be canceled')
        form.accepted = False
        
    
    if (( diff.seconds > 300) and (level.level <30)):
        print("delete reservation")
        print(diff.seconds)
        print(level.level)
    
        form.errors['delete'] = T('Only possible to delete from Admin User')
        form.accepted = False
            
    #row = db(db.reservation.id==path).select().first()

    #if not form.errors and form.vars['product_quantity'] % 2:
    #    form.errors['product_quantity'] = T('The product quantity must be even')


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
      ignore_attribute_plugin=False,
      completed=False
   ):
      self.url = url
      self.text = text
      self.icon = icon
      self.onclick = onclick
      self.additional_classes = additional_classes
      self.message = message
      self.append_id = append_id
      self.ignore_attribute_plugin = ignore_attribute_plugin
      self.completed = completed
      if self.completed :
          self.text = ""
          #self.icon = ""
          self.message="Reserve completed cannot be canceled"
          self.url=(URL("reservation/reservation"))
      
      
      
