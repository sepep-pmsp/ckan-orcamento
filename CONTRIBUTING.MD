# Contributing - Customização da UI do CKAN

Este guia explica como contribuir com customizações na interface do usuário (UI) do CKAN utilizando a extensão `ckanext-seplan` em ambiente de desenvolvimento.

## Sobre o CKAN

CKAN (Comprehensive Knowledge Archive Network) é uma plataforma open-source para gerenciamento de dados que permite organizações publicar, compartilhar e gerenciar dados de forma estruturada. No contexto técnico, CKAN é construído em Python usando o framework web Pylons/Flask, PostgreSQL como banco de dados principal, Apache Solr para indexação e busca, e Redis para cache e processamento de tarefas. A arquitetura modular do CKAN permite extensibilidade através de plugins (extensões), que podem adicionar funcionalidades personalizadas, modificar a interface do usuário, integrar APIs externas ou implementar workflows específicos de dados. Cada instância CKAN organiza informações em datasets (conjuntos de dados), resources (recursos como arquivos CSV, JSON, APIs), organizations (organizações proprietárias dos dados) e groups (agrupamentos temáticos), fornecendo uma API RESTful completa para integração com sistemas externos e facilitando a criação de portais de dados abertos governamentais e corporativos.


## Pré-requisitos

- Docker e Docker Compose instalados
- Git instalado
- Editor de código de sua preferência
- Conhecimentos básicos de HTML/CSS e Jinja2

## Configuração do Ambiente de Desenvolvimento

### 1. Clonando o Repositório

```bash
# Clone o repositório principal
git clone https://github.com/seu-usuario/ckan-orcamento.git
cd ckan-orcamento
```

### 2. Configuração do Ambiente

```bash
# Copie o arquivo de configuração de desenvolvimento
cp .env.example .env

# Edite o arquivo .env para incluir a extensão seplan
```

### 3. Build das Imagens de Desenvolvimento

```bash
# Construa as imagens de desenvolvimento
docker compose -f docker-compose.dev.yml build

# Inicie os serviços
docker compose -f docker-compose.dev.yml up -d

# Verifique se todos os containers estão rodando
docker compose -f docker-compose.dev.yml ps
```

### 4. Sobre a Extensão no Repositório



A extensão `ckanext-seplan` está localizada no diretório `src/` do repositório e é automaticamente montada como volume no container Docker durante o desenvolvimento. 
Esta configuração permite que todas as alterações feitas nos arquivos da extensão (CSS, templates, código Python) sejam refletidas imediatamente no ambiente CKAN sem necessidade de rebuild da imagem Docker.

A estrutura do volume está configurada no `docker-compose.dev.yml`:

```yaml
volumes:
  - ./src:/srv/app/src_extensions
```

Isso significa que:
- `./src/ckanext-seplan/` (local) → `/srv/app/src_extensions/ckanext-seplan/` (container)
- Mudanças em templates e CSS são aplicadas instantaneamente
- Alterações em código Python requerem apenas restart do serviço CKAN
- Não é necessário reinstalar a extensão para cada modificação durante desenvolvimento

A instalação e ativação da extensão são feitas de forma automática ao rodar o build do docker-compose.dev.yml pelo script 02_setup_seplan.sh

## Estrutura da Extensão ckanext-seplan

```
src/ckanext-seplan/
├── LICENSE
├── MANIFEST.in
├── README.md
├── ckanext/
│   ├── __init__.py
│   └── seplan/                    # Módulo principal da extensão
│       ├── __init__.py
│       ├── plugin.py              # Arquivo principal do plugin
│       ├── assets/                # Recursos gerenciados via webassets
│       │   ├── script.js          # JavaScript customizado
│       │   ├── style.css          # CSS principal da extensão
│       │   └── webassets.yml      # Configuração do webassets
│       ├── i18n/                  # Arquivos de internacionalização
│       ├── public/                # Arquivos estáticos servidos diretamente
│       │   ├── custom.css         # CSS adicional/sobrescritas
│       │   └── seplan.png         # Logo/imagens da SEPLAN
│       ├── templates/             # Templates Jinja2 customizados
│       │   ├── base.html          # Template base da aplicação
│       │   ├── header.html        # Cabeçalho customizado
│       │   └── home/
│       │       └── snippets/
│       │           └── promoted.html  # Snippet da seção promocional
│       └── tests/                 # Testes automatizados
│           ├── __init__.py
│           └── test_plugin.py
├── ckanext_seplan.egg-info/       # Metadados do pacote Python
├── dev-requirements.txt           # Dependências de desenvolvimento
├── pyproject.toml                 # Configuração moderna do projeto Python
├── requirements.txt               # Dependências de produção
├── setup.cfg                      # Configurações de setup
├── setup.py                       # Script de instalação
└── test.ini                       # Configurações para testes
```

