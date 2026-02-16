# import json
# import socket
# import subprocess
# import time
# import os 
# from urllib.parse import quote_plus, quote
# import boto3
# from app.utils.config import ENV_PROJECT


# def wait_for_port(host: str, port: int, timeout=15):
#     print(f"⏳ Waiting for {host}:{port} to be available...")
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.settimeout(1)
#             try:
#                 s.connect((host, port))
#                 print("✅ Tunnel is now reachable!")
#                 return True
#             except (ConnectionRefusedError, OSError):
#                 time.sleep(0.5)
#     raise TimeoutError(f"Port {port} on {host} is not reachable after {timeout}s")


# def start_ssh_tunnel():
#     """
#     Start a local SSH port-forward to the private MongoDB host via bastion.
#     Binds local <MONGO_PORT> to remote <MONGO_HOST>:<MONGO_PORT>.
#     """
#     print(f"🔧 Starting SSH tunnel with the following command:")
#     print(f"ssh -o StrictHostKeyChecking=no -i {ENV_PROJECT.SSH_KEY_PATH} -f -L {ENV_PROJECT.MONGO_PORT}:{ENV_PROJECT.MONGO_HOST}:{ENV_PROJECT.MONGO_PORT} {ENV_PROJECT.SSH_USER}@{ENV_PROJECT.SSH_HOST}")
    
#     ssh_command = [
#         "ssh",
#         "-o", "StrictHostKeyChecking=no",
#         "-i", ENV_PROJECT.SSH_KEY_PATH,
#         "-f",
#         "-L", f"{ENV_PROJECT.MONGO_PORT}:{ENV_PROJECT.MONGO_HOST}:{ENV_PROJECT.MONGO_PORT}",
#         f"{ENV_PROJECT.SSH_USER}@{ENV_PROJECT.SSH_HOST}",
#         "sleep 600",  # keep the tunnel alive for ~10 minutes
#     ]

#     print("🔧 Launching SSH tunnel...")
#     subprocess.Popen(ssh_command)
#     # Wait until the local end (localhost:<MONGO_PORT>) is reachable
#     wait_for_port("127.0.0.1", int(ENV_PROJECT.MONGO_PORT))


# def get_credentials_from_aws() -> dict:
#     print("🔐 Fetching MongoDB credentials from Secrets Manager...")
#     client = boto3.client(
#         "secretsmanager",
#         region_name=ENV_PROJECT.AWS_REGION
#     )
#     response = client.get_secret_value(SecretId=ENV_PROJECT.MONGO_SECRET_NAME)
#     secret = json.loads(response["SecretString"])
#     print("✅ Credentials fetched.")
#     return secret

# def build_documentdb_uri() -> str:
#     """
#     Build a MongoDB connection URI (now for EC2 Mongo, not DocumentDB).
#     - Uses SSH tunnel if USE_SSH_TUNNEL=True
#     - Enables TLS with CA and client cert if configured
#     - Adds authSource (default 'admin' or ENV override)
#     """
#     secret = get_credentials_from_aws()
#     username = quote_plus(secret["username"])
#     password = quote_plus(secret["password"])

#     # Database and auth DB
#     db = getattr(ENV_PROJECT, "MONGO_DB_NAME", "IVF_CHATBOT") or "IVF_CHATBOT"
#     auth_source = getattr(ENV_PROJECT, "MONGO_AUTH_SOURCE", "admin") or "admin"

#     use_tls = True  # you asked to add TLS similar to the sample
#     ca_file = getattr(ENV_PROJECT, "MONGO_TLS_CA_FILE", "certificates/ca.crt")
#     cert_key_file = getattr(ENV_PROJECT, "MONGO_TLS_CERT_FILE", "certificates/mongo.pem")
#     allow_invalid_hostnames = getattr(ENV_PROJECT, "MONGO_TLS_ALLOW_INVALID_HOSTNAMES", True)

#     # Debugging output for TLS files
#     print(f"🛠️ Use TLS: {use_tls}")
#     print(f"🛠️ TLS CA File Path: {ca_file}")
#     print(f"🛠️ TLS Cert Key File Path: {cert_key_file}")
    
#     # Check if the files exist at the given paths
#     if not os.path.isfile(ca_file):
#         print(f"❌ TLS CA file not found: {ca_file}")
#     else:
#         print(f"✅ TLS CA file found: {ca_file}")

#     if not os.path.isfile(cert_key_file):
#         print(f"❌ TLS Cert Key file not found: {cert_key_file}")
#     else:
#         print(f"✅ TLS Cert Key file found: {cert_key_file}")

#     # If tunneling, bind locally; otherwise, direct to private host (for deploy)
#     if getattr(ENV_PROJECT, "USE_SSH_TUNNEL", True):
#         print("🛠️ Starting SSH tunnel (local mode)...")
#         start_ssh_tunnel()
#         host = "127.0.0.1"
#         port = ENV_PROJECT.MONGO_PORT
#     else:
#         print("🚀 Connecting directly (deploy mode)...")
#         host = ENV_PROJECT.MONGO_HOST
#         port = ENV_PROJECT.MONGO_PORT

#     # IMPORTANT: file paths in the URI must be URL-encoded if they contain spaces
#     ca_file_q = quote(ca_file)
#     cert_key_file_q = quote(cert_key_file)

#     # Build query params
#     params = [
#         f"authSource={auth_source}",    
#     ]
#     if use_tls:
#         params.append("tls=true")
#         params.append(f"tlsCAFile={ca_file_q}")
#         params.append(f"tlsCertificateKeyFile={cert_key_file_q}")
#         if allow_invalid_hostnames:
#             params.append("tlsAllowInvalidHostnames=true")

#     query = "&".join(params)

#     uri = f"mongodb://{username}:{password}@{host}:{port}/{db}?{query}"

#     # Debugging output for the full URI
#     print("🔗 Mongo URI:", uri)
#     return uri
