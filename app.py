#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-приложение для учета игроков в покер
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from poker_tracker import PokerTracker
from datetime import datetime
import json

app = Flask(__name__)
tracker = PokerTracker()


@app.route('/')
def index():
    """Главная страница"""
    players = tracker.get_all_players()
    players_data = []
    for player_id, name, created_at in players:
        balance = tracker.get_player_balance(player_id)
        players_data.append({
            'id': player_id,
            'name': name,
            'balance': balance,
            'created_at': created_at
        })
    sessions = tracker.get_all_game_sessions()
    sessions_data = []
    for session_id, game_date, description, created_at in sessions:
        sessions_data.append({
            'id': session_id,
            'game_date': game_date,
            'description': description or '',
            'created_at': created_at
        })
    return render_template('index.html', players=players_data, sessions=sessions_data)


@app.route('/player/<int:player_id>')
def player_detail(player_id):
    """Страница детальной статистики игрока"""
    try:
        stats = tracker.get_player_statistics(player_id)
        return render_template('player.html', stats=stats, player_id=player_id)
    except:
        return redirect(url_for('index'))


@app.route('/sessions')
def sessions_list():
    """Страница со списком игровых сессий"""
    sessions = tracker.get_all_game_sessions()
    sessions_data = []
    for session_id, game_date, description, created_at in sessions:
        session_stats = tracker.get_session_statistics(session_id)
        sessions_data.append({
            'id': session_id,
            'game_date': game_date,
            'description': description or '',
            'created_at': created_at,
            'players_count': session_stats.get('players_count', 0),
            'total_buyin': session_stats.get('total_buyin', 0),
            'total_wins': session_stats.get('total_wins', 0),
            'total_losses': session_stats.get('total_losses', 0)
        })
    return render_template('sessions.html', sessions=sessions_data)


@app.route('/session/<int:session_id>')
def session_detail(session_id):
    """Страница детальной статистики игровой сессии"""
    try:
        stats = tracker.get_session_statistics(session_id)
        if not stats:
            return redirect(url_for('sessions_list'))
        return render_template('session.html', stats=stats)
    except:
        return redirect(url_for('sessions_list'))


@app.route('/api/players', methods=['GET'])
def api_get_players():
    """API: Получить список всех игроков"""
    players = tracker.get_all_players()
    players_data = []
    for player_id, name, created_at in players:
        balance = tracker.get_player_balance(player_id)
        players_data.append({
            'id': player_id,
            'name': name,
            'balance': balance,
            'created_at': created_at
        })
    return jsonify(players_data)


