# Documentação CKAN SEPLAN - Repositório Customizado

---
TODO: Fazer index com as separacoes do repositorio

# PARTE 1: DOCUMENTAÇÃO DAS MODIFICAÇÕES E CUSTOMIZAÇÕES

## 1. Visão Geral do Repositório Customizado

Este repositório contém uma implementação customizada do CKAN especificamente desenvolvida para atender às necessidades da SEPLAN. As principais modificações incluem extensões personalizadas, configurações específicas e processos automatizados de deploy e backup.

### Estrutura do Projeto

#TODO

## 2. Extensões Customizadas

### 2.1 Extensão ckanext-seplan

A **ckanext-seplan** é a extensão principal que abriga todas as customizações específicas para a SEPLAN:

#### Funcionalidades Implementadas:

- **Interface de Usuário Customizada**: 
  - Tema visual adaptado à identidade visual da SEPLAN
  - Layout responsivo com elementos específicos
  - Componentes de navegação personalizados
  - Dashboard administrativo customizado


### 2.2 Extensão ckanext-scheming

A **ckanext-scheming** é utilizada para personalizar o modelo de metadados:

#### Recursos Implementados:

- **Esquemas Personalizados**: Definição de campos específicos usando YAML/JSON
- **Validação de Dados**: Regras de validação customizadas para garantir qualidade
- **Formulários Dinâmicos**: Criação automática de formulários baseados em esquemas
- **Tipos de Dados Específicos**: Campos personalizados para necessidades da SEPLAN


## Explicar com exemplo aqui

## 4. Aspectos do Deploy

### 4.1 Pipeline CI/CD

O sistema utiliza GitHub Actions para automatização completa do deploy:

#todo inserir referencia para o procedimento no repositório

### 4.2 Ambientes

#### Produção
- **URL**: https://ckan.seplan.gov.br
- **Deploy**: Manual via aprovação no GitHub
- **Monitoramento**: 24/7 com alertas automáticos

### 4.3 Configurações Específicas

#### Variáveis de Ambiente Produção

## 5. Política de Backup

### 5.1 Estratégia Implementada

**Frequência**: Backups automatizados executados **a cada 2 semanas**

**Componentes incluídos**:
- Banco PostgreSQL completo (metadados, usuários, organizações)
- Arquivos de dados (uploads, recursos)
- Configurações customizadas
- Esquemas de metadados

### 5.2 Armazenamento Azure

Os dados ficam armazenados num azure blob container 



### 5.4 Política de rentenção

- Por padrão, os últimos 5 backups são armazenados no storage.

---

# PARTE 2: DOCUMENTAÇÃO OFICIAL CKAN DOCKER

## 1. Visão Geral do CKAN Oficial

