from flask import render_template, request, redirect, url_for, flash, jsonify, render_template_string
from models.cost_estimate import Material
from . import cost_estimate_bp
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class MaterialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    rate = FloatField('Rate', validators=[DataRequired(), NumberRange(min=0)])
    uom = StringField('Unit of Measure', validators=[DataRequired()])
    submit = SubmitField('Add Material')

@cost_estimate_bp.route('/materials', methods=['GET'])
def materials():
    materials = Material.get_all()
    form = MaterialForm()
    return render_template('cost_estimate/materials.html', materials=materials, form=form)

@cost_estimate_bp.route('/materials/add', methods=['POST'])
def add_material():
    form = MaterialForm()
    if form.validate_on_submit():
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
                    <a href="{{ url_for('cost_estimate.edit_material', material_id=material._id) }}" class="edit-button">Edit</a> |
                    <form action="{{ url_for('cost_estimate.delete_material', material_id=material._id) }}" method="POST" style="display:inline;" onsubmit="return confirm('Are you sure you want to delete this material?');">
                        <button type="submit" class="delete-button">Delete</button>
                    </form>
                </td>
            </tr>
        """, material=new_material)
        return jsonify({'success': True, 'html': html, 'csrf_token': form.csrf_token.current_token})
    return jsonify({'success': False, 'message': 'Invalid form data'})

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
