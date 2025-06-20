import requests

base_url = "http://localhost:5001"

print("Ejecutando pruebas de error...")

# Error 400 - JSON vacío
try:
    r = requests.post(f"{base_url}/tasks/add", data="")
    print("Error 400:", r.status_code)
except Exception as e:
    print("Fallo en prueba 400:", e)

# Error 404 - Ruta inexistente
try:
    r = requests.get(f"{base_url}/noexiste")
    print("Error 404:", r.status_code)
except Exception as e:
    print("Fallo en prueba 404:", e)

# Error 500 - División por cero
try:
    r = requests.get(f"{base_url}/crash")
    print("Error 500:", r.status_code)
except Exception as e:
    print("Fallo en prueba 500:", e)

# Ver estadísticas
try:
    r = requests.get(f"{base_url}/errors/stats")
    print("Estadísticas:")
    print(r.json())
except Exception as e:
    print("No se pudo obtener stats:", e)