Esta seção documenta a configuração base do CKAN usando Docker Compose, baseada no repositório oficial [ckan-docker](https://github.com/ckan/ckan-docker-base).

### Componentes Oficiais

* **CKAN Core**: Plataforma base de dados abertos
* **PostgreSQL**: Banco de dados oficial para metadados
* **Solr**: Motor de busca e indexação oficial
* **Redis**: Cache e gerenciamento de sessões
* **DataPusher**: Serviço para importação de dados
* **NGINX**: Servidor web e proxy reverso

## 2. Instalação Base

### 2.1 Pré-requisitos

Instale o Docker seguindo a documentação oficial: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

Verificação da instalação:
```bash
docker run hello-world
docker version
```

### 2.2 Configuração docker compose vs docker-compose

O projeto utiliza `docker compose` (plugin) em vez do `docker-compose` (standalone). Certifique-se de usar a versão correta:

```bash
# Correto (plugin)
docker compose up

# Deprecado (standalone)
docker-compose up
```

## 3. Modos de Execução

### 3.1 Modo Base (Produção)

Para uso em produção sem modificações no código:

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Construir imagens
docker compose build

# Iniciar serviços
docker compose up -d
```

**Estrutura de serviços**:
```bash
$ docker compose ps
NAME                       IMAGE                              STATUS
ckan-docker-ckan-1         ckan-docker-ckan                   Up (healthy)
ckan-docker-datapusher-1   ckan/ckan-base-datapusher:0.0.20   Up (healthy)
ckan-docker-db-1           ckan-docker-db                     Up (healthy)
ckan-docker-nginx-1        ckan-docker-nginx                  Up
ckan-docker-redis-1        redis:6                            Up (healthy)
ckan-docker-solr-1         ckan/ckan-solr:2.10-solr9          Up (healthy)
```

### 3.2 Modo Desenvolvimento

Para desenvolvimento com modificações de código:

```bash
# Usar scripts de desenvolvimento
bin/compose build
bin/install_src
bin/compose up
```

**Scripts disponíveis**:
- `bin/ckan …`: Comandos CKAN no container
- `bin/compose …`: Comandos docker compose para dev
- `bin/generate_extension`: Gerar nova extensão
- `bin/install_src`: Instalar extensões do diretório src/
- `bin/reload`: Recarregar CKAN sem reiniciar
- `bin/shell`: Shell bash no container

## 4. Arquitetura das Imagens CKAN

### 4.1 Dockerfile Base

```dockerfile
FROM ckan/ckan-base:2.11.0

# Instalação de extensões customizadas
RUN pip install -e git+https://github.com/seplan/ckanext-seplan.git#egg=ckanext-seplan

# Cópia de configurações
COPY setup/ ${APP_DIR}/
```

### 4.2 Dockerfile.dev

```dockerfile
FROM ckan/ckan-base:2.11.0-dev

# Auto-instalação de extensões do src/
# Execução em modo desenvolvimento
# Debugging habilitado
```

### 4.3 Estendendo Imagens Base

**Adicionando extensões**:
```dockerfile
FROM ckan/ckan-base:2.11.0-dev

RUN pip install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest && \
    pip install -r https://raw.githubusercontent.com/ckan/ckanext-harvest/master/requirements.txt

COPY docker-entrypoint.d/* /docker-entrypoint.d/
```

**Scripts de inicialização**: Qualquer arquivo `.sh` ou `.py` em `/docker-entrypoint.d/` será executado na inicialização.

## 5. Configuração de Serviços

### 5.1 PostgreSQL (Datastore)

- **Imagem**: postgres:14
- **Volumes**: Dados persistidos em volume nomeado
- **Configuração**: Usuários e bancos criados automaticamente

### 5.2 Solr (Indexação)

- **Imagem**: ckan/ckan-solr:2.10-solr9
- **Função**: Indexação e busca de datasets
- **Volume**: Índices persistidos

### 5.3 Redis (Cache)

- **Imagem**: redis:6
- **Função**: Cache de sessões e dados temporários
- **Configuração**: Sem persistência por padrão

### 5.4 NGINX (Proxy Reverso)

- **Configuração SSL**: Certificado autoassinado gerado automaticamente
- **Portas**: 80 (HTTP) e 8443 (HTTPS)
- **Customização**: Configurações em `nginx/setup/`

```bash
# Gerar certificado SSL customizado
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
  -subj "/C=BR/ST=TO/L=Palmas/O=SEPLAN/CN=ckan.seplan.gov.br" \
  -keyout nginx/setup/ckan.key \
  -out nginx/setup/ckan.crt
```

## 6. Configuração via Variáveis de Ambiente

### 6.1 ckanext-envvars

O CKAN utiliza a extensão `ckanext-envvars` para configuração via variáveis de ambiente:

**Formato das variáveis**:
- Todas maiúsculas
- Substituir `.` por `__`
- Prefixo `CKAN` ou `CKANEXT`

**Exemplos**:
```bash
CKAN__PLUGINS="envvars image_view text_view recline_view datastore datapusher"
CKAN__DATAPUSHER__CALLBACK_URL_BASE=http://ckan:5000
CKAN___BEAKER__SESSION__SECRET=CHANGE_ME
```

### 6.2 Configurações Essenciais

```bash
# .env base
CKAN_SITE_URL=https://localhost:8443
CKAN_SYSADMIN_NAME=admin
CKAN_SYSADMIN_PASSWORD=CHANGE_ME
POSTGRES_USER=ckan
POSTGRES_PASSWORD=ckan
POSTGRES_DB=ckan
```

## 7. Gerenciamento de Usuários

### 7.1 Comandos Base

```bash
# Criar usuário
docker compose exec ckan ckan user add admin email=admin@localhost

# Tornar sysadmin
docker compose exec ckan ckan sysadmin add admin

# Remover usuário
docker compose exec ckan ckan user remove admin
```

### 7.2 Modo Desenvolvimento

```bash
# Usar scripts de desenvolvimento
bin/ckan user add admin email=admin@localhost
bin/ckan sysadmin add admin
```

## 8. Depuração e Desenvolvimento

### 8.1 Depuração com pdb

Adicionar ao `docker-compose.dev.yml`:
```yaml
ckan-dev:
  stdin_open: true
  tty: true
```

Comando de depuração:
```bash
docker attach $(docker container ls -qf name=ckan)
python -m pdb /usr/lib/ckan/venv/bin/ckan --config /srv/app/ckan.ini run --host 0.0.0.0
```

### 8.2 VS Code Remote Debugging

1. Habilitar debugpy no `.env`:
```bash
USE_DEBUGPY_FOR_DEV=true
```

2. Instalar debugpy:
```bash
bin/install_src
```

3. Configurar VS Code:
   - Instalar extensão "Dev Container"
   - Conectar ao container em execução
   - Configurar debug remoto na porta 5678

## 9. Aplicação de Patches

### 9.1 Estrutura de Patches

```
ckan/
├── patches/
│   ├── ckan/
│   │   ├── 01_datasets_per_page.patch
│   │   └── 02_groups_per_page.patch
│   └── ckanext-harvest/
│       └── 01_resubmit_objects.patch
```

### 9.2 Aplicação Automática

Os patches são aplicados automaticamente durante o build das imagens, em ordem alfabética.

## 10. Alternativas e Extensões

### 10.1 Substituindo DataPusher por XLoader

Para melhor performance em grandes volumes:

```bash
# Desabilitar DataPusher
CKAN__PLUGINS="envvars xloader datastore"

# Configurar XLoader
CKAN__XLOADER__API_TOKEN=your-api-token
```

### 10.2 Alterando Versão Base

Modificar nos Dockerfiles:
```dockerfile
# De:
FROM ckan/ckan-base:2.11.0

# Para:
FROM ckan/ckan-base:2.10.5
```

---

## Licença e Direitos Autorais

Este material é copyright (c) 2006-2023 Open Knowledge Foundation e colaboradores.

É aberto e licenciado sob a GNU Affero General Public License (AGPL) v3.0 cujo texto completo pode ser encontrado em:

http://www.fsf.org/licensing/licenses/agpl-3.0.html