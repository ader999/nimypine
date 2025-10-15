# test_minio_upload.py

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# --- Cargar y verificar variables (igual que antes) ---
print("--- Cargando variables desde el archivo .env ---")
load_dotenv()
endpoint_url = os.getenv("MINIO_S3_ENDPOINT_URL")
access_key = os.getenv("MINIO_ACCESS_KEY_ID")
secret_key = os.getenv("MINIO_SECRET_ACCESS_KEY")
bucket_name = os.getenv("MINIO_BUCKET_NAME")

if not all([endpoint_url, access_key, secret_key, bucket_name]):
    print("❌ ERROR: Faltan variables de entorno. Revisa tu .env.")
    exit()

print("✅ Todas las variables fueron encontradas.")
print(f"   - Endpoint: {endpoint_url}")
print(f"   - Bucket: {bucket_name}\n")


# --- Intento de Subida ---
print(f"--- Intentando subir un archivo de prueba ('test_upload.txt') al bucket '{bucket_name}'... ---")

try:
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Contenido y nombre del archivo de prueba
    file_content = "Si puedes leer esto, la subida funcionó."
    object_name = "test_upload.txt"

    # Subir el archivo
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=file_content.encode('utf-8'),
        ContentType='text/plain'
    )

    print(f"✅ ¡ÉXITO! El archivo '{object_name}' fue subido correctamente al bucket '{bucket_name}'.")
    print("   - Esto confirma que tus credenciales tienen permisos de ESCRITURA (PutObject).")

except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code")
    if error_code == 'AccessDenied':
        print("❌ FALLÓ POR PERMISOS (Access Denied).")
        print("   - Razón: Las credenciales son válidas, pero el usuario no tiene permiso para realizar la acción 'PutObject' en este bucket.")
        print("   - SOLUCIÓN: Ve a Minio y asegúrate de que la política de tu usuario (NO la del bucket) incluya 's3:PutObject'.")
    else:
        print(f"❌ Ocurrió un error inesperado del cliente: {error_code}")
    print(f"\n   - ERROR TÉCNICO COMPLETO: {e}")

except Exception as e:
    print(f"❌ Ocurrió un error completamente inesperado.")
    print(f"\n   - ERROR TÉCNICO: {e}")