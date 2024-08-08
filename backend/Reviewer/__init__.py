import os 
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import json
from typing import List
from LLM.OllamaLLM import OllamaAI
from database import schemas
from time import time

class Reviewer():

    def __init__(self, ollama_client):
        self.model: OllamaAI = ollama_client
 
        
            
    def evaluate(self, questions: List[schemas.ExtractResult], answers: List[schemas.AnswerResult], draft_email: str):
        answers_scores = self.evaluate_answers(questions, answers)
        draft_score = self.evaluate_draft_email(draft_email, answers)
        
        return { 'answers_score': answers_scores, 'draft_email_score': draft_score }
    
      
    def evaluate_answers(self, questions: List[schemas.ExtractResult], answers: List[schemas.AnswerResult]):
        scores = {}
        for answer in answers:
            start_time = time()
            question: schemas.ExtractResult = next((question for question in questions if question.id == answer.extract_result_id), None)
            question_text = question.question_text
            print(question_text)
            print(answer.answer_text)
            answer_text = answer.answer_text
            
            pre_prompt = f"""
                From this question:
                Question: {question_text}
                Does the following answers the question?
                Answer: {answer_text}
            """
            if answer.sources and isinstance(answer.sources, str):
                sources = json.loads(answer.sources)
            elif answer.sources:
                sources = answer.sources 
            else:
                sources = []
            bin_scores = self.binary_eval(pre_prompt, ["Answer of the question"])
            linkert_score = self.linkert_eval(pre_prompt)
            hallucination_score = self.hallucination_eval(answer, sources)
    
            scores[answer.id] = { 'binary_scores' : bin_scores, 'linkert' : linkert_score, 'hallucination' : hallucination_score, "answer_id": answer.id, "time": time() - start_time }
            print(scores[answer.id])
        return scores
          
          
    def evaluate_draft_email(self, response_email, answers: List[schemas.AnswerResult]):
        all_sources = []
        for source in answers:
            if source.sources and isinstance(source.sources, str):
                all_sources = json.loads(source.sources)
            elif source.sources:
                all_sources = source.sources 
            else:
                all_sources = []
        
        bin_score = self.binary_eval(response_email, ["salutation", "closing", "signature"])
        linkert_score = self.linkert_eval(response_email)
        draft_score = self.hallucination_eval(response_email, all_sources)
        print({ 'binary_scores' : bin_score, 'linkert' : linkert_score, 'hallucination' : draft_score})
        return { 'binary_scores' : bin_score, 'linkert' : linkert_score, 'hallucination' : draft_score}

    
    def binary_eval(self, prompt:str, format_conditions: List[str]):
        counter = 0
        while counter < 3:
            try:
                prompt = f"""
                    {prompt}
                    Provide a score of 'useful', 'tone', and 'format' where:
                    0 means the answer is not useful, 1 means the answer is useful,
                    0 means the answer is not polite, 1 means the answer is polite,
                    0 means the answer is not well formatted, 1 means the answer is well formatted.
                    
                    To be well formatted, the answer should contain the following:
                    {" ".join(format_conditions)}
                    ---
                    format has to be in json format:
                    {{ "useful": int, "tone": int, "format": int }}
                """
                result = self.model.predict(prompt, format="json")
                res = json.loads(result)
                return res
            except Exception as e:
                print(e)
                counter += 1
                continue
    
    def linkert_eval(self, prompt:str):
        counter = 0
        while counter < 3:
            try:
                prompt ="""
                    {prompt}
                    
                    Provide in json format with a key of 'score' and a value of 0 to 5, where 
                    1 means the answer cannot be answered,
                    2 means the answer is not helpful and gives irrelevant information,
                    3 means the answer is not helpful and gives irrelevant information and asks to do more,
                    4 means the answer is helpful and gives relevant information but asks to do more,
                    5 means the answer is helpful and gives relevant information without asking to do more.
                    
                    the format has to be in json format:
                    {{ "score": int }}
                """
                result = self.model.predict(prompt, format="json")
                score = int(json.loads(result)['score'])
                return score
            except Exception as e:
                print(e)
                counter += 1
                continue
      
    def hallucination_eval(self, prompt:str, sources):
        retrieve_text = [source["text"].split("</document_metadata>\n\n")[1] for source in sources]
        retrieve_text = "\n".join(retrieve_text)
        retrieve_text = retrieve_text.replace("\xa0", "\n")
       
        total_prompt = f"""
          {prompt}
          Is the above answer only based on the context?

          -Beginning of the context--
          Context: {retrieve_text}
          -End of the context--
            
          reply in json format with a key of 'hallucination' and a value of 0 or 1, 
          where 0 means the answer is based on the context and 
          1 means the answer is not based on the context.
      
          schema: 
          {{ "hallucination": int }}
        """
        
        result = self.model.predict(total_prompt, format="json")
        res = json.loads(result)['hallucination']
        return int(res)