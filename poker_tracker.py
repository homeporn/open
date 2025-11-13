#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для учета игроков в покер, сумм и докупов
"""

import sqlite3
import sys
from datetime import datetime
from typing import List, Tuple, Optional


class PokerTracker:
    """Класс для учета игроков в покер"""
    
    def __init__(self, db_path: str = "poker_tracker.db"):
        """Инициализация базы данных"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Создание таблиц в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица игроков
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица игровых сессий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_date DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица транзакций (бай-ин, выигрыши, проигрыши)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                game_session_id INTEGER,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (game_session_id) REFERENCES game_sessions(id)
            )
        """)
        
        # Таблица докупов (дополнительных взносов)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rebuys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                game_session_id INTEGER,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (game_session_id) REFERENCES game_sessions(id)
            )
        """)
        
        # Добавляем колонку game_session_id, если её нет (для миграции существующих БД)
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN game_session_id INTEGER")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        try:
            cursor.execute("ALTER TABLE rebuys ADD COLUMN game_session_id INTEGER")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        conn.commit()
        conn.close()
    
    def add_player(self, name: str) -> bool:
        """Добавить игрока"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_player(self, player_id: int) -> bool:
        """Удалить игрока"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except:
            return False
    
    def get_all_players(self) -> List[Tuple]:
        """Получить список всех игроков"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at FROM players ORDER BY name")
        players = cursor.fetchall()
        conn.close()
        return players
    
    def find_player(self, name: str) -> Optional[int]:
        """Найти игрока по имени, вернуть ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def add_transaction(self, player_id: int, amount: float, 
                       transaction_type: str, description: str = "", 
                       game_session_id: Optional[int] = None) -> bool:
        """Добавить транзакцию (бай-ин, выигрыш, проигрыш)"""
        valid_types = ['buyin', 'win', 'loss']
        if transaction_type not in valid_types:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (player_id, amount, transaction_type, description, game_session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (player_id, amount, transaction_type, description, game_session_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def add_rebuy(self, player_id: int, amount: float, description: str = "", 
                  game_session_id: Optional[int] = None) -> bool:
        """Добавить докуп"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rebuys (player_id, amount, description, game_session_id)
                VALUES (?, ?, ?, ?)
            """, (player_id, amount, description, game_session_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_player_balance(self, player_id: int) -> float:
        """Получить баланс игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Сумма всех транзакций
        cursor.execute("""
            SELECT SUM(CASE 
                WHEN transaction_type = 'buyin' THEN -amount
                WHEN transaction_type = 'win' THEN amount
                WHEN transaction_type = 'loss' THEN -amount
            END) FROM transactions WHERE player_id = ?
        """, (player_id,))
        transaction_sum = cursor.fetchone()[0] or 0
        
        # Сумма всех докупов
        cursor.execute("SELECT SUM(amount) FROM rebuys WHERE player_id = ?", (player_id,))
        rebuy_sum = cursor.fetchone()[0] or 0
        
        conn.close()
        return transaction_sum - rebuy_sum
    
    def get_player_statistics(self, player_id: int) -> dict:
        """Получить статистику игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Имя игрока
        cursor.execute("SELECT name FROM players WHERE id = ?", (player_id,))
        name = cursor.fetchone()[0]
        
        # Общий бай-ин
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE player_id = ? AND transaction_type = 'buyin'
        """, (player_id,))
        total_buyin = cursor.fetchone()[0] or 0
        
        # Общие выигрыши
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE player_id = ? AND transaction_type = 'win'
        """, (player_id,))
        total_wins = cursor.fetchone()[0] or 0
        
        # Общие проигрыши
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE player_id = ? AND transaction_type = 'loss'
        """, (player_id,))
        total_losses = cursor.fetchone()[0] or 0
        
        # Общие докупы
        cursor.execute("SELECT SUM(amount) FROM rebuys WHERE player_id = ?", (player_id,))
        total_rebuys = cursor.fetchone()[0] or 0
        
        # Количество докупов
        cursor.execute("SELECT COUNT(*) FROM rebuys WHERE player_id = ?", (player_id,))
        rebuy_count = cursor.fetchone()[0]
        
        balance = self.get_player_balance(player_id)
        
        conn.close()
        
        return {
            'name': name,
            'total_buyin': total_buyin,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_rebuys': total_rebuys,
            'rebuy_count': rebuy_count,
            'balance': balance
        }
    
    def get_all_statistics(self) -> List[dict]:
        """Получить статистику всех игроков"""
        players = self.get_all_players()
        stats = []
        for player_id, name, _ in players:
            stats.append(self.get_player_statistics(player_id))
        return stats
    
    def create_game_session(self, game_date: str, description: str = "") -> Optional[int]:
        """Создать игровую сессию. Возвращает ID сессии"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO game_sessions (game_date, description)
                VALUES (?, ?)
            """, (game_date, description))
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id
        except:
            return None
    
    def get_or_create_game_session(self, game_date: str, description: str = "") -> Optional[int]:
        """Получить существующую сессию по дате или создать новую"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM game_sessions WHERE game_date = ?", (game_date,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return self.create_game_session(game_date, description)
    
    def get_all_game_sessions(self) -> List[Tuple]:
        """Получить список всех игровых сессий"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, game_date, description, created_at 
            FROM game_sessions 
            ORDER BY game_date DESC
        """)
        sessions = cursor.fetchall()
        conn.close()
        return sessions
    
    def get_session_statistics(self, session_id: int) -> dict:
        """Получить статистику по игровой сессии"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Информация о сессии
        cursor.execute("SELECT game_date, description FROM game_sessions WHERE id = ?", (session_id,))
        session_info = cursor.fetchone()
        if not session_info:
            conn.close()
            return {}
        
        game_date, description = session_info
        
        # Статистика по транзакциям
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN transaction_type = 'buyin' THEN amount ELSE 0 END) as total_buyin,
                SUM(CASE WHEN transaction_type = 'win' THEN amount ELSE 0 END) as total_wins,
                SUM(CASE WHEN transaction_type = 'loss' THEN amount ELSE 0 END) as total_losses,
                COUNT(DISTINCT player_id) as players_count
            FROM transactions 
            WHERE game_session_id = ?
        """, (session_id,))
        trans_stats = cursor.fetchone()
        
        # Статистика по докупам
        cursor.execute("""
            SELECT SUM(amount), COUNT(*) 
            FROM rebuys 
            WHERE game_session_id = ?
        """, (session_id,))
        rebuy_stats = cursor.fetchone()
        
        # Детали по игрокам
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                SUM(CASE WHEN t.transaction_type = 'buyin' THEN -t.amount
                         WHEN t.transaction_type = 'win' THEN t.amount
                         WHEN t.transaction_type = 'loss' THEN -t.amount
                         ELSE 0 END) as transaction_balance,
                COALESCE(SUM(r.amount), 0) as rebuy_total
            FROM players p
            LEFT JOIN transactions t ON t.player_id = p.id AND t.game_session_id = ?
            LEFT JOIN rebuys r ON r.player_id = p.id AND r.game_session_id = ?
            WHERE t.id IS NOT NULL OR r.id IS NOT NULL
            GROUP BY p.id, p.name
        """, (session_id, session_id))
        players_details = cursor.fetchall()
        
        conn.close()
        
        total_buyin = trans_stats[0] or 0
        total_wins = trans_stats[1] or 0
        total_losses = trans_stats[2] or 0
        players_count = trans_stats[3] or 0
        total_rebuys = rebuy_stats[0] or 0
        rebuy_count = rebuy_stats[1] or 0
        
        players_list = []
        for player_id, name, trans_balance, rebuy_total in players_details:
            players_list.append({
                'id': player_id,
                'name': name,
                'balance': (trans_balance or 0) - (rebuy_total or 0),
                'transaction_balance': trans_balance or 0,
                'rebuy_total': rebuy_total or 0
            })
        
        return {
            'session_id': session_id,
            'game_date': game_date,
            'description': description or '',
            'total_buyin': total_buyin,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_rebuys': total_rebuys,
            'rebuy_count': rebuy_count,
            'players_count': players_count,
            'players': players_list
        }
    
    def get_player_statistics_by_date(self, player_id: int, game_date: str) -> dict:
        """Получить статистику игрока за конкретную дату"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Найти сессию по дате
        cursor.execute("SELECT id FROM game_sessions WHERE game_date = ?", (game_date,))
        session = cursor.fetchone()
        if not session:
            conn.close()
            return {}
        
        session_id = session[0]
        
        # Статистика транзакций
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN transaction_type = 'buyin' THEN amount ELSE 0 END),
                SUM(CASE WHEN transaction_type = 'win' THEN amount ELSE 0 END),
                SUM(CASE WHEN transaction_type = 'loss' THEN amount ELSE 0 END)
            FROM transactions 
            WHERE player_id = ? AND game_session_id = ?
        """, (player_id, session_id))
        trans_stats = cursor.fetchone()
        
        # Статистика докупов
        cursor.execute("""
            SELECT SUM(amount), COUNT(*) 
            FROM rebuys 
            WHERE player_id = ? AND game_session_id = ?
        """, (player_id, session_id))
        rebuy_stats = cursor.fetchone()
        
        conn.close()
        
        total_buyin = trans_stats[0] or 0
        total_wins = trans_stats[1] or 0
        total_losses = trans_stats[2] or 0
        total_rebuys = rebuy_stats[0] or 0
        rebuy_count = rebuy_stats[1] or 0
        
        return {
            'game_date': game_date,
            'total_buyin': total_buyin,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_rebuys': total_rebuys,
            'rebuy_count': rebuy_count,
            'balance': total_wins - total_buyin - total_losses - total_rebuys
        }
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Удалить транзакцию"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except:
            return False
    
    def delete_rebuy(self, rebuy_id: int) -> bool:
        """Удалить докуп"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rebuys WHERE id = ?", (rebuy_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except:
            return False
    
    def delete_game_session(self, session_id: int) -> bool:
        """Удалить игровую сессию и все связанные транзакции и докупы"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Удаляем транзакции сессии
            cursor.execute("DELETE FROM transactions WHERE game_session_id = ?", (session_id,))
            # Удаляем докупы сессии
            cursor.execute("DELETE FROM rebuys WHERE game_session_id = ?", (session_id,))
            # Удаляем саму сессию
            cursor.execute("DELETE FROM game_sessions WHERE id = ?", (session_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except:
            return False
    
    def get_player_transactions(self, player_id: int, limit: int = 50) -> List[dict]:
        """Получить список транзакций игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.amount, t.transaction_type, t.description, t.created_at, 
                   gs.game_date
            FROM transactions t
            LEFT JOIN game_sessions gs ON t.game_session_id = gs.id
            WHERE t.player_id = ?
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (player_id, limit))
        transactions = cursor.fetchall()
        conn.close()
        
        result = []
        for trans in transactions:
            result.append({
                'id': trans[0],
                'amount': trans[1],
                'transaction_type': trans[2],
                'description': trans[3] or '',
                'created_at': trans[4],
                'game_date': trans[5] or ''
            })
        return result
    
    def get_player_rebuys(self, player_id: int, limit: int = 50) -> List[dict]:
        """Получить список докупов игрока"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.amount, r.description, r.created_at, gs.game_date
            FROM rebuys r
            LEFT JOIN game_sessions gs ON r.game_session_id = gs.id
            WHERE r.player_id = ?
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (player_id, limit))
        rebuys = cursor.fetchall()
        conn.close()
        
        result = []
        for rebuy in rebuys:
            result.append({
                'id': rebuy[0],
                'amount': rebuy[1],
                'description': rebuy[2] or '',
                'created_at': rebuy[3],
                'game_date': rebuy[4] or ''
            })
        return result


def print_menu():
    """Вывести меню"""
    print("\n" + "="*50)
    print("ПОКЕР ТРЕКЕР - Учет игроков и сумм")
    print("="*50)
    print("1. Добавить игрока")
    print("2. Удалить игрока")
    print("3. Список игроков")
    print("4. Добавить бай-ин")
    print("5. Добавить выигрыш")
    print("6. Добавить проигрыш")
    print("7. Добавить докуп")
    print("8. Статистика игрока")
    print("9. Общая статистика")
    print("0. Выход")
    print("="*50)


def main():
    """Главная функция"""
    tracker = PokerTracker()
    
    while True:
        print_menu()
        choice = input("\nВыберите действие: ").strip()
        
        if choice == "0":
            print("До свидания!")
            break
        
        elif choice == "1":
            name = input("Введите имя игрока: ").strip()
            if name:
                if tracker.add_player(name):
                    print(f"✓ Игрок '{name}' добавлен")
                else:
                    print(f"✗ Игрок '{name}' уже существует")
            else:
                print("✗ Имя не может быть пустым")
        
        elif choice == "2":
            players = tracker.get_all_players()
            if not players:
                print("Нет игроков в базе")
                continue
            print("\nСписок игроков:")
            for player_id, name, _ in players:
                print(f"  {player_id}. {name}")
            try:
                player_id = int(input("Введите ID игрока для удаления: "))
                if tracker.remove_player(player_id):
                    print("✓ Игрок удален")
                else:
                    print("✗ Игрок не найден")
            except ValueError:
                print("✗ Неверный ID")
        
        elif choice == "3":
            players = tracker.get_all_players()
            if not players:
                print("Нет игроков в базе")
            else:
                print("\nСписок игроков:")
                for player_id, name, created_at in players:
                    balance = tracker.get_player_balance(player_id)
                    print(f"  {player_id}. {name} (Баланс: {balance:.2f})")
        
        elif choice == "4":
            name = input("Введите имя игрока: ").strip()
            player_id = tracker.find_player(name)
            if player_id:
                try:
                    amount = float(input("Введите сумму бай-ина: "))
                    description = input("Описание (необязательно): ").strip()
                    if tracker.add_transaction(player_id, amount, 'buyin', description):
                        print("✓ Бай-ин добавлен")
                    else:
                        print("✗ Ошибка при добавлении")
                except ValueError:
                    print("✗ Неверная сумма")
            else:
                print("✗ Игрок не найден")
        
        elif choice == "5":
            name = input("Введите имя игрока: ").strip()
            player_id = tracker.find_player(name)
            if player_id:
                try:
                    amount = float(input("Введите сумму выигрыша: "))
                    description = input("Описание (необязательно): ").strip()
                    if tracker.add_transaction(player_id, amount, 'win', description):
                        print("✓ Выигрыш добавлен")
                    else:
                        print("✗ Ошибка при добавлении")
                except ValueError:
                    print("✗ Неверная сумма")
            else:
                print("✗ Игрок не найден")
        
        elif choice == "6":
            name = input("Введите имя игрока: ").strip()
            player_id = tracker.find_player(name)
            if player_id:
                try:
                    amount = float(input("Введите сумму проигрыша: "))
                    description = input("Описание (необязательно): ").strip()
                    if tracker.add_transaction(player_id, amount, 'loss', description):
                        print("✓ Проигрыш добавлен")
                    else:
                        print("✗ Ошибка при добавлении")
                except ValueError:
                    print("✗ Неверная сумма")
            else:
                print("✗ Игрок не найден")
        
        elif choice == "7":
            name = input("Введите имя игрока: ").strip()
            player_id = tracker.find_player(name)
            if player_id:
                try:
                    amount = float(input("Введите сумму докупа: "))
                    description = input("Описание (необязательно): ").strip()
                    if tracker.add_rebuy(player_id, amount, description):
                        print("✓ Докуп добавлен")
                    else:
                        print("✗ Ошибка при добавлении")
                except ValueError:
                    print("✗ Неверная сумма")
            else:
                print("✗ Игрок не найден")
        
        elif choice == "8":
            name = input("Введите имя игрока: ").strip()
            player_id = tracker.find_player(name)
            if player_id:
                stats = tracker.get_player_statistics(player_id)
                print("\n" + "="*50)
                print(f"СТАТИСТИКА: {stats['name']}")
                print("="*50)
                print(f"Общий бай-ин:     {stats['total_buyin']:.2f}")
                print(f"Общие выигрыши:   {stats['total_wins']:.2f}")
                print(f"Общие проигрыши:  {stats['total_losses']:.2f}")
                print(f"Общие докупы:      {stats['total_rebuys']:.2f}")
                print(f"Количество докупов: {stats['rebuy_count']}")
                print(f"Текущий баланс:    {stats['balance']:.2f}")
                print("="*50)
            else:
                print("✗ Игрок не найден")
        
        elif choice == "9":
            stats_list = tracker.get_all_statistics()
            if not stats_list:
                print("Нет игроков в базе")
            else:
                print("\n" + "="*70)
                print("ОБЩАЯ СТАТИСТИКА")
                print("="*70)
                print(f"{'Имя':<20} {'Бай-ин':<12} {'Выигрыши':<12} {'Проигрыши':<12} {'Докупы':<12} {'Баланс':<12}")
                print("-"*70)
                for stats in stats_list:
                    print(f"{stats['name']:<20} {stats['total_buyin']:<12.2f} "
                          f"{stats['total_wins']:<12.2f} {stats['total_losses']:<12.2f} "
                          f"{stats['total_rebuys']:<12.2f} {stats['balance']:<12.2f}")
                print("="*70)
        
        else:
            print("✗ Неверный выбор")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()

