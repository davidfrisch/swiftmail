from typing import List
import json
from .constants import NO_ANSWERS_TEMPLATE, WORKSPACE_CATEGORIES as categories
from .utils import get_workspace_slug


class Generater:
    def __init__(self, ollama_client=None, anyllm_client=None):
        if ollama_client is None and anyllm_client is None:
            raise Exception("At least one client should be provided")
        self.olllama_client = ollama_client
        self.anyllm_client = anyllm_client
        self.questions = []
        self.answers = []
        self.generated_draft_email = ""
        

    def reply_to_email(self, email:str, with_interaction:bool=False):
        ollama_client = self.models['ollama_client']
        anyllm_client = self.models['anyllm_client']
        self.extract_questions_from_text(ollama_client, email)
        self.answer_questions(anyllm_client, self.questions, with_interaction)
        self.generate_response_email(ollama_client, email, self.answers)
        self.response_to_markdown()
    

    def extract_questions_from_text(self, text:str) -> List[str]:
        prompt = f"""
          Extract the questions from the following email:
          Email:
          {text}
          
          For each question, provide the question asked and the category of the question.
          Possible categories are: {''.join([f'{category} ' for category in categories])}.
          
          Give it in a json format:
          questions: [ question ]
          question = { { 'question': 'question', 'category': 'category', 'summary': 'summary' } }

        """
        
        count_retries = 0
        self.questions = []
        
        while count_retries < 3:
            try:
                res = self.olllama_client.predict(prompt, format="json")
                res_json = json.loads(res)
                questions = res_json['questions']
                if len(questions) == 0:
                    raise Exception("No questions extracted")
                self.questions = questions
                return questions
            except:
                print("Failed to extract questions from text. Retrying...")
                count_retries += 1
                
        raise Exception("Failed to extract questions from text")


    def answer_questions(self, model, questions, with_interaction=False):
        self.answers = []
        for question in questions:
            question_text = question['question']
            additional_context = question.get('additional_context', "")
            category = question['category']
            summary = question['summary']
          
            if not with_interaction:
                question_text = question['question'] + "--- \n Additional context: "+ additional_context +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
                answer, sources, total_sim_distance = self.answer_question(model, question_text, summary, category, False)
            
            else:
                tries = 0
                while tries < 3:
                    question_text = question['question'] + "--- \n Additional context: "+ additional_context +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
                    has_additional_context = True if additional_context != "" else False
                    answer, sources, total_sim_distance = self.answer_question(model, question_text, summary, category, has_additional_context)
                    print("-----------------")
                    print("Question: ", question_text)
                    print("Answer: \n ", answer)
                    print("-----------------")
                    print(f"Are you satisfied with the answer? tries: {tries}")
                    response = input()
                    if response.strip() in ['yes', 'Yes', 'YES', 'y', 'Y']:
                        break
                    else:
                        tries += 1
                        question['additional_context'] = additional_context + "\n" + response
            
            
            
            self.answers.append({
                'question': question_text,
                'answer': answer,
                'sources': sources,
                'total_sim_distance': total_sim_distance
            })
            
        return self.answers



    def answer_question(self, model, question:str, summary: str, category="general", has_additional_context=False):
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
      
        print(f"Total Sim Distance: {total_sim_distance}")
        return answer, sources, total_sim_distance
      
      


    def generate_response_email(self, model, original_email, questions):
        program_administrator_name = "David"
        program_name = "UCL Software Engineering MSc"
        
        
        questions_answers = []
        
        for question in questions:
            question_text = question['question']
            answer_text = question['answer']
            questions_answers.append(f"Question: {question_text}\nAnswer: {answer_text} \n-------\n")
        
        prompt = f"""
        You are {program_administrator_name}, the program administrator for the {program_name} program.
        You have received an email from a student asking the following questions:
        {original_email}
        
        Here are the questions that the student asked with the answers:
        {''.join(questions_answers)}
        
        Reply to the student's email with the answers to their questions.
        Keep the ** that highlight the answers.
        """
        
        generated_email = model.predict(prompt)
        self.generated_draft_email = generated_email
        
        
    def response_to_markdown(self, output_path="./outputs/response.md"):
      response_email = self.generated_draft_email
      with open(output_path, 'w') as f:
          f.write(response_email)