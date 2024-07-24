

def get_workspace_slug(anythingllm_client, category):
    workspaces = anythingllm_client.get_all_workspaces()['workspaces']
    for workspace in workspaces:
        if workspace['name'] == category:
            return workspace['slug']
    return None