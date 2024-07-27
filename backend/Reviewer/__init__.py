import json
import os
from LLM.OllamaLLM import OllamaAI

class Reviewer():

    def __init__(self, ollama_client, source_questions):
        if isinstance(source_questions, str) and os.path.exists(source_questions):
            with open(source_questions, 'r') as f:
                output = json.load(f)
        
        if output is None:
            raise ValueError("Questions not found")
          
      
        self.model: OllamaAI = ollama_client
        self.questions = output['questions']
        self.draft_email = output['response_email']
        
        
        
    def evaluate(self):
        self.evaluate_answers(self.questions)
        self.evaluate_draft_email(self.draft_email, self.questions)
    
      
    def evaluate_answers(self, questions):
      
        for question in questions:
            category = question['category']
            question_text = question['question']
            answer = question['answer']
            pre_prompt = f"""
                From this question:
                Question: {question_text}
                Does the following answers the question?
                Answer: {answer}
            """
            sources = question['sources']
            bin_score = self.binary_eval(pre_prompt)
            linkert_score = self.linkert_eval(pre_prompt)
            hallucination_score = self.hallucination_eval(answer, sources)
    
            print({ 'binary' : bin_score, 'linkert' : linkert_score, 'hallucination' : hallucination_score})
          
          
    def evaluate_draft_email(self, response_email, questions):
        all_sources = [source for question in questions for source in question['sources']]
        bin_score = self.binary_eval(response_email)
        linkert_score = self.linkert_eval(response_email)
        draft_score = self.hallucination_eval(response_email, all_sources)
        print({ 'binary' : bin_score, 'linkert' : linkert_score, 'hallucination' : draft_score})

    
    def binary_eval(self, prompt:str):
        prompt = prompt + """
            Provide in a json format with a key of 'score' and a value of 0 or 1, 
            where 0 means the answer is not helpful and 
            1 means the answer is helpful and gives relevant information without asking to do more.
            ---
            schema:
            {{ "score": int }}
        """
        result = self.model.predict(prompt, format="json")
        res = json.loads(result)['score']
        return int(res)
      
    def linkert_eval(self, prompt:str):
        prompt = prompt +  """
            Provide in json format with a key of 'score' and a value of 0 to 5, where 
            1 means the answer cannot be answered,
            2 means the answer is not helpful and gives irrelevant information,
            3 means the answer is not helpful and gives irrelevant information and asks to do more,
            4 means the answer is helpful and gives relevant information but asks to do more,
            5 means the answer is helpful and gives relevant information without asking to do more.
            
            schema:
            {{ "score": int }}
        """
        result = self.model.predict(prompt, format="json")
        score = int(json.loads(result)['score'])
        return score
      
    def hallucination_eval(self, prompt:str, sources):
        retrieve_text = [source["text"].split("</document_metadata>\n\n")[1] for source in sources]
        retrieve_text = "\n".join(retrieve_text)
        retrieve_text = retrieve_text.replace("\xa0", "\n")
       
        prompt = prompt + f"""
          
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
        
        result = self.model.predict(prompt, format="json")
        res = json.loads(result)['hallucination']
        return int(res)