## Customização da Interface

### 1. Personalizando CSS

#### Arquivo Principal de Estilos

Crie ou edite o arquivo `src/ckanext-seplan/ckanext/seplan/public/custom.css`:
Este arquivo sobrescreve as configurações de CSS default


```css
/* Customizações gerais do tema */
.site-header {
  background-color: #2c3e50;
  border-bottom: 3px solid #3498db;
}

.logo img {
  max-height: 60px;
}

/* Customização da navbar */
.navbar-nav > li > a {
  color: #ecf0f1 !important;
  font-weight: 500;
}

.navbar-nav > li > a:hover {
  background-color: #34495e;
  color: #3498db !important;
}

/* Estilização dos botões principais */
.btn-primary {
  background-color: #3498db;
  border-color: #2980b9;
}

.btn-primary:hover {
  background-color: #2980b9;
  border-color: #21618c;
}

/* Customização do rodapé */
.site-footer {
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 40px 0;
}

/* Cards de datasets */
.dataset-item {
  border-left: 4px solid #3498db;
  transition: transform 0.2s;
}

.dataset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
```

#### CSS Específico para Páginas

Para customizações específicas de páginas, crie arquivos CSS modulares:

```css
/* src/ckanext-seplan/ckanext/seplan/public/css/dataset.css */

/* Estilização da página de dataset */
.dataset-content .module-content {
  padding: 25px;
}

.resource-item {
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  margin-bottom: 15px;
  padding: 15px;
}

.resource-item:hover {
  border-color: #3498db;
  background-color: #f8f9fa;
}

/* Melhorias na visualização de metadados */
.dataset-info dt {
  color: #2c3e50;
  font-weight: 600;
}

.dataset-info dd {
  margin-bottom: 10px;
  color: #5a6c7d;
}
```

### 2. Customizando Templates

#### Template Base

Crie ou edite `src/ckanext-seplan/ckanext/seplan/templates/base.html`:

```html
{% ckan_extends %}

{% block links -%}
  {{ super() }}
  {% resource 'seplan/css/seplan.css' %}
  {% resource 'seplan/css/custom.css' %}
{%- endblock %}

{% block styles %}
  {{ super() }}
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap">
{% endblock %}

{% block scripts %}
  {{ super() }}
  {% resource 'seplan/js/custom.js' %}
{% endblock %}
```

#### Customizando o Header

Edite `src/ckanext-seplan/ckanext/seplan/templates/header.html`:

```html
{% ckan_extends %}

{% block header_logo %}
  <div class="logo">
    <a href="{{ h.url_for('home.index') }}">
      <img src="{{ h.url_for_static('/images/logo-prefeitura-sp.png') }}" 
           alt="{{ g.site_title }}" title="{{ g.site_title }}">
      <span class="site-title">Portal de Dados Orçamentários</span>
    </a>
  </div>
{% endblock %}

{% block header_account_logged %}
  {{ super() }}
  <div class="account-info">
    <span class="username">{{ c.user }}</span>
    <a href="{{ h.url_for('user.logout') }}" class="btn btn-logout">
      <i class="fa fa-sign-out"></i> Sair
    </a>
  </div>
{% endblock %}
```

#### Customizando a Página Inicial

Crie `src/ckanext-seplan/ckanext/seplan/templates/home/index.html`:

