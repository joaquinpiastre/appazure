# SCRIPT PARA DESPLEGAR UNA IMAGEN DE DOCKER A AZURE CONTAINER REGISTRY (ACR)

import os
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv
from colorama import init, Fore, Style

init()
load_dotenv()

# Funciones para imprimir mensajes con colores
def print_info(message):
    print(Fore.CYAN + f"[{datetime.now().strftime('%H:%M:%S')}] - [INFO] {message}" + Style.RESET_ALL)

def print_success(message):
    print(Fore.GREEN + f"[{datetime.now().strftime('%H:%M:%S')}] - [SUCCESS] {message}" + Style.RESET_ALL)

def print_error(message):
    print(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}] - [ERROR] {message}" + Style.RESET_ALL)

def input_question(message):
    return input(Fore.YELLOW + f"[{datetime.now().strftime('%H:%M:%S')}] - [¿?] {message}" + Style.RESET_ALL)

# Función para confirmar el deploy
def confirm_deploy():
    print_info("Este script realizará las siguientes acciones:")
    print_info("    1. Cargar variables de entorno necesarias.")
    print_info("    2. Verificar si Docker está ejecutándose.")
    print_info("    3. Construir y etiquetar la imagen de Docker.")
    print_info("    4. Iniciar sesión en Azure Container Registry (ACR).")
    print_info("    5. Subir la imagen de Docker a ACR.")
    response = input_question("¿Desea continuar con el deploy? (s/n): ")
    if response.lower() == "s":
        print_success("Deploy confirmado.")
    else:
        print_error("Deploy cancelado.")
        exit(1)

# Cargar variables de entorno necesarias
def load_env_variables():
    env_vars = {
        "RESOURCE_GROUP": os.getenv("RESOURCE_GROUP"),
        "LOCATION": os.getenv("LOCATION"),
        "ACR_NAME": os.getenv("ACR_NAME"),
        "IMAGE_NAME": os.getenv("IMAGE_NAME"),
        "CONTAINER_NAME": os.getenv("CONTAINER_NAME"),
        "IMAGE_TAG": os.getenv("IMAGE_TAG"),
    }
    for key, value in env_vars.items():
        if not value:
            print_error(f"Error: La variable de entorno {key} no está definida.")
            exit(1)
    return env_vars

# Función para verificar si Docker está ejecutándose
def check_docker_running():
    print_info("Verificando si Docker está ejecutándose...")
    time.sleep(1)
    try:
        subprocess.check_output(["docker", "info"]) # Verifica si Docker está ejecutándose
        print_success("Docker está ejecutándose.")
    except subprocess.CalledProcessError:
        print_error("Error: Docker no está ejecutándose.")
        exit(1)

# Verificar si existe la imagen de Docker
def check_docker_image_exists(image_name, image_tag):
    print_info("Verificando si la imagen de Docker existe...")
    time.sleep(1)
    try:
        subprocess.check_output(["docker", "image", "inspect", f"{image_name}:{image_tag}"]) # Verifica si la imagen de Docker existe
        print_success("La imagen de Docker ya existe.")
    except subprocess.CalledProcessError:
        print_error("Error: La imagen de Docker no existe.")
        create_image = input_question("¿Desea crear la imagen de Docker? (s/n): ")
        if create_image.lower() == "s":
            print_info("Creando la imagen de Docker...")
            subprocess.run(["docker", "build", "-t", f"{image_name}:{image_tag}", "."])  # Crea la imagen de Docker
            print_success("Imagen de Docker creada.")
        else:
            print_error("Error: El script requiere que la imagen de Docker exista.")
            exit(1)

# Verificar si el usuario está logueado en Azure
def check_azure_login():
    print_info("Verificando si el usuario está logueado en Azure...")
    time.sleep(1)
    try:
        subprocess.check_output("az account show", shell=True) # Verifica si el usuario está logueado en Azure
        print_success("Usuario logueado en Azure.")
    except subprocess.CalledProcessError:
        print_error("Error: Usuario no logueado en Azure.")
        login_azure = input_question("¿Desea loguearse en Azure? (s/n): ")
        if login_azure.lower() == "s":
            print_info("Logueando en Azure...")
            subprocess.run("az login", shell=True)
            print_success("Logueado en Azure.")
        else:
            print_error("Error: El script requiere que el usuario esté logueado en Azure.")
            exit(1)

