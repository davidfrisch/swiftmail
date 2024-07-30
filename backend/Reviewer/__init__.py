import json
import os
from typing import List
from LLM.OllamaLLM import OllamaAI

class Reviewer():

    def __init__(self, ollama_client, source_questions):
        if isinstance(source_questions, str) and os.path.exists(source_questions):
            with open(source_questions, 'r') as f:
                output = json.load(f)
        
        if output is None:
            raise ValueError("Questions not found")
          
      
        self.model: OllamaAI = ollama_client
        self.questions = output['extracted_questions']
        self.answers = output['answers']
        self.draft_email = output['generated_draft_email']
        
        
        
    def evaluate(self):
        self.evaluate_answers( self.answers)
        self.evaluate_draft_email(self.draft_email, self.answers)
    
      
    def evaluate_answers(self, answers):
        for answer in answers:
            question_text = answer['full_question']
            answer_text = answer['answer']
            pre_prompt = f"""
                From this question:
                Question: {question_text}
                Does the following answers the question?
                Answer: {answer_text}
            """
            sources = answer['sources']
            bin_scores = self.binary_eval(pre_prompt, ["Answer of the question"])
            linkert_score = self.linkert_eval(pre_prompt)
            hallucination_score = self.hallucination_eval(answer, sources)
    
            print({ 'binary_scores' : bin_scores, 'linkert' : linkert_score, 'hallucination' : hallucination_score})
            return { 'binary_scores' : bin_scores, 'linkert' : linkert_score, 'hallucination' : hallucination_score}
          
          
    def evaluate_draft_email(self, response_email, answers):
        all_sources = [source for answer in answers for source in answer['sources']]
        bin_score = self.binary_eval(response_email, ["sayutation", "closing", "signature"])
        linkert_score = self.linkert_eval(response_email)
        draft_score = self.hallucination_eval(response_email, all_sources)
        print({ 'binary' : bin_score, 'linkert' : linkert_score, 'hallucination' : draft_score})
        return { 'binary' : bin_score, 'linkert' : linkert_score, 'hallucination' : draft_score}

    
    def binary_eval(self, prompt:str, format_conditions: List[str]):
        counter = 0
        while counter < 3:
            try:
                prompt = prompt + f"""
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
                prompt = prompt +  """
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