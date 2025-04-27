# app/routes/api.py
from flask import Blueprint, request, jsonify
from app.models.vacation import Vacation  # Sie müssen Ihr Vacation-Modell erstellen oder importieren
from app import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/vacations', methods=['GET'])
def get_vacations():
    """API-Endpunkt zum Abrufen aller Urlaubseinträge"""
    try:
        vacations = Vacation.query.all()
        return jsonify([{
            'id': vacation.id,
            'name': vacation.name,
            'start': vacation.start_date.strftime('%Y-%m-%d'),
            'end': vacation.end_date.strftime('%Y-%m-%d'),
            'type': vacation.type
        } for vacation in vacations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/vacations', methods=['POST'])
def create_vacation():
    """API-Endpunkt zum Erstellen eines neuen Urlaubseintrags"""
    try:
        data = request.json
        
        # Überprüfen der erforderlichen Daten
        if not all(key in data for key in ['name', 'start_date', 'end_date']):
            return jsonify({'error': 'Fehlende Daten'}), 400
        
        # Datumsformatierung
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
        # Neuen Urlaubseintrag erstellen
        vacation = Vacation(
            name=data['name'],
            start_date=start_date,
            end_date=end_date,
            type=data.get('type', 'Urlaub')  # Standard ist 'Urlaub', wenn kein Typ angegeben
        )
        
        # In die Datenbank speichern
        db.session.add(vacation)
        db.session.commit()
        
        return jsonify({
            'id': vacation.id,
            'name': vacation.name,
            'start': vacation.start_date.strftime('%Y-%m-%d'),
            'end': vacation.end_date.strftime('%Y-%m-%d'),
            'type': vacation.type
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/vacations/<int:vacation_id>', methods=['DELETE'])
def delete_vacation(vacation_id):
    """API-Endpunkt zum Löschen eines Urlaubseintrags"""
    try:
        vacation = Vacation.query.get(vacation_id)
        
        if not vacation:
            return jsonify({'error': 'Urlaub nicht gefunden'}), 404
        
        db.session.delete(vacation)
        db.session.commit()
        
        return jsonify({'message': 'Urlaub erfolgreich gelöscht'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500