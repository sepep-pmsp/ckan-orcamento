import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model

class SeplanPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers) 
   
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
        }


# Funções helper para grupos
def get_featured_groups(limit=6):
    """
    Buscar grupos em destaque para exibir na homepage
    
    Args:
        limit (int): Número máximo de grupos a retornar
        
    Returns:
        list: Lista de grupos com metadados
    """
    try:
        # Buscar grupos ativos ordenados por número de datasets
        groups = toolkit.get_action('group_list')(
            data_dict={
                'all_fields': True,
                'include_extras': True,
                'include_dataset_count': True,
                'sort': 'package_count desc'
            }
        )
        
        # Filtrar apenas grupos com imagens ou datasets
        featured_groups = []
        for group in groups:
            # Priorizar grupos com imagem ou com mais de 0 datasets
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
    """
    Buscar todos os grupos que têm imagens
    
    Returns:
        list: Lista de grupos que possuem imagens
    """
    try:
        groups = toolkit.get_action('group_list')(
            data_dict={
                'all_fields': True,
                'include_extras': True,
                'include_dataset_count': True
            }
        )
        
        # Filtrar apenas grupos com imagens
        groups_with_images = [
            group for group in groups 
            if group.get('image_display_url')
        ]
        
        # Ordenar por nome
        groups_with_images.sort(key=lambda x: x.get('display_name', x.get('name', '')))
        
        return groups_with_images
        
    except Exception as e:
        import logging
        log = logging.getLogger(__name__)
        log.error(f"Erro ao buscar grupos com imagens: {e}")
        return []