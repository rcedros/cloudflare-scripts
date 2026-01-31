import os
import sys
import argparse
import httpx
from cloudflare import Cloudflare, APIError
from dotenv import load_dotenv
from typing import List, Optional

# Carrega variáveis (Token)
load_dotenv()

# --- Classe Gerenciadora (Mesma lógica anterior) ---
class CloudflareMTLSManager:
    def __init__(self, api_token: Optional[str] = None, verify_ssl: bool = True):
        self.api_token = api_token or os.environ.get("CLOUDFLARE_API_KEY")
        if not self.api_token:
            raise ValueError("Erro: CLOUDFLARE_API_KEY não encontrada, adicione em uma variavel, eg: CLOUDFLARE_API_KEY='xxxxxxxxxxx'.")

        self.http_client = httpx.Client(verify=verify_ssl)
        self.client = Cloudflare(api_token=self.api_token, http_client=self.http_client)

    def import_bundle(self, account_id: str, bundle_pem_path: str) -> Optional[str]:
        print(f"🔄 Importando bundle de: {bundle_pem_path} ...")
        try:
            with open(bundle_pem_path, "r") as f:
                bundle_content = f.read()

            mtls_certificate = self.client.mtls_certificates.create(
                account_id=account_id,
                ca=True,
                certificates=bundle_content
            )
            return mtls_certificate.id
        except FileNotFoundError:
            print(f"Erro: O arquivo '{bundle_pem_path}' não existe.")
            return None
        except APIError as e:
            print(f"Erro na API Cloudflare: {e}")
            return None

    def update_associates(self, zone_id: str, mtls_certificate_id: str, hostnames: List[str]) -> List[str]:
        print(f"🔄 Atualizando associação para a zona {zone_id}...")
        try:
            hostname_association = self.client.certificate_authorities.hostname_associations.update(
                zone_id=zone_id,
                mtls_certificate_id=mtls_certificate_id,
                hostnames=hostnames
            )
            return hostname_association.hostnames
        except APIError as e:
            print(f"Erro na API Cloudflare: {e}")
            return []

    def get_associates(self, zone_id: str, mtls_certificate_id: str) -> Optional[List[str]]:
        print(f"🔍 Buscando associações para o certificado {mtls_certificate_id}...")
        try:
            hostname_association = self.client.certificate_authorities.hostname_associations.get(
                zone_id=zone_id,
                mtls_certificate_id=mtls_certificate_id,
            )
            if hostname_association.hostnames:
                return hostname_association.hostnames
            return []
        except APIError as e:
            print(f"Erro na API Cloudflare: {e}")
            return None

# --- Lógica de Linha de Comando (CLI) ---
def main():
    parser = argparse.ArgumentParser(description="Gerenciador CLI de Cloudflare mTLS")

    # Grupo de Ações (O usuário deve escolher EXATAMENTE uma dessas opções)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--import-bundle', action='store_true', help='Importar um novo certificado CA')
    action_group.add_argument('--update-associates', action='store_true', help='Associar hostnames a um certificado')
    action_group.add_argument('--get-associates', action='store_true', help='Verificar associações existentes')

    # Argumentos (Flags)
    parser.add_argument('--account', help='ID da Conta Cloudflare')
    parser.add_argument('--zone_id', help='ID da Zona (Site)')
    parser.add_argument('--mtls_certificate_id', help='ID do Certificado mTLS')
    parser.add_argument('--bundle', help='Caminho para o arquivo .pem')
    parser.add_argument('--hostnames', nargs='+', help='Lista de hostnames (separados por espaço)')
    
    # Flag opcional para ignorar SSL (útil no seu caso)
    parser.add_argument('--insecure', action='store_true', help='Ignorar validação SSL (Não recomendado para prod)')

    args = parser.parse_args()

    # Inicializa o Manager (decidindo se verifica SSL ou não)
    verify_ssl = not args.insecure
    try:
        manager = CloudflareMTLSManager(verify_ssl=verify_ssl)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # --- Lógica 1: Import Bundle ---
    if args.import_bundle:
        if not args.account or not args.bundle:
            print("Erro: Para importar, você precisa fornecer --account e --bundle")
            sys.exit(1)
        
        cert_id = manager.import_bundle(args.account, args.bundle)
        if cert_id:
            print(f"Sucesso! Certificado criado com ID: {cert_id}")

    # --- Lógica 2: Update Associates ---
    elif args.update_associates:
        if not args.zone_id or not args.mtls_certificate_id or not args.hostnames:
            print("Erro: Para atualizar, forneça --zone_id, --mtls_certificate_id e --hostnames")
            sys.exit(1)

        result = manager.update_associates(args.zone_id, args.mtls_certificate_id, args.hostnames)
        if result:
            print(f"Sucesso! Hostnames associados: {result}")
        else:
            print("A operação retornou uma lista vazia ou falhou.")

    # --- Lógica 3: Get Associates ---
    elif args.get_associates:
        if not args.zone_id or not args.mtls_certificate_id:
            print("Erro: Para consultar, forneça --zone_id e --mtls_certificate_id")
            sys.exit(1)

        hostnames = manager.get_associates(args.zone_id, args.mtls_certificate_id)
        if hostnames:
            print(f"Hostnames associados encontrados: {hostnames}")
            
            # Se o usuário passou --hostnames no GET, podemos fazer uma verificação extra
            if args.hostnames:
                for h in args.hostnames:
                    if h in hostnames:
                        print(f"   -> O hostname '{h}' ESTÁ na lista.")
                    else:
                        print(f"   -> O hostname '{h}' NÃO ESTÁ na lista.")
        else:
            print("Nenhum hostname associado encontrado.")

if __name__ == "__main__":
    main()
