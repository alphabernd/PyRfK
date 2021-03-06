from flask import Blueprint, Flask, session, g, render_template, flash, redirect, url_for, request, jsonify, abort


import rfk
from rfk.helper import now
import rfk.database
from rfk.database.base import User, ApiKey
from rfk.database.show import Show, UserShow

from datetime import datetime, timedelta

user = Blueprint('user',__name__)
import apikey

@user.route('/<user>')
def info(user):
    user = User.get_user(username=user)
    
    upcoming_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.begin >= now()).order_by(Show.begin.asc()).limit(5).all()
    last_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.end <= now()).order_by(Show.end.desc()).limit(5).all()
    if user:
        return render_template('user/info.html',
                               username=user.username,
                               st=user.get_total_streamtime(),
                               shows={'upcoming': upcoming_shows , 'last': last_shows})
    else:
        abort(404)
