from app import create_app
import logging
from healthcheck import HealthCheck

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = create_app()
app.app_context().push()

# Configuración del HealthCheck
health = HealthCheck()

# Función de verificación de salud
def app_working():
    return True, "App is working"

# Añadir la verificación de salud
health.add_check(app_working)

# Configura el endpoint de healthcheck manualmente
app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)