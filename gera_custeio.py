# coding: utf-8
import requests
from pprint import pprint
from logical.models import Project

remote_business_services = requests.get(
    'http://dicionario.dev.globoi.com/v1/custeio/servicos-de-negocio'
).json()


def find_fields(string):
    string = int(string or 0)
    for n in remote_business_services:
        if n.get('id') == int(string):
            return {
                'id': n['id'],
                'nome': n['nome'],
                'projects': []
            }
    return {
        'id': int(string),
        'nome': 'Nao informado',
        'projects': []
    }


result = {
    "origem": {
        "id": 1,
        "nome": "Processamento de Dados em Modelo Virtual",
        "provedor-de-cloud": "cloudstack",
        "ambiente": "RJCME",
        "driver": "Capacidade de processamento",
        "unidade-de-utilizacao": {
            "cpus": "Quantidade de cores",
            "memoria": "Quantidade em MB de Memória RAM",
            "quantidade": "Quantidade média de VMs no intervalo de tempo"
        },
        "abertura": "2018-01-01-00:00:00",
        "fechamento": "2018-01-31-23:59:59"
    },
    "distribuicao": {
        "servicos-de-negocio": []
    }
}
all_projects = Project.objects.order_by('business_service')

first_business_id = all_projects[0].business_service

used_business_service = find_fields(first_business_id)

for project in all_projects:
    project_business_service = int(project.business_service or 0)
    if used_business_service['id'] != project_business_service:
        result['distribuicao']['servicos-de-negocio'].append(used_business_service)
        used_business_service = find_fields(project_business_service)

    used_business_service['projects'].append({
        # id do projeto vem de onde ? é o id do meu banco ?
        'id': project.id,
        'nome': project.name,
        'consumo_detalhado': False,
        'id_origem': '7c0d5672-04ee-4502-82b3-34d4ac76ac51',
        'componente': dict(**{'id': project.component} if project.component else {}),
        'sub-componente': dict(**{'id': project.subcomponent} if project.subcomponent else {}),
        # Equipe tera no futuro
        # 'equipe': dict(**{'id': project.team} if project.team else {})
        'produto': dict(**{'id': project.product} if project.product else {}),
        'utilizacao': []
    })


result['distribuicao']['servicos-de-negocio'].append(used_business_service)

pprint(result)
