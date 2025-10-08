# Documentação CKAN SEPLAN - Repositório Customizado

# PARTE 1: DOCUMENTAÇÃO DAS MODIFICAÇÕES E CUSTOMIZAÇÕES

## Como Contribuir

Contribuições para melhorar este portal são bem-vindas. Para configurar o ambiente de desenvolvimento e entender o fluxo de trabalho, consulte nosso [**Guia de Contribuição**](CONTRIBUTING.md).


## Visão Geral do Projeto

Este repositório contém o código-fonte e a documentação da instância customizada do CKAN para o Portal de Dados Orçamentários do Município de São Paulo. O projeto utiliza uma extensão personalizada, a `ckanext-seplan`, para adaptar a aparência e as funcionalidades da plataforma às necessidades específicas do portal.

O objetivo principal é oferecer um ambiente centralizado, transparente e de fácil acesso para os dados do ciclo orçamentário, incluindo o Plano Plurianual (PPA), a Lei de Diretrizes Orçamentárias (LDO), a Lei Orçamentária Anual (LOA) e a execução orçamentária.

## Principais Funcionalidades e Customizações

As customizações estão concentradas na extensão `ckanext-seplan`, que implementa lógicas de backend através do `plugin.py` e personaliza a interface do usuário com templates HTML. 

### Funcionalidades do Plugin (`plugin.py`)

O arquivo `plugin.py` é o núcleo da extensão e implementa diversas interfaces do CKAN para estender seu comportamento padrão.

* **IConfigurer**: Este plugin é responsável por registrar os diretórios customizados da extensão (`templates/`, `public/`, `assets/`) na aplicação principal do CKAN. Isso permite que a extensão sobrescreva templates padrão e sirva arquivos estáticos próprios, como logos, imagens e folhas de estilo CSS.

* **ITemplateHelpers**: Implementa funções Python que podem ser chamadas diretamente dos templates HTML. Isso permite que a interface exiba informações dinâmicas, como listas de organizações e grupos em destaque na página inicial, sem a necessidade de lógica complexa no frontend. As funções principais são `get_featured_groups` e `get_featured_organizations`.

* **IPackageController**: Este plugin modifica o processo de indexação de dados. Através do método `before_dataset_index`, ele extrai um metadado específico de cada recurso (`res_extra_periodo`) e o promove ao nível do conjunto de dados. Essa modificação é crucial, pois torna o campo "Períodos" uma faceta pesquisável em todo o portal.

* **IFacets**: Com esta interface, os nomes técnicos das facetas de busca são substituídos por títulos mais amigáveis ao usuário. Por exemplo, `organization` é exibido como "Organizações", `res_format` como "Formatos", e o campo customizado `res_extra_periodo` é apresentado como "Períodos", melhorando a experiência de navegação e busca.

### Funções Customizadas (`plugin.py`)

Para dar vida às funcionalidades do portal, o `plugin.py` implementa funções auxiliares e modifica o comportamento de indexação do CKAN.

#### Funções de Template (Template Helpers)

