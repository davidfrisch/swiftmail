
def answer_question(model, question:str, category="general"):
        
    res = model.chat_with_workspace(category, question)
    answer = res['textResponse']
    sources = res['sources']
    
    total_score = sum([source['score'] for source in sources]) / len(sources)
    total_sim_distance = sum([source['_distance'] for source in sources]) / len(sources)
    
    print(f"Total Score: {total_score}")
    print(f"Total Sim Distance: {total_sim_distance}")
    return answer