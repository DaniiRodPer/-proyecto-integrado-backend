# Backend del proyecto integrado

## Requisitos para la Ejecución

Para levantar este servidor en local, asegúrate de cumplir con lo siguiente:

### 1. Base de Datos (MariaDB / MySQL)
- Tener instalado **MariaDB** o MySQL.
- Crear una base de datos vacía.
- Configurar en el fichero .env:
  - Usuario y contraseña de la Base de Datos
  - Usuario y contraseña del servicio de email
  
  ```python
  SQLALCHEMY_DATABASE_URL = "mysql+pymysql://USUARIO:CONTRASEÑA@localhost:3306/proyectodrp"

### 2. Entorno Python (MariaDB / MySQL)

- Crear el entorno
  
  ```python
  python -m venv venv

- Activar el entorno (Linux/macOS)
  
  ```python
  source venv/bin/activate

- Activar el entorno (Windows)
  
   ```python
  venv\Scripts\activate

### 3. Instalar dependencias

  ```bash
   pip install -r requirements.txt
  ```

### 4. Iniciar el servidor

   ```python
  uvicorn app.main:app --reload --host 0.0.0.0
  ```

- Nota: Usar --host 0.0.0.0 es fundamental para que el emulador de Android pueda comunicarse con el servidor.