# Verificar si el grupo de recursos existe
def check_resource_group_exists(resource_group, location):
    print_info(f"Verificando si el grupo de recursos {resource_group} existe...")
    time.sleep(1)
    try:
        subprocess.check_output(f"az group show --name {resource_group}", shell=True) # Verifica si el grupo de recursos existe
        print_success(f"El grupo de recursos {resource_group} ya existe.")
    except subprocess.CalledProcessError:
        create_resource_group = input_question(f"El grupo de recursos {resource_group} no existe. ¿Desea crearlo? (s/n): ")
        if create_resource_group.lower() == "s":
            print_info(f"Creando el grupo de recursos {resource_group}...")
            subprocess.run(f"az group create --name {resource_group} --location {location}", shell=True) # Crea el grupo de recursos            
            print_success(f"Grupo de recursos {resource_group} creado.")
        else:
            print_error(f"Error: El script requiere que el grupo de recursos {resource_group} exista.")
            exit(1)

# Verificar si ACR existe
def check_acr_exists(acr_name, resource_group):
    print_info(f"Verificando si el ACR {acr_name} existe...")
    time.sleep(1)
    try:
        subprocess.check_output(f"az acr show --name {acr_name}", shell=True) # Verifica si el ACR existe
        print_success(f"El ACR {acr_name} ya existe.")
    except subprocess.CalledProcessError:
        create_acr = input_question(f"El ACR {acr_name} no existe. ¿Desea crearlo? (s/n): ")
        if create_acr.lower() == "s":
            print_info(f"Creando el ACR {acr_name}...")
            subprocess.run(f"az acr create --resource-group {resource_group} --name {acr_name} --sku Basic", shell=True) # Crea el ACR
            print_success(f"ACR {acr_name} creado.")
        else:
            print_error(f"Error: ACR {acr_name} no creado.")
            exit(1)

# Login a ACR
def login_acr(acr_name):
    print_info(f"Logueando en ACR {acr_name}...")
    subprocess.run(f"az acr login --name {acr_name}", shell=True) # Login a ACR
    print_success("Logueado en ACR.")

# Etiquetar la imagen de Docker
def tag_docker_image(image_name, acr_name, image_tag):
    print_info("Etiquetando la imagen de Docker...")
    subprocess.run(
        f"docker tag {image_name}:{image_tag} {acr_name}.azurecr.io/{image_name}:{image_tag}", shell=True
        ) # Etiqueta la imagen de Docker
    print_success("Imagen construida y etiquetada.")

# Analizar la imagen con Grype para encontrar vulnerabilidades
def scan_image_with_grype(image_name, image_tag):
    print_info(f"Analizando la imagen {image_name}:{image_tag} con Grype...")
    subprocess.run(["grype", f"{image_name}:{image_tag}", "--by-cve"], check=True)
    print_error("Se encontraron vulnerabilidades en la imagen:")
    upload_image = input_question("¿Desea subir la imagen a ACR a pesar de las vulnerabilidades? (s/n): ")
    if upload_image.lower() != "s":
        print_error("Deploy cancelado debido a vulnerabilidades en la imagen.")
        exit(1)
    else:
        print_info("Continuando con el deploy a pesar de las vulnerabilidades.")

# Subir la imagen a ACR
def push_docker_image(acr_name, image_name, image_tag):
    print_info(f"Subiendo la imagen {image_name} a ACR {acr_name}...")
    subprocess.run(f"docker push {acr_name}.azurecr.io/{image_name}:{image_tag}", shell=True) # Sube la imagen a ACR
    print_success("Imagen subida a ACR.")

# Listar los repositorios en ACR
def list_acr_repositories(acr_name):
    print_info("Repositorios en ACR:")
    subprocess.run(f"az acr repository list --name {acr_name} --output table", shell=True) # Lista los repositorios en ACR
    
