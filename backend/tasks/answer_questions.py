from constants import NO_ANSWERS_TEMPLATE


def get_workspace_slug(anythingllm_client, category):
    workspaces = anythingllm_client.get_all_workspaces()['workspaces']
    for workspace in workspaces:
        if workspace['name'] == category:
            return workspace['slug']
    return None


def answer_question(model, question:str, summary: str, category="general", has_additional_context=False):
    prompt = f"""
      You are a Program Administrator at UCL. You only have access to the following information.
      If you don't have an answer, just say "I don't have an answer for this question".
      Answer the following question:
      Question: {question}
      Category: {category}
      Summary: {summary}
    """
    
    slug = get_workspace_slug(model, "General")
    res = model.chat_with_workspace(slug, prompt)
    answer = res['textResponse']
    sources = res['sources']
    
    if len(sources) == 0 and not has_additional_context:
        print(f"No sources found for question: {question}")
        default_response = NO_ANSWERS_TEMPLATE.get(category) if category in NO_ANSWERS_TEMPLATE else NO_ANSWERS_TEMPLATE.get("general")
        answer = "WARNING: No answer found for this question. Here is a generic response:\n\n" + default_response
        return answer, [], 0
      
    if len(sources) == 0 and has_additional_context:
        res = model.chat_with_workspace("others", question)
        answer = res['textResponse']
        return answer, [], 0
      
      
    total_sim_distance = sum([source['_distance'] if '_distance' in source else 0 for source in sources]) / len(sources) if len(sources) > 0 else 0
    chunk_sources = [source['chunkSource'].replace("link://", "") for source in sources if 'chunkSource' in source]
    unique_chunk_sources = list(set(chunk_sources)) if len(chunk_sources) > 0 else []
   
   
    print(f"Unique chunk sources: {unique_chunk_sources}")
    print(f"Total Sim Distance: {total_sim_distance}")
    return answer, unique_chunk_sources, total_sim_distance
  
  
