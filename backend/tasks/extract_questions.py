from typing import List
import json

categories = [
  "Applications",
  "Entry requirements",
  "Application fees",
  "References for application",
  "Updating your application",
  "Application status",
  "Offers of admission",
  "Tuition fees",
  "Student visas",
  "Others"
]

def extract_questions_from_text(model, text:str) -> List[str]:
    prompt = f"""
      Extract all questions from the following email:
      Email:
      {text}
      
      For each question, provide the question asked and the category of the question.
      Possible categories are: {''.join([f'{category} ' for category in categories])}.
      
      Give it in a json format:
      questions: [ question ]
      question = { { 'question': 'question', 'category': 'category' } }

    """
    
    count_retries = 0
    
    while count_retries < 3:
        try:
            res = model.predict(prompt, format="json")
            res_json = json.loads(res)
            print(res_json)
            questions = res_json['questions']
            if len(questions) == 0:
                raise Exception("No questions extracted")
            return questions
        except:
            print("Failed to extract questions from text. Retrying...")
            count_retries += 1
            
    raise Exception("Failed to extract questions from text")