Estas funções são expostas para serem usadas diretamente nos arquivos de template (`.html`), permitindo que a interface busque dados dinâmicos do backend - para mais informações, veja a seção sobre helper functions na documentação do [CKAN](https://docs.ckan.org/en/2.9/theming/template-helper-functions.html). 

* **`get_featured_groups()`**: Busca e retorna uma lista de grupos para exibição em destaque na página inicial. A função prioriza grupos que possuem uma imagem ou que tenham pelo menos um dataset associado.
* **`get_all_groups_with_images()`**: Retorna uma lista de todos os grupos que possuem uma imagem de exibição cadastrada, ordenada alfabeticamente.
* **`get_featured_organizations()`**: Busca e retorna uma lista de organizações para exibição em destaque. Assim como a função de grupos, prioriza aquelas com imagem ou com datasets publicados.

#### Funções de indexação de metadados (`before_dataset_index`)

Esta função é uma das customizações de backend mais importantes e é o que torna a faceta "Períodos" funcional.

O CKAN permite filtrar datasets por campos que existem no nível do *dataset* (conjunto de dados), mas o campo "Período" (`res_extra_periodo`) foi originalmente definido no nível de *recurso* (os arquivos individuais dentro de um dataset).

A função **`before_dataset_index`** resolve esse problema. Ela é executada automaticamente toda vez que um dataset está prestes a ser indexado pelo motor de busca (Solr). O seu papel é:
1.  **Inspecionar o Dataset**: Acessa cada um dos recursos (arquivos) dentro do dataset que será indexado.
2.  **Coletar os Períodos**: Lê o valor do campo `res_extra_periodo` de cada recurso.
3.  **Promover os Dados**: Agrupa todos os valores únicos de "Período" encontrados nos recursos e os adiciona a uma nova lista no nível do *dataset*.
4.  **Permitir a Faceta**: Ao "promover" essa informação, o campo "Períodos" se torna visível para o Solr, que consegue então criar um filtro (faceta) a partir dele na página de busca. Isto permite a criação de filtros de busca a partir dos metadados customizados. 

Em resumo, essa função transforma um metadado de nível de recurso em um metadado de nível de dataset, tornando-o uma ferramenta de busca poderosa para o usuário final.

### Customização de Templates (Interface do Usuário)

Vários arquivos de template foram modificados ou criados para customizar a landing page e o css do portal. Estes arquivos estão localizados em ckanext-seplan/ckanext/seplan/templates e ckanext-seplan/ckanext/seplan/public.

* **`header.html`**: Personaliza o cabeçalho do site, substituindo o logo padrão do CKAN pelo logo da SEPLAN.

* **`footer.html`**: Modifica o rodapé global. Altera o link "Sobre" para direcionar à página correta do portal e inclui a logo da "Base dos Dados" como desenvolvedora da solução.

* **`search.html`**: Altera o componente de busca na página inicial, definindo um texto de exemplo (`placeholder`) específico para o contexto orçamentário, como "E.g. Lei Orçamentaria Anual".

* **`promoted.html` e `about_text.html`**: Estes arquivos contêm o texto de boas-vindas e a apresentação do portal. Eles explicam o propósito do site, os tipos de dados disponíveis e o objetivo de promover a transparência fiscal.

* **`organizations.html`**: Cria a seção "Organizações" na página inicial. Utiliza uma função do `ITemplateHelpers` para buscar e exibir as organizações em destaque, com seus logos, nomes e a quantidade de datasets publicados.

* **`groups.html`**: Similarmente ao arquivo de organizações, este template renderiza a seção de "Grupos" temáticos na página inicial, exibindo os grupos mais relevantes com suas imagens e contagem de datasets.

* **`resource_read.html`**: Ajusta a página de visualização de um recurso de dados. A modificação impede que o metadado customizado "Período" seja exibido de forma duplicada na tabela de informações adicionais. Esta configuração merece uma explicação adicional: o arquivo resource_read.html é gerada pela extensão ckanext-scheming. Essa extensão é utilizada para criar campos de metadados customizados. 

## Extensões Adicionais

### Customização do modelo de Metadados

A extensão `ckanext-scheming` viabilza a criação e gestão de **esquemas de metadados personalizados** através de arquivos YAML, sem a necessidade de implementar funcionalidades em Python através das interaces de Plugins do Ckan. Isso possibilita a criação de formulários de submissão de dados totalmente adaptados às necessidades específicas de um projeto.

Nesta implementação, a `ckanext-scheming` é utilizada para adaptar o formulário de submissão de dados às necessidades do portal orçamentário. A principal customização realizada foi a adição do campo **`Período`** (com o nome técnico `res_extra_periodo`). Este campo foi adicionado no **nível do recurso** (resource) que permite que cada arquivo individual (como uma planilha ou PDF) dentro de um conjunto de dados seja associado a um ano ou período de referência específico (ex: '2025'). A criação deste campo via `ckanext-scheming` foi o primeiro passo que, posteriormente, permitiu sua utilização como um filtro de busca (faceta), através da customização de indexação realizada no `plugin.py`.

### Outras extensões

Além da extensão principal `ckanext-seplan` e da `ckanext-scheming`, esta instância do CKAN utiliza outras extensões para adicionar funcionalidades importantes de visualização e configuração:

* **`ckanext-envvars`**: Essencial para ambientes containerizados, esta extensão permite que a configuração do CKAN seja lida a partir de variáveis de ambiente. Em vez de ter valores "hardcoded" no arquivo `ckan.ini`, configurações como senhas de banco de dados, chaves secretas e listas de plugins podem ser injetadas de forma segura durante a execução do contêiner. Essas configurações ficam no arquivo .env

* **`ckanext-pdf_view`**: Melhora a experiência do usuário ao integrar um visualizador de PDFs diretamente na página do recurso. Com esta extensão, em vez de precisar baixar um arquivo `.pdf` para visualizá-lo, o usuário pode abri-lo e lê-lo dentro da própria interface do CKAN.

* **`ckanext-geoview`**: Adiciona a capacidade de visualizar dados geoespaciais. Esta extensão fornece visualizadores para formatos como GeoJSON, KML e Shapefile (quando convertidos), permitindo que recursos com dados geográficos sejam exibidos como mapas interativos diretamente na página do recurso, em vez de apenas um link para download.

## Deploy e CI/CD

O processo de deploy da aplicação é automatizado com github actions. O script pode ser acessado em .github/workflows. O workflow, definido no arquivo de configuração do GitHub Actions, automatiza o processo de build e publicação das imagens Docker customizadas da aplicação.

### Gatilhos do Workflow (Triggers)

O processo é iniciado automaticamente nos seguintes eventos:
* Quando há um `push` para a branch `master`.
* O processo também pode ser iniciado manualmente através da interface do GitHub Actions (`workflow_dispatch`).

### Processo de build das imagens

Quando acionado, o workflow executa os seguintes passos em um ambiente `ubuntu-latest`:

1.  **Autenticação:** O primeiro passo é realizar o login no Docker Hub utilizando credenciais seguras armazenadas nos `secrets` do repositório (`DOCKERHUB_USERNAME` e `DOCKERHUB_PASSWORD`).

2.  **Build das Imagens:** O workflow constrói três imagens Docker distintas, cada uma a partir do seu respectivo `Dockerfile` e contexto:
    * **NGINX:** Construída a partir do diretório `./nginx`.
    * **PostgreSQL:** Construída a partir do diretório `./postgresql`.
    * **CKAN:** Construída a partir do diretório `./ckan`, que contém a aplicação principal e as extensões customizadas.

3.  **Push para o Docker Hub:** Após cada imagem ser construída com sucesso, ela é enviada (push) para o repositório no Docker Hub com a tag `latest`. As imagens publicadas são:
    * `folhesgabriel/ckan-docker-nginx:latest` 
    * `folhesgabriel/ckan-docker-postgresql:latest` 
    * `folhesgabriel/ckan-docker-ckan:latest` 

### Processo de deploy no ambiente de produção

1. Acessar a VM de produção via SSH.
2. Navegar até o diretório do `docker compose`.
3. Matar a rede de containers atual `docker compose down`.
3. Executar o comando `docker compose pull` para baixar as imagens mais recentes do Docker Hub.
4. Executar `docker compose up -d` para recriar os contêineres com as novas imagens, aplicando as atualizações.

## Política de Backup

Esta política descreve o processo automatizado para garantir a segurança e a recuperabilidade dos dados da plataforma CKAN. O processo é gerenciado por um script que executa o backup dos bancos de dados, armazena-os no Azure Blob Storage e mantém uma política de retenção para gerenciar o espaço de armazenamento. Todas as operações são registradas em um arquivo de log dentro da máquina virtual.

### Componentes do Backup

Cada arquivo de backup gerado é um arquivo compactado (`.tar.gz`) que contém os seguintes componentes essenciais:

* **Dump do Banco de Dados Principal (`ckandb`):** Um arquivo `.sql` contendo a exportação completa do banco de dados principal do CKAN.  Isso inclui todos os metadados dos datasets, usuários, organizações, grupos e configurações do sistema.

* **Dump do Banco de Dados Datastore (`datastore`):** Um arquivo `.sql` contendo a exportação completa do banco de dados do Datastore. Isso inclui todos os dados tabulares que foram enviados para a API do Datastore.

### O que Não é Incluído

Este processo de backup foca exclusivamente nos bancos de dados. Ele **não** inclui os arquivos enviados pelos usuários (como CSVs, PDFs, imagens) que são armazenados no *filestore* do CKAN. Uma estratégia de backup separada deve ser considerada para o diretório de armazenamento (`CKAN_STORAGE_PATH`).

### Processo de Execução do Backup

O backup é executado na seguinte sequência:

1.  **Criação dos Dumps de Banco de Dados:** O script se conecta ao contêiner do banco de dados e utiliza o comando `pg_dump` para exportar os bancos de dados `ckandb` e `datastore` separadamente. Cada dump é salvo em um arquivo `.sql` com um timestamp único em um diretório temporário (`/tmp/ckan_backups`).

2.  **Compactação:** Os dois arquivos `.sql` gerados são combinados em um único arquivo de backup compactado no formato `.tar.gz` (ex: `ckan_backup_20251008_073447.tar.gz`). Após a compactação bem-sucedida, os arquivos `.sql` originais são removidos.

3.  **Envio dos arquivos para o  Azure Blob Storage:** O arquivo compactado é enviado para um contêiner de armazenamento dedicado chamado `ckan-orcamento`, localizado na conta de Azure Blob Storage `ckanbackups`.

### Política de Retenção

Foi implementado uma política de retenção:

* Somente os **10 backups mais recentes** são mantidos no Azure Blob Storage.
* Ao final de cada execução bem-sucedida do backup, o script lista todos os backups mais antigos (além dos 10 mais recentes) e os exclui automaticamente do Azure.

### Monitoramento e Logs

Todas as ações executadas pelo script de backup, desde o início até a conclusão (ou falha), são registradas com data e hora em um arquivo de log dentro da VM em `/var/log/ckan_backup.log`. Este arquivo serve como um registro de auditoria e é a principal ferramenta para diagnosticar quaisquer problemas com o processo de backup.

## 6. Vixe, deu ruim. Algum problema ocorreu e os dados e metadados no ckan foram perdidos. Como restaurar? 
#TODO: Adicionar tutorial de Restore

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