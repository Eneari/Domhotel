from .common import db

import datetime


def Authorized(app=None , userid=None):
    
    
    try:
        #print(app)
        #print(userid)
        role = db(db.user_roles.user_id==userid).select(db.user_roles.profile_id).first()
        #print(role.profile_id)
        level= db(db.user_profiles.id==role.profile_id).select(db.user_profiles.level).first()
        #print(level.level)
        
        min_level = db(db.app_level.path==app).select(db.app_level.min_level).first()
        
        #print(min_level.min_level)
        
        if level.level < min_level.min_level :
            return False
        else:
            return True
    except:
        #print("EXCEPT")
        return False

def UpdateStatus():
    
    import pytz
    date_now  = datetime.datetime.now(pytz.timezone('Africa/Abidjan'))
   
   
    lista = db((db.reservation.check_out < date_now) & (db.reservation.completed == False )).select(
                db.reservation.id,db.reservation.room,db.reservation.formula,db.reservation.check_in,
                db.reservation.check_out,)
    #print("------lista-----")
    #print(lista)
    
    for elm in lista :
        #  next status
        next_status = db((db.formula.id == elm.formula)).select(db.formula.next_status).first()
        db(db.rooms.id == elm.room).update(status=next_status.next_status)
        db(db.reservation.id == elm.id).update(completed=True)
        
        maintenance = db((db.status.id == next_status.next_status)).select(db.status.maintenance).first()
        if maintenance.maintenance :
            db.maintenance.insert(reservation=db.reservation.id,room=elm.room,check_in=elm.check_in,
            check_out=elm.check_out,status=next_status.next_status)

