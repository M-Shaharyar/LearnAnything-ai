from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import pandas as pd
import streamlit as st
import os

MAX_TOKENS=16000

load_dotenv()
base_url = "https://api.aimlapi.com/v1"
api_key = os.getenv("AIML_API_KEY")

system_prompt = "You are an AI tutor. Be descriptive and helpful."

api = OpenAI(api_key=api_key, base_url=base_url)

class FlashcardList(BaseModel):
    flashcards: list[(str, str)]

def get_flashcards(document, n):

    user_prompt = f"""
        Prepare {n} questions from the input document.
        Each question should be related to some important information like: fact, place, person, date, work.
        Questions should be so formulated as the answer is only one word.

        Return questions and answers in CSV format.

        __

        Output example:

        Question1, answer1
        Question2, answer2

        ---
        {document[:MAX_TOKENS-500]}
        ---
        """


    completion = api.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.01,
        max_tokens=MAX_TOKENS,
        response_format=FlashcardList,
    )

    response = completion.choices[0].message.parsed
    # st.write(response)

    def split_resp(r):
        splitted = r.split(',')
        for i, s in enumerate(splitted):
            if type(s) is not str:
                splitted[i] = str(s)

        if len(splitted) == 2:
            return splitted
        if len(splitted) == 1:
            return [splitted[0], ""]
        return "".join(splitted[:-1]), splitted[-1]


    q = [split_resp(r) for r in response.flashcards]
    #st.write(q)
    df = pd.DataFrame(q, columns=['Question', 'Answer'])
    #st.write(df)

    return df


def run_openai(prompt):

    try:
        # Sending the answer text to OpenAI API using the updated method
        completion = api.chat.completions.create(
            model="gpt-4o-2024-08-06",  # You can choose a different model as needed
            messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": prompt}
            ]
            )
        return completion.choices[0].message.content  # Display the response
    except Exception as e:
        return
        #st.write("An error occurred:", e) 



def get_question(document):

    # st.write(document)

    user_prompt = f"""
        Prepare one questions from the input document.
        The question should be related to some important information like: fact, place, person, date, work.
        Write only this question, without any introduction or explaination.
        ---
        {document}
        ---
        """

    return run_openai(user_prompt)


class Question(BaseModel):
    question: str
    information: str
    options: list[str]
    answer: str

class QuizList(BaseModel):
    quiz: list[Question]

def get_quiz(document, n):

    user_prompt = f"""
        Prepare {n} quiz questions and answers from the input document.

        Expected information for each question:

        "question": Here is your question,
        "information": This is a fragment of document, answering the question,
        "options": [Option1, Option2, Option3, Option4],
        "answer": Option2

        Format your output in JSON format.
        __

        Example output:


    
        "question": "What is the primary goal of artificial intelligence?",
        "information": "This field of computer science aims to create systems capable of performing tasks that would typically require human intelligence.",
        "options": ["To simulate human intelligence", "To enhance computer speed", "To replace human jobs", "To improve data storage"],
        "answer": "To simulate human intelligence"
    ,
    
        "question": "What is 'machine learning' in the context of artificial intelligence?",
        "information": "This is a subset of artificial intelligence that involves the creation of systems that can learn from and make decisions based on data.",
        "options": ["A new programming language", "A data processing method", "A subset of artificial intelligence", "A type of computer hardware"],
        "answer": "A subset of artificial intelligence"
    


        ---
        {document}
        ---
        """


    completion = api.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.01,
        max_tokens=16000,
        response_format=QuizList,
    )

    response = completion.choices[0].message.parsed

    return response.quiz

