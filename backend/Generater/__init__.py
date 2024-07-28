from typing import List
import json
import sys
import os
from typing import List
from constants import NO_ANSWERS_TEMPLATE, WORKSPACE_CATEGORIES as categories
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from LLM.OllamaLLM import OllamaAI
from LLM.AnythingLLM_client import AnythingLLMClient
from database.schemas import Email, ExtractResult, AnswerResult

class Generater:
    def __init__(self, ollama_client:OllamaAI= None, anyllm_client:AnythingLLMClient = None):
        
        self.olllama_client = ollama_client
        self.anyllm_client = anyllm_client
        self.questions = []
        self.answers = []
        self.generated_draft_email = ""
        

    def reply_to_email(self, email: Email, path_output:str, with_interaction:bool=False):
        self.extract_questions_from_text(email.body)
        self.answer_questions(self.questions, with_interaction)
        self.generate_response_email(email, self.answers)
        self.response_to_markdown(path_output)
    
    
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
      


    def answer_questions(self, questions: List[ExtractResult], with_interaction: bool=False):
        self.answers = []
        for question in questions:
            full_question = question.question_text
            category = question.category
            additional_context = ""
          
            if not with_interaction:
                full_question = question.question_text + "--- \n Additional context: "+ additional_context +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
                answer, sources, total_sim_distance = self.answer_question(full_question, category, False)
            
            else:
                tries = 0
                while tries < 3:
                    full_question = question.question_text + "--- \n Additional context: "+ additional_context +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
                    has_additional_context = True if additional_context != "" else False
                    answer, sources, total_sim_distance = self.answer_question(full_question, category, has_additional_context)
                    print("-----------------")
                    print("Question: ", full_question)
                    print("Answer: \n ", answer)
                    print("-----------------")
                    print(f"Are you satisfied with the answer? tries: {tries}")
                    response = input()
                    if response.strip() in ['yes', 'Yes', 'YES', 'y', 'Y']:
                        break
                    else:
                        tries += 1
                        additional_context = additional_context + "\n" + response
            
            
            
            self.answers.append({
                'question': question.question_text,
                'full_question': full_question,
                'answer': answer,
                'sources': sources,
                'total_sim_distance': total_sim_distance
            })
            
        return self.answers



    def answer_question(self, question:str, category="general", has_additional_context=False):
        prompt = f"""
          You are a Program Administrator at UCL. You only have access to the following information.
          If you don't have an answer, just say "I don't have an answer for this question".
          Answer the following question:
          Question: {question}
          Category: {category}
        """
        
        slug = self.anyllm_client.get_workspace_slug("General")
        res = self.anyllm_client.chat_with_workspace(slug, prompt)
        answer = res['textResponse']
        sources = res['sources']
        
        if len(sources) == 0 and not has_additional_context:
            print(f"No sources found for question: {question}")
            default_response = NO_ANSWERS_TEMPLATE.get(category) if category in NO_ANSWERS_TEMPLATE else NO_ANSWERS_TEMPLATE.get("general")
            answer = "WARNING: No answer found for this question. Here is a generic response:\n\n" + default_response
            return answer, [], 0
          
        if len(sources) == 0 and has_additional_context:
            res = self.anyllm_client.chat_with_workspace("others", question)
            answer = res['textResponse']
            return answer, [], 0
          
          
        total_sim_distance = sum([source['_distance'] if '_distance' in source else 0 for source in sources]) / len(sources) if len(sources) > 0 else 0
        chunk_sources = [source['chunkSource'].replace("link://", "") for source in sources if 'chunkSource' in source]
      
        print(f"Total Sim Distance: {total_sim_distance}")
        return answer, sources, total_sim_distance
      
      


    def generate_response_email(self, original_email: Email, questions: List[ExtractResult], answers: List[AnswerResult]):
        program_administrator_name = "David"
        program_name = "UCL Software Engineering MSc"
        
        
        questions_answers = []
        
        for question in questions:
            question_text = question.question_text
            answer_text = next((answer.answer_text for answer in answers if answer.extract_result_id == question.id), "I don't have an answer for this question")
            questions_answers.append(f"Question: {question_text}\nAnswer: {answer_text} \n-------\n")
        
        prompt = f"""
        You are {program_administrator_name}, the program administrator for the {program_name} program.
        You have received an email from a student asking the following questions:
        Subject: {original_email.subject}
        Body: {original_email.body}
        
        Here are the questions that the student asked with the answers:
        {''.join(questions_answers)}
        
        Reply to the student's email with the answers to their questions.
        Keep the ** that highlight the answers.
        """
        
        generated_email = self.olllama_client.predict(prompt)
        self.generated_draft_email = generated_email
        
        return generated_email
        
        
    def response_to_markdown(self, output_path):
      response_email = self.generated_draft_email
      with open(output_path, 'w') as f:
          f.write(response_email)