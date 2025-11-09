# Documentação CKAN SEPLAN - Repositório Customizado

## Sumário

- [Como Contribuir](#como-contribuir)
- [Visão Geral do Projeto](#visão-geral-do-projeto)
- [Principais Funcionalidades e Customizações](#principais-funcionalidades-e-customizações)
  - [Funcionalidades do Plugin (`plugin.py`)](#funcionalidades-do-plugin-pluginpy)
  - [Funções Customizadas (`plugin.py`)](#funções-customizadas-pluginpy)
  - [Customização de Templates (Interface do Usuário)](#customização-de-templates-interface-do-usuário)
- [Extensões Adicionais](#extensões-adicionais)
  - [Customização do modelo de Metadados](#customização-do-modelo-de-metadados)
  - [Outras extensões](#outras-extensões)
- [Deploy e CI/CD](#deploy-e-cicd)
  - [Gatilhos do Workflow (Triggers)](#gatilhos-do-workflow-triggers)
  - [Processo de Build e Push das Imagens (Job: `build_push_acs`)](#processo-de-build-e-push-das-imagens-job-build_push_acs)
  - [Processo de Deploy no Ambiente de Produção (Job: `deploy_to_vm`)](#processo-de-deploy-no-ambiente-de-produção-job-deploy_to_vm)
- [Política de Backup](#política-de-backup)

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

O processo de deploy da aplicação é automatizado com GitHub Actions, definido no arquivo `.github/workflows/deploy-ckan.yml`. Este workflow automatiza o build, o push das imagens Docker customizadas para o Azure Container Registry (ACR) e o deploy para a máquina virtual de produção.

### Gatilhos do Workflow (Triggers)

O processo é iniciado automaticamente nos seguintes eventos:
* Quando há um `push` para as branches `master` ou `adjust/backend-uploadtimeout`.
* O processo também pode ser iniciado manualmente através da interface do GitHub Actions (`workflow_dispatch`).

### Processo de Build e Push das Imagens (Job: `build_push_acs`)

Quando acionado, o workflow executa os seguintes passos em um ambiente `ubuntu-latest`:

1.  **Checkout do Repositório:** Clona o código do repositório.
2.  **Configuração do QEMU e Docker Buildx:** Prepara o ambiente para builds Docker multi-arquitetura.
3.  **Login no Azure Container Registry (ACR):** Realiza o login no ACR utilizando credenciais seguras armazenadas nos `secrets` do repositório (ACR_LOGIN_SERVER, ACR_SP_APP_ID, ACR_SP_PASSWORD).
4.  **Build e Push das Imagens:** O workflow constrói três imagens Docker distintas e as envia para o ACR com a tag `latest`:
    *   **NGINX:** Construída a partir do diretório `./nginx`. Tag: `${{ secrets.ACR_LOGIN_SERVER }}/ckan-nginx:latest`
    *   **PostgreSQL:** Construída a partir do diretório `./postgresql`. Tag: `${{ secrets.ACR_LOGIN_SERVER }}/ckan-postgresql:latest`
    *   **CKAN:** Construída a partir do diretório `./ckan`, que contém a aplicação principal e as extensões customizadas. Tag: `${{ secrets.ACR_LOGIN_SERVER }}/ckan-ckan:latest`

### Processo de Deploy no Ambiente de Produção (Job: `deploy_to_vm`)

Este job é executado após o sucesso do `build_push_acs` e realiza o deploy na VM de produção via SSH:

1.  **SSH na VM:** Conecta-se à máquina virtual de produção usando `appleboy/ssh-action` e credenciais seguras (VM_HOST, VM_USERNAME, VM_SSH_PRIVATE_KEY).
2.  **Login no ACR (na VM):** Realiza o login no Azure Container Registry diretamente na VM para poder puxar as imagens.
3.  **Navegação ao Diretório:** Navega até o diretório `ckan-orcamento` na VM.
4.  **Pull das Imagens:** Executa `docker compose -f docker-compose.prod.yml pull` para baixar as imagens mais recentes do ACR.
5.  **Reinício dos Serviços:** Executa `docker compose -f docker-compose.prod.yml up -d --remove-orphans` para parar os serviços antigos, iniciar os novos com as imagens atualizadas e remover containers órfãos.
6.  **Limpeza de Imagens Antigas:** Executa `docker image prune -af` para remover imagens Docker não utilizadas e liberar espaço em disco.

## Política de Backup

Esta política descreve o processo automatizado para garantir a recuperabilidade dos dados da plataforma CKAN. O processo é gerenciado por um script que executa o backup dos bancos de dados, armazena-os no Azure Blob Storage e mantém uma política de retenção para gerenciar o espaço de armazenamento. Todas as operações são registradas em um arquivo de log dentro da máquina virtual.

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