from typing import List
import json_tricks as json
import json as simplejson
import sys
import os
from typing import List
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import NO_ANSWERS_TEMPLATE, WORKSPACE_CATEGORIES as categories
from LLM.OllamaLLM import OllamaAI
from LLM.AnythingLLM_client import AnythingLLMClient
from database.schemas import Email, ExtractResult, AnswerResult, AnswerResultCreate
from datetime import datetime

class Generater:
    def __init__(self, ollama_client:OllamaAI= None, anyllm_client:AnythingLLMClient = None):
        
        self.olllama_client = ollama_client
        self.anyllm_client = anyllm_client
        self.questions = []
        self.answers = []
        self.generated_draft_email = ""
        

    def single_run_reply_to_email(self, email: Email, path_output:str=None):
        with open(path_output, 'w') as f:
            json.dump({}, f)

        workspace_slug = self.anyllm_client.get_workspace_slug("General")
        new_thread = self.anyllm_client.new_thread(workspace_slug, "test123")
        thread_slug = new_thread['slug']
                
        extract_questions = self.extract_questions_from_text(email.body)
        self.dump_intermediate({'extracted_questions': extract_questions}, path_output)
        
        extract_questions = [ExtractResult(
              job_id=-1,
              question_text=question['question_text'],
              category=question['category'],
              is_answered=False,
              problem_context=question['problem_context'] if 'problem_context' in question else "",
              extract_text=question['extract_text'],
              id=i,
              extracted_at=datetime.now()
           ) for i, question in enumerate(extract_questions)
        ]
        answers = self.answer_questions(email, extract_questions, thread_slug)
        self.dump_intermediate({'answers': answers}, path_output)
        
        answers_results: List[AnswerResult] = []
        for answer in answers:
            find_extract_result = next((x for x in extract_questions if x.question_text == answer['question']), None)
            if find_extract_result:
                answer_result = AnswerResultCreate(
                    extract_result_id=find_extract_result.id,
                    job_id=-1,
                    answer_text = answer['answer'],
                    sources = json.dumps(answer['sources']),
                    answered_at = datetime.now()
                )
                
                answers_results.append(answer_result)
        generated_draft_email = self.generate_response_email(email, extract_questions,  answers_results)
        self.dump_intermediate({'generated_draft_email': generated_draft_email}, path_output)
        
        return {
            'email': email,
            'extracted_questions': extract_questions,
            'generated_answers': answers_results,
            'generated_draft_email': generated_draft_email
        }
    
    
    def extract_questions_from_text(self, text:str) -> List[str]:
        prompt = f"""
          Extract the questions from the following email:
          Email:
          {text}
          
          For each question, provide the question asked and the category of the question.
          Possible categories are: {''.join([f'{category} ' for category in categories])}.
          
          Give it in a json format:
          questions: [ question ]
          question = { { 
            'extract_text': 'What is the extract text from the email?',
            'question_text': 'What is the question?',
            'category': 'What is the category of the question?',
            'problem_context': 'Explain what is the problem from the student',
          } }

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
      


    def answer_questions(self, email: Email, questions: List[ExtractResult], slug_thread=None):
        self.answers = []
        for question in questions:
            full_question = question.question_text
            category = question.category
          
            full_question = question.question_text  
            answer, unique_sources, sources = self.answer_question(
              email_text=email.body,
              question=question.question_text,
              feedback="",
              slug_thread=slug_thread,
              category=category,
            )
            
            self.answers.append({
                'question': question.question_text,
                'full_question': full_question,
                'answer': answer,
                'sources': sources,
                'unique_sources': unique_sources
            })
            
        return self.answers



    def answer_question(self, email_text, question:str, feedback:str, category="general", has_additional_context=False, slug_thread=None):
        prompt = f"""
          email: {email_text} \n
          category: {category}
          ---
          Answer the following question: \n
          Question: {question} \n
          {("Additional information:\n"+ feedback) if feedback else ""}
        """
        slug_workspace = self.anyllm_client.get_workspace_slug("General")
        
        if slug_thread:
            res = self.anyllm_client.chat_with_thread(slug_workspace, slug_thread, prompt)
        else:
            res = self.anyllm_client.chat_with_workspace(slug_workspace, prompt)
            
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
        unique_sources = list(set(chunk_sources))
      
        print(f"Total Sim Distance: {total_sim_distance}")
        return answer, unique_sources, sources
      
      


    def generate_response_email(self, original_email: Email, questions: List[ExtractResult], answers: List[AnswerResult], additional_context="") -> str:
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
        
        {("Additional information:"+ additional_context) if additional_context else ""}
        """
        
        generated_email = self.olllama_client.predict(prompt)
        self.generated_draft_email = generated_email
        
        return generated_email
        
      
    def response_to_markdown(self, output_path):
      response_email = self.generated_draft_email
      with open(output_path, 'w') as f:
          f.write(response_email)
          
    def dump_response(self, path_output:str, email: Email, questions: List[ExtractResult], answers: List[AnswerResult], generated_draft_email:str):
        with open(path_output, 'w') as f:
            json.dump({
                'email': email.model_dump(),
                'questions': [question.model_copy() for question in questions],
                'answers': [answer.model_dump() for answer in answers],
                'generated_draft_email': generated_draft_email
            }, f)
            
    def dump_intermediate(self, new_data: dict, path_output):
        with open(path_output, 'r') as f:
            data = json.load(f)
        
        old_data = data.copy()  
        try:
            data.update(new_data)
            with open(path_output, 'w') as f:
                json.dump(data, f)
        except:
            with open(path_output, 'w') as f:
                json.dump(old_data, f)
                raise Exception("Failed to write to file")