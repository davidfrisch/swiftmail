from constants import NO_ANSWERS_TEMPLATE

def answer_question(model, question:str, category="general"):
        
    res = model.chat_with_workspace(category, question)
    answer = res['textResponse']
    sources = res['sources']
    
    if len(sources) == 0:
        print(f"No sources found for question: {question}")
        return "WARNING: No answer found for this question. Here is a generic response:\n\n" + NO_ANSWERS_TEMPLATE.get(category)
      
    total_score = sum([source['score'] if 'score' in source else 0 for source in sources]) / len(sources)
    total_sim_distance = sum([source['_distance'] if '_distance' in source else 0 for source in sources]) / len(sources)
    chunk_sources = [source['chunkSource'].replace("link://", "") for source in sources if 'chunkSource' in source]
    unique_chunk_sources = list(set(chunk_sources))
    print(f"Unique chunk sources: {unique_chunk_sources}")
    print(f"Total Score: {total_score}")
    print(f"Total Sim Distance: {total_sim_distance}")
    return answer