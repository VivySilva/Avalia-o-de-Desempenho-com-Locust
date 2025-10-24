"""
Script para popular o banco de dados do Spring PetClinic
com dados de teste para garantir que os endpoints GET
retornem resultados consistentes durante os testes de carga.
"""

import requests
import random
import time
from typing import List, Dict

BASE_URL = "http://localhost:8080"

# Listas para gerar dados variados
FIRST_NAMES = [
    "João", "Maria", "Pedro", "Ana", "Carlos", "Juliana", "Rafael", "Fernanda",
    "Lucas", "Beatriz", "Marcos", "Patricia", "Fernando", "Camila", "Ricardo",
    "Amanda", "Gabriel", "Leticia", "Bruno", "Larissa", "Thiago", "Vanessa"
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Ferreira", "Rodrigues",
    "Almeida", "Nascimento", "Araújo", "Carvalho", "Gomes", "Martins", "Rocha",
    "Ribeiro", "Alves", "Monteiro", "Mendes", "Barros", "Freitas", "Barbosa"
]

CITIES = [
    "Picos", "São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza",
    "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Porto Alegre", "Belém"
]

STREETS = [
    "Rua das Flores", "Avenida Principal", "Rua do Comércio", "Avenida Central",
    "Rua dos Pinheiros", "Alameda dos Anjos", "Travessa do Porto", "Rua da Paz",
    "Avenida Paulista", "Rua Sete de Setembro", "Rua do Rosário", "Avenida Beira Mar"
]


def check_api_health() -> bool:
    """Verifica se a API está respondendo"""
    try:
        response = requests.get(f"{BASE_URL}/api/customer/owners", timeout=5)
        return response.status_code == 200
    except:
        return False


def create_owner(first_name: str, last_name: str, address: str, 
                 city: str, telephone: str) -> Dict:
    """Cria um novo dono no sistema"""
    owner = {
        "firstName": first_name,
        "lastName": last_name,
        "address": address,
        "city": city,
        "telephone": telephone
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customer/owners",
            json=owner,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return {"success": True, "owner": owner}
        else:
            return {"success": False, "error": f"Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_owners(count: int) -> List[Dict]:
    """Gera uma lista de donos com dados aleatórios"""
    owners = []
    
    for i in range(1, count + 1):
        owner = {
            "firstName": random.choice(FIRST_NAMES),
            "lastName": random.choice(LAST_NAMES),
            "address": f"{random.choice(STREETS)}, {random.randint(1, 999)}",
            "city": random.choice(CITIES),
            "telephone": f"88{random.randint(10000000, 99999999)}"
        }
        owners.append(owner)
    
    return owners


def main():
    print("=" * 60)
    print("POPULAR BANCO DE DADOS - SPRING PETCLINIC")
    print("=" * 60)
    
    # Verificar conectividade
    print("\n1. Verificando conectividade com a API...")
    if not check_api_health():
        print("✗ ERRO: API não está respondendo!")
        print("  Certifique-se de que o Spring PetClinic está rodando:")
        print("  docker-compose up -d")
        return
    
    print("✓ API está respondendo")
    
    # Definir quantidade de donos a criar
    total_owners = 100
    print(f"\n2. Gerando {total_owners} donos de teste...")
    
    owners = generate_owners(total_owners)
    print(f"✓ {total_owners} donos gerados")
    
    # Criar donos no sistema
    print(f"\n3. Criando donos no sistema...")
    print("   (Este processo pode levar alguns minutos)")
    
    success_count = 0
    error_count = 0
    
    for i, owner_data in enumerate(owners, 1):
        result = create_owner(**owner_data)
        
        if result["success"]:
            success_count += 1
            if i % 10 == 0:
                print(f"   Progresso: {i}/{total_owners} donos criados...")
        else:
            error_count += 1
            if error_count <= 5:  # Mostrar apenas os 5 primeiros erros
                print(f"   ✗ Erro ao criar dono {i}: {result.get('error')}")
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.1)
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"✓ Donos criados com sucesso: {success_count}")