from ..lib.logger import configure_logger

LOGGER = configure_logger(__name__)
CONFIG_PATH_EMBER_APPS = 'config/environment.js'
CONFIG_PATH_EMBER_ADDONS = 'tests/dummy/config/environment.js'

mapping_web_apps_repos_to_urls = {
    #https://github.com/ConnectedHomes/bg-gaq-and-checkout/blob/master/config/environment.js#L5
    'bg-gaq-and-checkout': 'GetAQuote',
    #need to land on a page with this format TODO: refactor that (repo witll disappear anyway)
    'ember-home-services': 'apps/home-services/product-catalog/HC1',
    #need to use right rootUrl in config - repo is disappearing anyway
    'home-move': 'discover/home-move',
    #using ROOT_URL env. var
    'ev-charger': 'evpartnership',
    #https://github.com/ConnectedHomes/home-insurance/blob/master/config/environment.js#L14
    #https://centricadigital.slack.com/archives/CGBU97483/p1611668627064300?thread_ts=1611658341.059200&cid=CGBU97483
    'home-insurance': 'home-services/insurance/home-insurance',
    #https://github.com/ConnectedHomes/ember-on-demand/blob/master/config/environment.js#L11
    #https://centricadigital.slack.com/archives/CGBU97483/p1611668627064300?thread_ts=1611658341.059200&cid=CGBU97483
    'ember-on-demand': 'apps/boilers-and-heating'
}

def fetch_root_url(github_full_repo_name, repo_name, github, commit_id):
    '''compute root_url prefix'''
    root_url = ''
    try:
        root_url = mapping_web_apps_repos_to_urls.get(repo_name)
        if not root_url:
            config_path_ember = None
            is_an_ember_addon = ('ukh-web-addon' in repo_name) or ('ukh-web-engine' in repo_name)
            is_an_ember_app = 'ukh-web-app' in repo_name
            if (not is_an_ember_addon) and (not is_an_ember_app):
                ember_cli_build_content = github.get_file_content(
                    github_full_repo_name, commit_id, 'ember-cli-build.js'
                ) or ''
                if 'EmberApp' in ember_cli_build_content:
                    is_an_ember_app = True
                    LOGGER.info('is_an_ember_app True')
                if 'EmberAddon' in ember_cli_build_content:
                    is_an_ember_addon = True
                    LOGGER.info('is_an_ember_addon True')
            if is_an_ember_app:
                config_path_ember = CONFIG_PATH_EMBER_APPS
            elif is_an_ember_addon:
                config_path_ember = CONFIG_PATH_EMBER_ADDONS
            if config_path_ember:
                config_content = github.get_file_content(github_full_repo_name, commit_id, config_path_ember)
                root_url_st_split = config_content[config_content.find('rootURL:'):].split("'")
                if len(root_url_st_split) > 1:
                    root_url_st = root_url_st_split[1]
                    '''remove trailing and final "/"'''
                    root_url = root_url_st[1:len(root_url_st)-1]
            if not root_url:
                root_url = repo_name
    except:
        LOGGER.error('>>> error in trying to run mapping_web_apps_repos_to_urls', exc_info=True)

    return root_url or ''
