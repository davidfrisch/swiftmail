

    

def generate_response_email(model, original_email, questions):
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
    Keep the highlighted qualitative information in the answers.
    """
    
    generated_email = model.predict(prompt)
    return generated_email