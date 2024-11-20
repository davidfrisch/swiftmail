from typing import List
import json_tricks as json
import json as simplejson
import sys
import os
from typing import List
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
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
        

    def single_run_reply_to_email(self, email: Email, workspace_name, path_output:str=None):
        
        if path_output:
            with open(path_output, 'w') as f:
                json.dump({}, f)

        workspace_slug = self.anyllm_client.get_workspace_slug(workspace_name)
        new_thread = self.anyllm_client.new_thread(workspace_slug, "new_thread")
        thread_slug = new_thread['slug']
                
        extract_questions = self.extract_questions_from_text(email.body)
        
        path_output and self.dump_intermediate({'extracted_questions': extract_questions}, path_output)
        
        extract_questions = [ExtractResult(
              job_id=-1,
              question_text=question['extract_text'],
              is_answered=False,
              problem_context=question['problem_context'] if 'problem_context' in question else "",
              id=i,
              extracted_at=datetime.now()
           ) for i, question in enumerate(extract_questions)
        ]
        answers = self.answer_questions(email, extract_questions, thread_slug)
        path_output and self.dump_intermediate({'answers': answers}, path_output)
        
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
        path_output and self.dump_intermediate({'generated_draft_email': generated_draft_email}, path_output)
        self.anyllm_client.delete_thread(workspace_slug, thread_slug)
        return {
            'email': email,
            'extracted_questions': extract_questions,
            'generated_answers': answers_results,
            'generated_draft_email': generated_draft_email
        }
    
    
    def extract_questions_from_text(self, text:str) -> List[str]:
        prompt = f"""
          Split the full email into multiple contextual segments
          Email:
          {text.strip()}
          
          ---
          - The type can only be either a "question" or "information" or "not_information"!
          - If a question is composed of multiple sentences, keep it as one question.
           
          Give the ouptut in a json format:
          segments = [{{
            'type': question/information/not_information,
            'extract_text': 'What is the extract text from the email?',
          }}, ...]

        """
        
        count_retries = 0
        self.questions = []
        
        while count_retries < 3:
            try:
                res = self.olllama_client.predict(prompt, format="json")
                res_json = json.loads(res)
                segments = res_json['segments']
                questions = [segment for segment in segments if segment['type'] == 'question']
                all_informations = " ".join([segment['extract_text'] for segment in segments if segment['type'] == 'information'])
                
                for question in questions:
                    question['problem_context'] = "Information about the email: \n " + all_informations + "\n --- \n"
                    
                if len(questions) == 0:
                    raise Exception("No segments extracted")
                  
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
          
            full_question = question.question_text  
            answer, unique_sources, sources = self.answer_question(
              workspace_name=email.workspace_name,
              question=question.question_text,
              feedback="",
              slug_thread=slug_thread,
            )
            
            self.answers.append({
                'question': question.question_text,
                'full_question': full_question,
                'answer': answer,
                'sources': sources,
                'unique_sources': unique_sources
            })
            
        return self.answers



    def answer_question(self, workspace_name: str, question:str, feedback:str, has_additional_context=False, slug_thread=None):
        prompt = f"""
          Answer the following question: \n
          Question: {question} \n
          {("Additional information:\n"+ feedback) if feedback else ""}
        """
        slug_workspace = self.anyllm_client.get_workspace_slug(workspace_name)
        
        if slug_thread:
            res = self.anyllm_client.chat_with_thread(slug_workspace, slug_thread, prompt)
        else:
            res = self.anyllm_client.chat_with_workspace(slug_workspace, prompt)
            
        answer = res['textResponse']
        sources = res['sources']
        
        if len(sources) == 0 and not has_additional_context:
            print(f"No sources found for question: {question}")
            answer = "WARNING: No answer found for this question." 
            return answer, [], 0
          
        if len(sources) == 0 and has_additional_context:
            res = self.anyllm_client.chat_with_workspace("others", question)
            answer = res['textResponse']
            return answer, [], 0
          
        chunk_sources = [source['url'] for source in sources]
        unique_sources = list(set(chunk_sources))
      
        return answer, unique_sources, sources
      
      


    def generate_response_email(self, original_email: Email, questions: List[ExtractResult], answers: List[AnswerResult], additional_context="") -> str:
        program_administrator_name = "David"
        program_name = "UCL Software Engineering MSc"
        
        
        questions_answers = []
        
        for question in questions:
            question_text = question.question_text
            answer_text = next((answer.answer_text for answer in answers if answer.extract_result_id == question.id), "I don't have an answer for this question")
            questions_answers.append(f"Question: {question_text}\nAnswer: {answer_text} \n-------\n")
        print(questions_answers)
        prompt = f"""
        You are {program_administrator_name}, the program administrator for the {program_name} program.
        You have received an email from a student asking the following questions:
        Subject: {original_email.subject}
        Body: {original_email.body}
        
        Here are the questions that the student asked with the answers:
        {''.join(questions_answers)}
        
        ---
        Reply to the student's email with the answers to their questions.
        
        {("Additional information:"+ additional_context) if additional_context else ""}
        """
        
        generated_email = self.olllama_client.predict(prompt)
        self.generated_draft_email = generated_email
        
        return generated_email
    
    
    def regenerate_response_email(self,  original_draft, corrections):
        prompt = f"""
        {original_draft}
        
        ---
        
        Apply the following corrections:
        {corrections}
        
        """

        print(prompt)
        generated_email = self.olllama_client.predict(prompt)
        
        is_column_on_first_line = generated_email.split("\n")[0].strip().find(":")
        if is_column_on_first_line != -1:
            generated_email = "\n".join(generated_email.split("\n")[1:])
            
        self.generated_draft_email = generated_email.strip()
        return generated_email.strip()
      
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