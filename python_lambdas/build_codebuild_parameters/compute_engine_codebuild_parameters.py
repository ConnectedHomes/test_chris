from ..lib.parameters import Parameters
from .compute_codebuild_parameters import compute as compute_codebuild_parameters

parameters = Parameters()

shared_addons_list = [
    'ukh-web-addon-parent-dependencies',
    'ukh-web-addon-child-dependencies'
]

'''Builds env variables to be used in codebuild jobs'''
def compute(event, engine_repo_name, package_json_head):
    full_engine_version_head = package_json_head['devDependencies'][engine_repo_name]
    source_version = full_engine_version_head.lower().replace(
        f'github:connectedhomes/{engine_repo_name}#',
        ''
    )
    # "COMMIT_ID" and "root_url" env vars won't be useful there -
    # and probably not "_projectname" either btw
    # TODO: make them optionals in ngw-codebuild-utils
    codebuild_engine_parameters = compute_codebuild_parameters(event, True)
    env_vars = codebuild_engine_parameters['EnvironmentVariablesOverride']
    for addon_name in shared_addons_list:
        addon_version_head = package_json_head['devDependencies'][addon_name]
        addon_version_head = addon_version_head.lower().replace(
            f'github:connectedhomes/{addon_name}#',
            ''
        )
        env_vars.append({
            'Name': f'{addon_name.upper().replace("-", "_")}_VERSION',
            'Value': addon_version_head,
            'Type': 'PLAINTEXT'
        })

    return {
        "EnvironmentVariablesOverride": env_vars,
        "SourceVersion": source_version,
        'Buildspec': ''
    }