@app.route('/api/players', methods=['POST'])
def api_add_player():
    """API: Добавить игрока"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Имя не может быть пустым'}), 400
    
    if tracker.add_player(name):
        return jsonify({'success': True, 'message': f'Игрок "{name}" добавлен'})
    else:
        return jsonify({'success': False, 'message': f'Игрок "{name}" уже существует'}), 400


@app.route('/api/players/<int:player_id>', methods=['DELETE'])
def api_delete_player(player_id):
    """API: Удалить игрока"""
    if tracker.remove_player(player_id):
        return jsonify({'success': True, 'message': 'Игрок удален'})
    else:
        return jsonify({'success': False, 'message': 'Игрок не найден'}), 404


@app.route('/api/players/<int:player_id>/statistics', methods=['GET'])
def api_get_player_stats(player_id):
    """API: Получить статистику игрока"""
    try:
        stats = tracker.get_player_statistics(player_id)
        return jsonify(stats)
    except:
        return jsonify({'error': 'Игрок не найден'}), 404


@app.route('/api/transactions', methods=['POST'])
def api_add_transaction():
    """API: Добавить транзакцию"""
    data = request.get_json()
    player_id = data.get('player_id')
    amount = data.get('amount')
    transaction_type = data.get('transaction_type')
    description = data.get('description', '').strip()
    game_date = data.get('game_date', '').strip()
    
    if not player_id or not amount or not transaction_type:
        return jsonify({'success': False, 'message': 'Недостаточно данных'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Сумма должна быть положительной'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Неверная сумма'}), 400
    
    # Если указана дата, создаем или получаем сессию
    game_session_id = None
    if game_date:
        game_session_id = tracker.get_or_create_game_session(game_date, description)
        if not game_session_id:
            return jsonify({'success': False, 'message': 'Ошибка при создании игровой сессии'}), 400
    else:
        # Если дата не указана, используем текущую дату
        today = datetime.now().strftime('%Y-%m-%d')
        game_session_id = tracker.get_or_create_game_session(today, description)
        if not game_session_id:
            return jsonify({'success': False, 'message': 'Ошибка при создании игровой сессии'}), 400
    
    if tracker.add_transaction(player_id, amount, transaction_type, description, game_session_id):
        type_names = {'buyin': 'Бай-ин', 'win': 'Выигрыш', 'loss': 'Проигрыш'}
        return jsonify({'success': True, 'message': f'{type_names.get(transaction_type, "Транзакция")} добавлен'})
    else:
        return jsonify({'success': False, 'message': 'Ошибка при добавлении транзакции'}), 400


@app.route('/api/rebuys', methods=['POST'])
def api_add_rebuy():
    """API: Добавить докуп"""
    data = request.get_json()
    player_id = data.get('player_id')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    game_date = data.get('game_date', '').strip()
    
    if not player_id or not amount:
        return jsonify({'success': False, 'message': 'Недостаточно данных'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Сумма должна быть положительной'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Неверная сумма'}), 400
    
    # Если указана дата, создаем или получаем сессию
    game_session_id = None
    if game_date:
        game_session_id = tracker.get_or_create_game_session(game_date, description)
        if not game_session_id:
            return jsonify({'success': False, 'message': 'Ошибка при создании игровой сессии'}), 400
    else:
        # Если дата не указана, используем текущую дату
        today = datetime.now().strftime('%Y-%m-%d')
        game_session_id = tracker.get_or_create_game_session(today, description)
        if not game_session_id:
            return jsonify({'success': False, 'message': 'Ошибка при создании игровой сессии'}), 400
    
    if tracker.add_rebuy(player_id, amount, description, game_session_id):
        return jsonify({'success': True, 'message': 'Докуп добавлен'})
    else:
        return jsonify({'success': False, 'message': 'Ошибка при добавлении докупа'}), 400


@app.route('/api/statistics', methods=['GET'])
def api_get_all_statistics():
    """API: Получить статистику всех игроков"""
    stats = tracker.get_all_statistics()
    return jsonify(stats)


@app.route('/api/sessions', methods=['GET'])
def api_get_sessions():
    """API: Получить список всех игровых сессий"""
    sessions = tracker.get_all_game_sessions()
    sessions_data = []
    for session_id, game_date, description, created_at in sessions:
        sessions_data.append({
            'id': session_id,
            'game_date': game_date,
            'description': description or '',
            'created_at': created_at
        })
    return jsonify(sessions_data)


@app.route('/api/sessions', methods=['POST'])
def api_create_session():
    """API: Создать игровую сессию"""
    data = request.get_json()
    game_date = data.get('game_date', '').strip()
    description = data.get('description', '').strip()
    
    if not game_date:
        return jsonify({'success': False, 'message': 'Дата обязательна'}), 400
    
    session_id = tracker.create_game_session(game_date, description)
    if session_id:
        return jsonify({'success': True, 'message': 'Игровая сессия создана', 'session_id': session_id})
    else:
        return jsonify({'success': False, 'message': 'Ошибка при создании сессии'}), 400


@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def api_get_session_stats(session_id):
    """API: Получить статистику игровой сессии"""
    stats = tracker.get_session_statistics(session_id)
    if stats:
        return jsonify(stats)
    else:
        return jsonify({'error': 'Сессия не найдена'}), 404


@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def api_delete_session(session_id):
    """API: Удалить игровую сессию"""
    if tracker.delete_game_session(session_id):
        return jsonify({'success': True, 'message': 'Игровая сессия удалена'})
    else:
        return jsonify({'success': False, 'message': 'Сессия не найдена'}), 404


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def api_delete_transaction(transaction_id):
    """API: Удалить транзакцию"""
    if tracker.delete_transaction(transaction_id):
        return jsonify({'success': True, 'message': 'Транзакция удалена'})
    else:
        return jsonify({'success': False, 'message': 'Транзакция не найдена'}), 404


@app.route('/api/rebuys/<int:rebuy_id>', methods=['DELETE'])
def api_delete_rebuy(rebuy_id):
    """API: Удалить докуп"""
    if tracker.delete_rebuy(rebuy_id):
        return jsonify({'success': True, 'message': 'Докуп удален'})
    else:
        return jsonify({'success': False, 'message': 'Докуп не найден'}), 404


@app.route('/api/players/<int:player_id>/transactions', methods=['GET'])
def api_get_player_transactions(player_id):
    """API: Получить список транзакций игрока"""
    transactions = tracker.get_player_transactions(player_id)
    return jsonify(transactions)


@app.route('/api/players/<int:player_id>/rebuys', methods=['GET'])
def api_get_player_rebuys(player_id):
    """API: Получить список докупов игрока"""
    rebuys = tracker.get_player_rebuys(player_id)
    return jsonify(rebuys)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

