from flask import render_template, abort
from . import main
from flask_login import login_required, current_user
from app import mongo

def project_access_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(project_number, *args, **kwargs):
        if project_number not in current_user.assigned_projects and not current_user.is_admin():
            abort(403)
        return f(project_number, *args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/projects')
@login_required
def projects():
    if current_user.is_admin():
        projects = mongo.db.projects.find()
    else:
        projects = mongo.db.projects.find({'project_number': {'$in': current_user.assigned_projects}})
    return render_template('projects.html', projects=projects)

@main.route('/projects/<project_number>')
@login_required
@project_access_required
def project_detail(project_number):
    project = mongo.db.projects.find_one({'project_number': project_number})
    if not project:
        abort(404)
    return render_template('project_detail.html', project=project)