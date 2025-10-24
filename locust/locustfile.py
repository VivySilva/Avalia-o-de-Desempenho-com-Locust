from locust import HttpUser, task, between
import random


class PetClinicUser(HttpUser):
    """
    Simula usuários acessando o Spring PetClinic Microservices
    Mix de requisições conforme especificação:
    - 40% GET /owners (lista donos)
    - 30% GET /owners/{id} (dono específico)
    - 20% GET /vets (lista veterinários)
    - 10% POST /owners (cadastro)
    """
    
    # Simula tempo humano entre requisições (1-3 segundos)
    wait_time = between(1, 3)

    @task(4)  # 40% das requisições
    def list_owners(self):
        """Lista todos os donos cadastrados"""
        self.client.get("/api/customer/owners")

    @task(3)  # 30% das requisições
    def get_owner_by_id(self):
        """Busca um dono específico por ID"""
        owner_id = random.randint(1, 10)  # Ajuste conforme população do banco
        self.client.get(f"/api/customer/owners/{owner_id}")

    @task(2)  # 20% das requisições
    def list_vets(self):
        """Lista todos os veterinários"""
        self.client.get("/api/vet/vets")

    @task(1)  # 10% das requisições
    def create_owner(self):
        """Cria um novo dono"""
        new_owner = {
            "firstName": f"Teste{random.randint(1, 9999)}",
            "lastName": f"Locust{random.randint(1, 9999)}",
            "address": f"Rua Teste {random.randint(1, 999)}",
            "city": "Picos",
            "telephone": f"88{random.randint(10000000, 99999999)}"
        }
        self.client.post("/api/customer/owners", json=new_owner)