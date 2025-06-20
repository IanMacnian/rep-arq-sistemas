from flask import Flask, request, render_template, redirect, jsonify
import json, os, sys
from collections import defaultdict

app = Flask(__name__)
DATA_FILE = "tasks.json"

# Variables para logging de errores
error_stats = defaultdict(int)
error_log = []

# Función para registrar errores
def log_error(error_type, details=""):
    error_stats[error_type] += 1
    error_log.append(f"{error_type} - {details}")

# Cargar tareas
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Guardar tareas
def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

@app.route("/")
def index():
    tasks = load_tasks()
    port = request.host.split(":")[-1]
    return render_template("index.html", tasks=tasks, port=port)

@app.route("/tasks/add", methods=["POST"])
def add_task():
    try:
        tasks = load_tasks()
        new_task = {"id": len(tasks) + 1, "text": request.form["task"], "done": False}
        tasks.append(new_task)
        save_tasks(tasks)
        return redirect("/")
    except Exception as e:
        log_error("500_INTERNAL_ERROR", str(e))
        return jsonify(error="Error interno"), 500

@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
    save_tasks(tasks)
    return redirect("/")

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return redirect("/")

# Simulación de error 500 para pruebas
@app.route("/crash")
def crash():
    return 1 / 0

# Endpoint para estadísticas de errores
@app.route('/errors/stats')
def error_stats_view():
    return jsonify({
        'total_errors': sum(error_stats.values()),
        'error_types': dict(error_stats),
        'recent_errors': error_log[-10:]
    })

# Manejadores de errores
@app.errorhandler(400)
def bad_request(e):
    log_error("400_BAD_REQUEST", str(e))
    return jsonify(error="Solicitud malformada"), 400

@app.errorhandler(404)
def not_found(e):
    log_error("404_NOT_FOUND", str(e))
    return jsonify(error="Recurso no encontrado"), 404

@app.errorhandler(500)
def internal_error(e):
    log_error("500_INTERNAL_ERROR", str(e))
    return jsonify(error="Error interno del servidor"), 500

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(port=port)
