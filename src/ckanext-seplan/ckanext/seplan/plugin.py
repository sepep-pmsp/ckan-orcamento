import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
import logging

log = logging.getLogger(__name__)

class SeplanPlugin(plugins.SingletonPlugin):
    """
    Plugin customizado para o portal CKAN da Seplan.
    
    Este plugin implementa diversas interfaces do CKAN para:
    - Adicionar templates e diretórios públicos customizados (IConfigurer).
    - Registrar funções Python para serem usadas nos templates (ITemplateHelpers).
    - Modificar o processo de indexação para criar facetas customizadas (IPackageController).
    - Customizar os filtros de faceta exibidos nas páginas de busca (IFacets).
    """
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True) 
    plugins.implements(plugins.IFacets)

    # --- IConfigurer ---
    def update_config(self, config_):
        """
        Adiciona os diretórios de templates e recursos públicos da extensão
        à configuração do CKAN, permitindo a sobrescrita de templates e o
        uso de arquivos estáticos (CSS, JS, imagens) customizados.
        """
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "seplan")
    
    # --- ITemplateHelpers ---
    def get_helpers(self):
        """
        Registra funções Python como 'template helpers', permitindo que
        sejam chamadas diretamente dos arquivos de template Jinja2 (HTML).
        
        Isso permite que os templates executem lógica de backend complexa,
        como buscar listas de grupos ou organizações em destaque.
        """
        return {
            'get_featured_groups': get_featured_groups,
            'get_all_groups_with_images': get_all_groups_with_images,
            'get_featured_organizations': get_featured_organizations, 
        }
        
    # --- IPackageController ---
    def before_dataset_index(self, pkg_dict: dict) -> dict:
        """
        Executado imediatamente antes de um dataset ser enviado ao Solr para indexação.

        Esta função é o núcleo da faceta de 'Períodos'. Ela busca o
        dicionário completo do dataset para acessar seus recursos, itera sobre
        cada recurso para coletar os valores do campo 'res_extra_periodo',
        e adiciona uma nova chave ('res_extra_periodo') ao dicionário principal
        do dataset. Isso "promove" um metadado de nível de recurso para o nível
        de dataset, tornando-o disponível para busca facetada no Solr.
        """
        log.debug("--- DEBUG: Executando before_dataset_index para o dataset: %s ---", pkg_dict.get('name'))
        try:
            full_pkg_dict = toolkit.get_action('package_show')(
                data_dict={'id': pkg_dict['id']}
            )
            resources = full_pkg_dict.get('resources', [])
        except toolkit.ObjectNotFound:
            resources = []
            log.warning("Dataset %s não encontrado durante o before_dataset_index.", pkg_dict.get('id'))

        periodo_values = []
        for resource in resources:
            value = resource.get('res_extra_periodo')
            if value and value not in periodo_values:
                periodo_values.append(value)
        
        if periodo_values:
            pkg_dict['res_extra_periodo'] = periodo_values
        
        return pkg_dict
    
    # --- IFacets ---
    def dataset_facets(self, facets_dict, package_type):
        """
        Customiza os títulos das facetas na página de busca principal de datasets.
        
        Este dicionário mapeia o nome do campo no Solr (chave) para o título
        que será exibido ao usuário (valor).
        """
        facets_dict.update({
            'organization': 'Organizações',
            'groups': 'Grupos',
            'tags': 'Etiquetas',
            'res_format': 'Formatos',
            'license_id': 'Licenças',
            'res_extra_periodo': 'Períodos'
        })
        return facets_dict
        
    def group_facets(self, facets_dict, group_type, package_type):
        """Customiza as facetas exibidas na página de um grupo específico."""
        facets_dict.update({
            'organization': 'Organizações',
            'tags': 'Etiquetas',
            'res_format': 'Formatos',
            'license_id': 'Licenças',
            'res_extra_periodo': 'Períodos'
        })
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        """Customiza as facetas exibidas na página de uma organização específica."""
        facets_dict.update({
            'groups': 'Grupos',
            'tags': 'Etiquetas', 
            'res_format': 'Formatos',
            'license_id': 'Licenças',
            'res_extra_periodo': 'Períodos'
        })
        return facets_dict

# --- Funções Helper ---
def get_featured_groups(limit=6):
    """
    Busca e retorna uma lista de grupos para exibição em destaque.

    A função prioriza grupos que possuem uma imagem de exibição ou que
    tenham pelo menos um dataset, ordenando pelo maior número de datasets.

    Args:
        limit (int): O número máximo de grupos a serem retornados.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um grupo.
    """
    try:
        groups = toolkit.get_action('group_list')(
            data_dict={'all_fields': True, 'include_dataset_count': True, 'sort': 'package_count desc'}
        )
        featured_groups = [g for g in groups if g.get('image_display_url') or g.get('package_count', 0) > 0]
        return featured_groups[:limit]
    except Exception as e:
        log.error(f"Erro ao buscar grupos em destaque: {e}")
        return []

def get_all_groups_with_images():
    """
    Busca e retorna todos os grupos que possuem uma imagem de exibição.

    A lista é ordenada alfabeticamente pelo nome de exibição do grupo.

    Returns:
        list: Uma lista de dicionários de grupos que contêm uma imagem.
    """
    try:
        groups = toolkit.get_action('group_list')(data_dict={'all_fields': True})
        groups_with_images = [g for g in groups if g.get('image_display_url')]
        groups_with_images.sort(key=lambda x: x.get('display_name', x.get('name', '')))
        return groups_with_images
    except Exception as e:
        log.error(f"Erro ao buscar grupos com imagens: {e}")
        return []

def get_featured_organizations(limit=6):
    """
    Busca e retorna uma lista de organizações para exibição em destaque.
    
    A função prioriza organizações que possuem uma imagem de exibição ou que
    tenham pelo menos um dataset, ordenando pelo maior número de datasets.
    
    Args:
        limit (int): Número máximo de organizações a retornar.
        
    Returns:
        list: Lista de dicionários, onde cada dicionário representa uma organização.
    """
    try:
        organizations = toolkit.get_action('organization_list')(
            data_dict={'all_fields': True, 'include_dataset_count': True, 'sort': 'package_count desc'}
        )
        featured_organizations = [org for org in organizations if org.get('image_display_url') or org.get('package_count', 0) > 0]
        return featured_organizations[:limit]
    except Exception as e:
        log.error(f"Erro ao buscar organizações em destaque: {e}")
        return []