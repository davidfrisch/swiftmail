from AnythingLLM_client import AnythingLLMClient

def main():
    client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    print(client.check_auth_jwt())
    res = client.chat_with_workspace("lancedb", "When do I have to pay my UCL autumn term fees?")
    
  
if __name__ == '__main__':
    main()