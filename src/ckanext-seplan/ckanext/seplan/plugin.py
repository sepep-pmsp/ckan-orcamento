import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model

class SeplanPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True) 
   
    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "seplan")
    
    # ITemplateHelpers
    def get_helpers(self):
        """Registrar funções helper customizadas"""
        return {
            'get_featured_groups': get_featured_groups,
            'get_all_groups_with_images': get_all_groups_with_images,
            'get_featured_organizations': get_featured_organizations, 
        }
        
    # IPackageController
    def before_dataset_index(self, pkg_dict: dict) -> dict:
        spatial_values = []
        for resource in pkg_dict.get('resources', []):
            value = resource.get('periodo')
            if value and value not in spatial_values:
                spatial_values.append(value)
        if spatial_values:
            pkg_dict['res_extras_periodo'] = spatial_values
        return pkg_dict
    
    def after_dataset_search(self, search_results: dict, search_params: dict) -> dict:
        search_results['facet_titles'] = {
            'organization': 'Organizações',
            'groups': 'Grupos',
            'tags': 'Etiquetas',
            'res_format': 'Formatos',
            'license_id': 'Licenças',
            'res_extras_periodo': 'Períodos'
        }
        return search_results


# Funções helper existentes para grupos
def get_featured_groups(limit=6):
    """Buscar grupos em destaque para exibir na homepage"""
    try:
        groups = toolkit.get_action('group_list')(
            data_dict={
                'all_fields': True,
                'include_extras': True,
                'include_dataset_count': True,
                'sort': 'package_count desc'
            }
        )
        
        featured_groups = []
        for group in groups:
            if group.get('image_display_url') or group.get('package_count', 0) > 0:
                featured_groups.append(group)
                
            if len(featured_groups) >= limit:
                break
        
        return featured_groups
        
    except Exception as e:
        import logging
        log = logging.getLogger(__name__)
        log.error(f"Erro ao buscar grupos em destaque: {e}")
        return []


def get_all_groups_with_images():
    """Buscar todos os grupos que têm imagens"""
    try:
        groups = toolkit.get_action('group_list')(
            data_dict={
                'all_fields': True,
                'include_extras': True,
                'include_dataset_count': True
            }
        )
        
        groups_with_images = [
            group for group in groups 
            if group.get('image_display_url')
        ]
        
        groups_with_images.sort(key=lambda x: x.get('display_name', x.get('name', '')))
        
        return groups_with_images
        
    except Exception as e:
        import logging
        log = logging.getLogger(__name__)
        log.error(f"Erro ao buscar grupos com imagens: {e}")
        return []


def get_featured_organizations(limit=6):
    """
    Buscar organizações em destaque para exibir na homepage
    
    Args:
        limit (int): Número máximo de organizações a retornar
        
    Returns:
        list: Lista de organizações com metadados
    """
    try:
        # Buscar organizações ativas ordenadas por número de datasets
        organizations = toolkit.get_action('organization_list')(
            data_dict={
                'all_fields': True,
                'include_extras': True,
                'include_dataset_count': True,
                'sort': 'package_count desc'
            }
        )
        
        # Filtrar apenas organizações com imagens ou datasets
        featured_organizations = []
        for org in organizations:
            # Priorizar organizações com imagem ou com mais de 0 datasets
            if org.get('image_display_url') or org.get('package_count', 0) > 0:
                featured_organizations.append(org)
                
            if len(featured_organizations) >= limit:
                break
        
        return featured_organizations
        
    except Exception as e:
        import logging
        log = logging.getLogger(__name__)
        log.error(f"Erro ao buscar organizações em destaque: {e}")
        return []