# Crear el contenedor en Azure
def create_azure_container(resource_group, container_name, acr_name, image_name, image_tag, location):
    print_info(f"Verificando si el contenedor {container_name} ya existe en el grupo de recursos {resource_group}...")
    try:
        # Verificar si el contenedor ya existe
        try:
            subprocess.check_output(
                f"az container show --resource-group {resource_group} --name {container_name}", 
                shell=True
            )
            print_info(f"El contenedor {container_name} ya existe.")
            use_different_name = input_question("¿Desea subir el contenedor con otro nombre? (s/n): ")
            if use_different_name.lower() == "s":
                container_name = input_question("Ingrese el nuevo nombre para el contenedor: ")
            else:
                return
        except subprocess.CalledProcessError:
            print_info(f"El contenedor {container_name} no existe. Procediendo a crearlo...")

        # Habilitar acceso de administrador en ACR
        print_info(f"Habilitando acceso de administrador para ACR {acr_name}...")
        subprocess.run(f"az acr update -n {acr_name} --admin-enabled true", shell=True, check=True)
        print_success(f"Acceso de administrador habilitado para ACR {acr_name}.")
        
        # Obtener credenciales del ACR
        registry_username = subprocess.check_output(
            f"az acr credential show --name {acr_name} --query username -o tsv", 
            shell=True
        ).strip().decode('utf-8')
        registry_password = subprocess.check_output(
            f"az acr credential show --name {acr_name} --query passwords[0].value -o tsv", 
            shell=True
        ).strip().decode('utf-8')
        
        # Crear el contenedor
        subprocess.run(
            f"az container create --resource-group {resource_group} --name {container_name} "
            f"--image {acr_name}.azurecr.io/{image_name}:{image_tag} --cpu 1 --memory 1 "
            f"--registry-login-server {acr_name}.azurecr.io --registry-username {registry_username} "
            f"--registry-password {registry_password} --dns-name-label dns-{container_name} --ip-address Public --location {location} "
            f"--ports 5000",
            shell=True, check=True
        )
        print_success(f"Contenedor {container_name} creado exitosamente.")
    except subprocess.CalledProcessError:
        print_error(f"Error: No se pudo crear el contenedor {container_name}.")
        exit(1)

def main(): # Función principal
    confirm_deploy() # Confirmar el Deploy
    
    header = "========================= SCRIPT DEPLOY ========================="
    message = "Deploy de imagen de Docker a Azure Container Registry (ACR)..."
    print_info(f"\n{header}\n{message}") # Mensaje de bienvenida
    
    env_vars = load_env_variables() # Cargar variables de entorno
    
    check_docker_running() # Verifica si Docker está ejecutándose
    check_docker_image_exists(env_vars["IMAGE_NAME"], env_vars["IMAGE_TAG"]) # Verifica si la imagen de Docker existe
    check_azure_login() # Verifica si el usuario está logueado en Azure
    check_resource_group_exists(env_vars["RESOURCE_GROUP"], env_vars["LOCATION"]) # Verifica si el grupo de recursos existe
    check_acr_exists(env_vars["ACR_NAME"], env_vars["RESOURCE_GROUP"]) # Verifica si ACR existe
    login_acr(env_vars["ACR_NAME"]) # Login a ACR
    tag_docker_image(env_vars["IMAGE_NAME"], env_vars["ACR_NAME"], env_vars["IMAGE_TAG"]) # Etiqueta la imagen de Docker
    scan_image_with_grype(env_vars["IMAGE_NAME"], env_vars["IMAGE_TAG"]) # Analiza la imagen con Grype para encontrar vulnerabilidades
    push_docker_image(env_vars["ACR_NAME"], env_vars["IMAGE_NAME"], env_vars["IMAGE_TAG"]) # Sube la imagen a ACR
    list_acr_repositories(env_vars["ACR_NAME"]) # Lista los repositorios en ACR
    create_azure_container(
        env_vars["RESOURCE_GROUP"], 
        env_vars["CONTAINER_NAME"], 
        env_vars["ACR_NAME"], 
        env_vars["IMAGE_NAME"], 
        env_vars["IMAGE_TAG"], 
        env_vars["LOCATION"],
    ) # Crea el contenedor en Azure

    end_message = "DEPLOY completado. La aplicación se encuentra en ejecución."
    print_success(f"\n{header}\n{end_message}") # Mensaje final

if __name__ == "__main__":
    main()
