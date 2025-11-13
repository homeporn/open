// Показать модальное окно добавления игрока
function showAddPlayerModal() {
    document.getElementById('addPlayerModal').style.display = 'block';
    document.getElementById('playerName').focus();
}

// Показать модальное окно транзакции
function showTransactionModal(playerId, playerName) {
    document.getElementById('transactionModal').style.display = 'block';
    document.getElementById('transactionPlayerId').value = playerId;
    document.getElementById('transactionModalTitle').textContent = `Добавить транзакцию: ${playerName}`;
    document.getElementById('transactionAmount').focus();
}

// Показать модальное окно докупа
function showRebuyModal(playerId, playerName) {
    document.getElementById('rebuyModal').style.display = 'block';
    document.getElementById('rebuyPlayerId').value = playerId;
    document.getElementById('rebuyModalTitle').textContent = `Добавить докуп: ${playerName}`;
    document.getElementById('rebuyAmount').focus();
}

// Закрыть модальное окно
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    // Очистить форму
    const form = document.getElementById(modalId.replace('Modal', 'Form'));
    if (form) {
        form.reset();
    }
}

// Закрыть модальное окно при клике вне его
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Переключение темы
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    const button = document.getElementById('themeToggle');
    if (button) {
        button.textContent = theme === 'dark' ? '☀️ Светлая' : '🌙 Темная';
    }
}

// Загрузить сохраненную тему при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
});

// Добавить игрока
async function addPlayer(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const name = formData.get('name');

    try {
        const response = await fetch('/api/players', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            closeModal('addPlayerModal');
            location.reload();
        } else {
            alert(data.message);
        }
    } catch (error) {
        alert('Ошибка при добавлении игрока: ' + error.message);
    }
}

// Удалить игрока
async function deletePlayer(playerId, playerName) {
    if (!confirm(`Вы уверены, что хотите удалить игрока "${playerName}"? Это действие нельзя отменить.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/players/${playerId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert(data.message);
        }
    } catch (error) {
        alert('Ошибка при удалении игрока: ' + error.message);
    }
}

// Добавить транзакцию
async function addTransaction(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const data = {
        player_id: parseInt(formData.get('player_id')),
        amount: parseFloat(formData.get('amount')),
        transaction_type: formData.get('transaction_type'),
        description: formData.get('description') || '',
        game_date: formData.get('game_date') || ''
    };

    try {
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);
            closeModal('transactionModal');
            location.reload();
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Ошибка при добавлении транзакции: ' + error.message);
    }
}

// Добавить докуп
async function addRebuy(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const data = {
        player_id: parseInt(formData.get('player_id')),
        amount: parseFloat(formData.get('amount')),
        description: formData.get('description') || '',
        game_date: formData.get('game_date') || ''
    };

    try {
        const response = await fetch('/api/rebuys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);
            closeModal('rebuyModal');
            location.reload();
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Ошибка при добавлении докупа: ' + error.message);
    }
}