```html
{% ckan_extends %}

{% block primary_content %}
  <div class="hero-section">
    <div class="container">
      <div class="row">
        <div class="col-md-8">
          <h1 class="hero-title">Portal de Dados Orçamentários</h1>
          <p class="hero-subtitle">
            Acesse informações transparentes sobre o orçamento público 
            do município de São Paulo
          </p>
          <a href="{{ h.url_for('dataset.search') }}" class="btn btn-primary btn-lg">
            Explorar Dados
          </a>
        </div>
        <div class="col-md-4">
          <div class="stats-widget">
            <h3>Estatísticas</h3>
            <div class="stat-item">
              <span class="stat-number">{{ h.get_site_statistics().dataset_count }}</span>
              <span class="stat-label">Datasets</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  {{ super() }}
{% endblock %}
```

### 3. Registrando Recursos Estáticos

No arquivo `src/ckanext-seplan/ckanext/seplan/plugin.py`:

```python
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

class seplanPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'seplan')

    # Registrar arquivos CSS/JS via fanstatic
    def setup_template_variables(self, context, data_dict):
        toolkit.c.userobj = context.get('user_obj')
```

Crie o arquivo de recursos `src/ckanext-seplan/ckanext/seplan/fanstatic.py`:

```python
from fanstatic import Library, Resource

library = Library('seplan', 'public')

seplan_css = Resource(
    library, 'css/seplan.css',
    minified='css/seplan.min.css'
)

custom_css = Resource(
    library, 'css/custom.css',
    depends=[seplan_css]
)

custom_js = Resource(
    library, 'js/custom.js',
    minified='js/custom.min.js'
)
```

## Exemplos de Customizações Avançadas

### 1. Tema Escuro

```css
/* Implementação de tema escuro */
@media (prefers-color-scheme: dark) {
  body {
    background-color: #1a202c;
    color: #e2e8f0;
  }
  
  .module {
    background-color: #2d3748;
    border-color: #4a5568;
  }
  
  .nav-tabs > li > a {
    background-color: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;
  }
}
```

### 2. Responsividade Mobile

```css
/* Melhorias para dispositivos móveis */
@media (max-width: 768px) {
  .hero-section {
    padding: 30px 0;
    text-align: center;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .dataset-item {
    margin-bottom: 15px;
  }
  
  .navbar-nav {
    margin-top: 10px;
  }
}
```

## Workflow de Desenvolvimento

### 1. Desenvolvimento Local

```bash
# Faça suas alterações nos arquivos CSS/templates
# Os arquivos são montados como volume, então as mudanças são refletidas imediatamente

# Para mudanças em Python (plugin.py), reinicie o container
docker compose -f docker-compose.dev.yml restart ckan-dev

# Para mudanças em CSS/templates, apenas recarregue a página
```

### 2. Testando Alterações

```bash
# Acesse o CKAN em desenvolvimento
http://localhost:5000
```

### 3. Versionamento

```bash
# Commit suas alterações
git add .
git commit -m "feat: adiciona customização do header e hero section"

# Crie branch para features específicas
git checkout -b feature/dark-theme
```

## Referências e Documentação

- [CKAN Theming Guide](https://docs.ckan.org/en/latest/theming/index.html)
- [CKAN Templates and Template Inheritance](https://docs.ckan.org/en/latest/theming/templates.html)
- [CKAN Static Files](https://docs.ckan.org/en/latest/theming/static-files.html)
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)
- [Bootstrap 3 Documentation](https://getbootstrap.com/docs/3.4/)

## Troubleshooting

### CSS não está sendo carregado
- Verifique se o arquivo está registrado corretamente no plugin
- Confirme que o caminho do arquivo está correto
- Limpe o cache do browser (Ctrl+F5)

### Templates não estão sendo aplicados
- Verifique a sintaxe do Jinja2
- Confirme que `{% ckan_extends %}` está no topo do arquivo
- Reinicie o container após mudanças no plugin.py

### Mudanças não aparecem
- Para CSS/Templates: recarregue a página
- Para Python: reinicie o container
- Verifique logs: `sudo docker-compose logs ckan-dev`

## Contribuindo

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-customizacao`)
3. Push para a branch (`git push origin feature/nova-customizacao`)
4. Abra um Pull Request

