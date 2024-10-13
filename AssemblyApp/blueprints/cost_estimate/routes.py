from flask import render_template, request, redirect, url_for, flash, jsonify, render_template_string
from models.cost_estimate import Material, TradeModel, TaskModel, LabourConstantModel
from . import cost_estimate_bp
from flask_wtf import FlaskForm, csrf
from wtforms import StringField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class MaterialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    rate = FloatField('Rate', validators=[DataRequired(), NumberRange(min=0)])
    uom = StringField('Unit of Measure', validators=[DataRequired()])
    submit = SubmitField('Add Material')

class TradeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    rate = FloatField('Rate', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Trade')

class TaskForm(FlaskForm):
    trade_id = SelectField('Trade', validators=[DataRequired()], coerce=str)
    material_id = SelectField('Material', validators=[DataRequired()], coerce=str)
    description = StringField('Description', validators=[DataRequired()])
    labour_constant = FloatField('Labour Constant', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Task')

class LabourConstantForm(FlaskForm):
    trade = SelectField('Trade', validators=[DataRequired()], coerce=str)
    item = StringField('Item', validators=[DataRequired()])
    constant = FloatField('Constant', validators=[DataRequired(), NumberRange(min=0)])
    uom = SelectField('Unit of Measure', validators=[DataRequired()], choices=[
        ('hr/unit', 'hr/unit'),
        ('hr/m', 'hr/m'),
        ('hr/m2', 'hr/m2'),
        ('hr/m3', 'hr/m3')
    ])
    submit = SubmitField('Add Labour Constant')

@cost_estimate_bp.route('/materials', methods=['GET'])
def materials():
    materials = Material.get_all()
    form = MaterialForm()
    return render_template('cost_estimate/materials.html', materials=materials, form=form)

from flask import current_app
import traceback

@cost_estimate_bp.route('/materials/add', methods=['POST'])
def add_material():
    form = MaterialForm()
    current_app.logger.info(f"Form data received: {request.form}")
    if form.validate_on_submit():
        try:
            data = {
                'name': form.name.data,
                'description': form.description.data,
                'rate': form.rate.data,
                'uom': form.uom.data
            }
            new_material = Material.create(data)
            html = render_template_string("""
                <tr>
                    <td>{{ material.name }}</td>
                    <td>{{ material.description }}</td>
                    <td>{{ material.rate }}</td>
                    <td>{{ material.uom }}</td>
                    <td>
                        <button class="edit-button" data-id="{{ material._id }}">Edit</button>
                    </td>
                </tr>
            """, material=new_material)
            return jsonify({'success': True, 'html': html, 'csrf_token': form.csrf_token.current_token})
        except Exception as e:
            current_app.logger.error(f"Error creating material: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({'success': False, 'message': f'Error creating material: {str(e)}'})
    else:
        current_app.logger.error(f"Form validation failed. Errors: {form.errors}")
        return jsonify({'success': False, 'message': 'Invalid form data', 'errors': form.errors})

@cost_estimate_bp.route('/materials/edit/<string:material_id>', methods=['GET', 'POST'])
def edit_material(material_id):
    material = Material.get_by_id(material_id)
    form = MaterialForm(obj=material)
    if form.validate_on_submit():
        updated_data = {
            'name': form.name.data,
            'description': form.description.data,
            'rate': form.rate.data,
            'uom': form.uom.data
        }
        Material.update(material_id, updated_data)
        flash('Material updated successfully!')
        return redirect(url_for('cost_estimate.materials'))
    return render_template('cost_estimate/edit_material.html', form=form, material=material)

@cost_estimate_bp.route('/materials/delete/<string:material_id>', methods=['POST'])
def delete_material(material_id):
    Material.delete(material_id)
    flash('Material deleted successfully!')
    return redirect(url_for('cost_estimate.materials'))

@cost_estimate_bp.route('/trades', methods=['GET'])
def trades():
    trades = TradeModel.get_all()
    form = TradeForm()
    return render_template('cost_estimate/trades.html', trades=trades, form=form)

@cost_estimate_bp.route('/trades/add', methods=['POST'])
def add_trade():
    form = TradeForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'description': form.description.data,
            'rate': form.rate.data
        }
        new_trade = TradeModel.create(data)
        html = render_template_string("""
            <tr>
                <td>{{ trade.name }}</td>
                <td>{{ trade.description }}</td>
                <td>{{ trade.rate }}</td>
                <td>
                    <button class="edit-button" data-id="{{ trade._id }}">Edit</button>
                </td>
            </tr>
        """, trade=new_trade)
        return jsonify({'success': True, 'html': html, 'csrf_token': form.csrf_token.current_token})
    return jsonify({'success': False, 'message': 'Invalid form data'})

@cost_estimate_bp.route('/trades/edit/<string:trade_id>', methods=['GET', 'POST'])
def edit_trade(trade_id):
    trade = TradeModel.get_by_id(trade_id)
    form = TradeForm(obj=trade)
    if form.validate_on_submit():
        updated_data = {
            'name': form.name.data,
            'description': form.description.data,
            'rate': form.rate.data
        }
        TradeModel.update(trade_id, updated_data)
        flash('Trade updated successfully!')
        return redirect(url_for('cost_estimate.trades'))
    return render_template('cost_estimate/edit_trade.html', form=form, trade=trade)

@cost_estimate_bp.route('/trades/delete/<string:trade_id>', methods=['POST'])
def delete_trade(trade_id):
    TradeModel.delete(trade_id)
    flash('Trade deleted successfully!')
    return redirect(url_for('cost_estimate.trades'))

@cost_estimate_bp.route('/tasks', methods=['GET'])
def tasks():
    tasks = TaskModel.get_all()
    trades = {str(trade['_id']): trade['name'] for trade in TradeModel.get_all()}
    materials = {str(material['_id']): material['name'] for material in Material.get_all()}
    
    for task in tasks:
        task['trade_name'] = trades.get(str(task['trade_id']), 'Unknown Trade')
        task['material_name'] = materials.get(str(task['material_id']), 'Unknown Material')
    
    form = TaskForm()
    form.trade_id.choices = [(id, name) for id, name in trades.items()]
    form.material_id.choices = [(id, name) for id, name in materials.items()]
    
    return render_template('cost_estimate/tasks.html', tasks=tasks, form=form, csrf_token=csrf.generate_csrf())

@cost_estimate_bp.route('/tasks/add', methods=['POST'])
def add_task():
    form = TaskForm()
    trades = TradeModel.get_all()
    materials = Material.get_all()
    form.trade_id.choices = [(str(trade['_id']), trade['name']) for trade in trades]
    form.material_id.choices = [(str(material['_id']), material['name']) for material in materials]
    if form.validate_on_submit():
        try:
            data = {
                'trade_id': form.trade_id.data,
                'material_id': form.material_id.data,
                'description': form.description.data,
                'labour_constant': form.labour_constant.data
            }
            new_task = TaskModel.create(data)
            # Fetch the newly created task from the database
            created_task = TaskModel.get_by_id(new_task.inserted_id)
            trade_name = next((trade['name'] for trade in trades if str(trade['_id']) == created_task['trade_id']), '')
            material_name = next((material['name'] for material in materials if str(material['_id']) == created_task['material_id']), '')
            html = render_template_string("""
                <tr data-task-id="{{ task['_id'] }}">
                    <td>{{ trade_name }}</td>
                    <td>{{ material_name }}</td>
                    <td>{{ task['description'] }}</td>
                    <td>{{ task['labour_constant'] }}</td>
                    <td>
                        <button class="edit-button" data-id="{{ task['_id'] }}">Edit</button>
                    </td>
                </tr>
            """, task=created_task, trade_name=trade_name, material_name=material_name)
            return jsonify({'success': True, 'html': html, 'csrf_token': form.csrf_token.current_token})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error creating task: {str(e)}'})
    return jsonify({'success': False, 'message': 'Invalid form data', 'errors': form.errors})

@cost_estimate_bp.route('/tasks/edit/<string:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = TaskModel.get_by_id(task_id)
    form = TaskForm(obj=task)
    trades = TradeModel.get_all()
    materials = Material.get_all()
    form.trade_id.choices = [(str(trade['_id']), trade['name']) for trade in trades]
    form.material_id.choices = [(str(material['_id']), material['name']) for material in materials]

    if request.method == 'POST':
        if form.validate_on_submit():
            updated_data = {
                'trade_id': form.trade_id.data,
                'material_id': form.material_id.data,
                'description': form.description.data,
                'labour_constant': form.labour_constant.data
            }
            TaskModel.update(task_id, updated_data)
            
            # Fetch the updated task
            updated_task = TaskModel.get_by_id(task_id)
            trade_name = next((trade['name'] for trade in trades if str(trade['_id']) == updated_task['trade_id']), '')
            material_name = next((material['name'] for material in materials if str(material['_id']) == updated_task['material_id']), '')
            
            html = render_template_string("""
                <tr data-task-id="{{ task['_id'] }}">
                    <td>{{ trade_name }}</td>
                    <td>{{ material_name }}</td>
                    <td>{{ task['description'] }}</td>
                    <td>{{ task['labour_constant'] }}</td>
                    <td>
                        <button class="edit-button" data-id="{{ task['_id'] }}">Edit</button>
                    </td>
                </tr>
            """, task=updated_task, trade_name=trade_name, material_name=material_name)
            
            return jsonify({'success': True, 'html': html})
        else:
            return jsonify({'success': False, 'message': 'Invalid form data', 'errors': form.errors})

    return render_template('cost_estimate/edit_task.html', form=form, task=task)

@cost_estimate_bp.route('/tasks/delete/<string:task_id>', methods=['POST'])
def delete_task(task_id):
    TaskModel.delete(task_id)
    flash('Task deleted successfully!')
    return redirect(url_for('cost_estimate.tasks'))

from flask import current_app, render_template_string

@cost_estimate_bp.route('/labour_constants', methods=['GET'])
def labour_constants():
    try:
        current_app.logger.info("Entering labour_constants route")
        
        labour_constants = LabourConstantModel.get_all()
        current_app.logger.info(f"Retrieved {len(labour_constants)} labour constants")
        
        trades = TradeModel.get_all()
        current_app.logger.info(f"Retrieved {len(trades)} trades")
        
        form = LabourConstantForm()
        form.trade.choices = [(str(trade['_id']), trade['name']) for trade in trades]
        
        trade_names = {str(trade['_id']): trade['name'] for trade in trades}
        
        for lc in labour_constants:
            lc['trade_name'] = trade_names.get(str(lc['trade']), 'Unknown Trade')
        
        current_app.logger.info("Rendering template")
        rendered_template = render_template('cost_estimate/labour_constants.html', 
                               labour_constants=labour_constants, 
                               form=form, 
                               trade_names=trade_names)
        
        current_app.logger.info("Template rendered successfully")
        
        if not rendered_template.strip():
            current_app.logger.error("Rendered template is empty")
            return "The rendered template is empty. Check your template file.", 500
        
        return rendered_template
    
    except Exception as e:
        current_app.logger.error(f"Error in labour_constants route: {str(e)}")
        return render_template_string("""
            <h1>An error occurred</h1>
            <p>{{ error }}</p>
            <h2>Debug Information:</h2>
            <p>Number of labour constants: {{ lc_count }}</p>
            <p>Number of trades: {{ trade_count }}</p>
        """, error=str(e), lc_count=len(labour_constants) if 'labour_constants' in locals() else 'N/A', 
           trade_count=len(trades) if 'trades' in locals() else 'N/A'), 500

@cost_estimate_bp.route('/labour_constants/add', methods=['POST'])
def add_labour_constant():
    form = LabourConstantForm()
    trades = TradeModel.get_all()
    form.trade_id.choices = [(str(trade['_id']), trade['name']) for trade in trades]
    if form.validate_on_submit():
        try:
            data = {
                'trade_id': form.trade_id.data,
                'item': form.item.data,
                'constant': form.constant.data,
                'uom': form.uom.data
            }
            new_labour_constant = LabourConstantModel.create(data)
            created_labour_constant = LabourConstantModel.get_by_id(new_labour_constant.inserted_id)
            trade_name = next((trade['name'] for trade in trades if str(trade['_id']) == created_labour_constant['trade_id']), '')
            html = render_template_string("""
                <tr data-labour-constant-id="{{ labour_constant['_id'] }}">
                    <td>{{ trade_name }}</td>
                    <td>{{ labour_constant['item'] }}</td>
                    <td>{{ labour_constant['constant'] }}</td>
                    <td>{{ labour_constant['uom'] }}</td>
                    <td>
                        <button class="edit-button" data-id="{{ labour_constant['_id'] }}">Edit</button>
                    </td>
                </tr>
            """, labour_constant=created_labour_constant, trade_name=trade_name)
            return jsonify({'success': True, 'html': html, 'csrf_token': form.csrf_token.current_token})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error creating labour constant: {str(e)}'})
    return jsonify({'success': False, 'message': 'Invalid form data', 'errors': form.errors})

@cost_estimate_bp.route('/labour_constants/edit/<string:labour_constant_id>', methods=['GET', 'POST'])
def edit_labour_constant(labour_constant_id):
    labour_constant = LabourConstantModel.get_by_id(labour_constant_id)
    form = LabourConstantForm(obj=labour_constant)
    trades = TradeModel.get_all()
    form.trade_id.choices = [(str(trade['_id']), trade['name']) for trade in trades]

    if request.method == 'POST':
        if form.validate_on_submit():
            updated_data = {
                'trade_id': form.trade_id.data,
                'item': form.item.data,
                'constant': form.constant.data,
                'uom': form.uom.data
            }
            LabourConstantModel.update(labour_constant_id, updated_data)
            
            updated_labour_constant = LabourConstantModel.get_by_id(labour_constant_id)
            trade_name = next((trade['name'] for trade in trades if str(trade['_id']) == updated_labour_constant['trade_id']), '')
            
            html = render_template_string("""
                <tr data-labour-constant-id="{{ labour_constant['_id'] }}">
                    <td>{{ trade_name }}</td>
                    <td>{{ labour_constant['item'] }}</td>
                    <td>{{ labour_constant['constant'] }}</td>
                    <td>{{ labour_constant['uom'] }}</td>
                    <td>
                        <button class="edit-button" data-id="{{ labour_constant['_id'] }}">Edit</button>
                    </td>
                </tr>
            """, labour_constant=updated_labour_constant, trade_name=trade_name)
            
            return jsonify({'success': True, 'html': html})
        else:
            return jsonify({'success': False, 'message': 'Invalid form data', 'errors': form.errors})

    return render_template('cost_estimate/edit_labour_constant.html', form=form, labour_constant=labour_constant)

@cost_estimate_bp.route('/labour_constants/delete/<string:labour_constant_id>', methods=['POST'])
def delete_labour_constant(labour_constant_id):
    LabourConstantModel.delete(labour_constant_id)
    flash('Labour Constant deleted successfully!')
    return redirect(url_for('cost_estimate.labour_constants'))