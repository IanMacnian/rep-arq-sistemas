# ...existing code...
import json
import os
import sys
import requests
from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file

TASKS_FILE = os.path.join(os.path.dirname(__file__), 'tasks.json')

app = Flask(__name__)

@app.route("/download-log")
def download_log():
    return send_file("errors.log", as_attachment=True)

def log_event(message):
    try:
        requests.post("http://localhost:5003/log", json={"message": message}, timeout=1)
    except:
        pass

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as file:
        try:
            tasks = json.load(file)
            valid_tasks = []
            for task in tasks:
                if isinstance(task, dict) and 'title' in task:
                    if 'completed' not in task:
                        task['completed'] = False
                    valid_tasks.append(task)
            return valid_tasks
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

@app.route('/')
def index():
    tasks = load_tasks()
    background_color = "#e6f7ff" if request.host.endswith('5001') else "#ffe6e6"
    return render_template('index.html', tasks=tasks, background_color=background_color)

@app.route('/info')
def server_info():
    return jsonify({
        'server_port': request.host.split(':')[1],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

# API - Obtener todas las tareas
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

# API - Agregar una nueva tarea
@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    tasks = load_tasks()
    data = request.json
    if 'title' in data:
        new_task = {'title': data['title'], 'completed': False}
        tasks.append(new_task)
        save_tasks(tasks)
        log_event(f"API: Nueva tarea añadida: {data['title']}")
        return jsonify(new_task), 201
    return jsonify({"error": "El título de la tarea es requerido"}), 400

# API - Marcar una tarea como completada
@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id]['completed'] = True
        save_tasks(tasks)
        log_event(f"API: Tarea completada: {tasks[task_id]['title']}")
        return jsonify(tasks[task_id])
    return jsonify({"error": "Tarea no encontrada"}), 404

# API - Eliminar una tarea
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        deleted_task = tasks.pop(task_id)
        save_tasks(tasks)
        log_event(f"API: Tarea eliminada: {deleted_task['title']}")
        return jsonify(deleted_task)
    return jsonify({"error": "Tarea no encontrada"}), 404

# Rutas web para interacción desde el navegador
@app.route('/tasks/add', methods=['POST'])
def web_add_task():
    title = request.form.get("title", "").strip()
    if not title:
        return jsonify(error="La tarea no puede estar vacía"), 400
    tasks = load_tasks()
    if any(t["title"].lower() == title.lower() for t in tasks):
        return jsonify(error="La tarea ya existe"), 400
    new_task = {"id": len(tasks) + 1, "title": title, "completed": False}
    tasks.append(new_task)
    save_tasks(tasks)
    log_event(f"WEB: Nueva tarea añadida: {title} (servidor {request.host})")
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def web_complete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        task_title = tasks[task_id]['title']
        tasks[task_id]['completed'] = True
        save_tasks(tasks)
        log_event(f"WEB: Tarea completada: {task_title} (servidor {request.host})")
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def web_delete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        task_title = tasks[task_id]['title']
        tasks.pop(task_id)
        save_tasks(tasks)
        log_event(f"WEB: Tarea eliminada: {task_title} (servidor {request.host})")
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"Servidor iniciado en puerto: {port}")
    app.run(host='0.0.0.0', port=port, debug=True)