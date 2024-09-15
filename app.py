import streamlit as st
from io import BytesIO
from llm import get_flashcards, get_quiz
from web_search import get_content

# Streamlit app layout
st.title('LearnAnything - The Flashcard and Quiz Generator')

# Initialize session variables for document upload and web search quizzes
default_values = {
    'doc_quiz_data': [],
    'doc_quiz_started': False,
    'doc_current_index': 0,
    'doc_score': 0,
    'doc_selected_option': None,
    'doc_answer_submitted': False,
    'web_quiz_data': [],
    'web_quiz_started': False,
    'web_current_index': 0,
    'web_score': 0,
    'web_selected_option': None,
    'web_answer_submitted': False
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Sidebar for switching between functionalities
option = st.sidebar.selectbox(
    'Choose an option:',
    ('Upload Document', 'Search from Web')
)

content = None

# Reset quizzes if the user switches between "Upload Document" and "Search from Web"
if option == 'Upload Document' and st.session_state.web_quiz_started:
    st.session_state.web_quiz_started = False
    st.session_state.web_quiz_data = []
elif option == 'Search from Web' and st.session_state.doc_quiz_started:
    st.session_state.doc_quiz_started = False
    st.session_state.doc_quiz_data = []

# Upload document functionality
if option == 'Upload Document':
    st.subheader("Upload a document")
    uploaded_file = st.file_uploader("Upload a document", type=['txt', 'docx', 'pdf'])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        content = uploaded_file.getvalue()

        # Flashcard generation
        num_lines = st.number_input("Set number of flashcards", min_value=5, max_value=50, value=30)

        if st.button('Generate flashcards', key='generate_doc_flashcards'):
            st.write("Processing the content...")
            df = get_flashcards(content, num_lines)
            st.write("Content processed successfully!")
            st.dataframe(df)

            csv_file = BytesIO()
            df.to_csv(csv_file, index=False)
            csv_file.seek(0)

            st.download_button(
                label="Download CSV",
                data=csv_file,
                file_name="output.csv",
                mime="text/csv"
            )

        # Quiz generation
        if st.button('Start Document Quiz', key='start_doc_quiz'):
            st.session_state.doc_quiz_data = get_quiz(content, 15)
            st.session_state.doc_quiz_started = True
            st.session_state.doc_current_index = 0
            st.session_state.doc_score = 0
            st.session_state.doc_selected_option = None
            st.session_state.doc_answer_submitted = False

# Web search functionality
elif option == 'Search from Web':
    st.subheader("Search the web")
    query = st.text_input("Enter your idea for searching the web:")

    if query:
        try:
            content = get_content(query)
            st.success("Content retrieved successfully!")

            st.download_button(
                label="Download the content",
                data=content,
                file_name=f"{query}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"An error occurred while fetching content: {str(e)}")
            content = None

    if content is not None:
        num_lines = st.number_input("Set number of flashcards", min_value=5, max_value=50, value=30)

        if st.button('Generate flashcards', key='generate_web_flashcards'):
            st.write("Processing the content...")
            df = get_flashcards(content, num_lines)
            st.write("Content processed successfully!")
            st.dataframe(df)

            csv_file = BytesIO()
            df.to_csv(csv_file, index=False)
            csv_file.seek(0)

            st.download_button(
                label="Download CSV",
                data=csv_file,
                file_name="output.csv",
                mime="text/csv"
            )

        # Quiz generation
        if st.button('Start Web Quiz', key='start_web_quiz'):
            st.session_state.web_quiz_data = get_quiz(content, 15)
            st.session_state.web_quiz_started = True
            st.session_state.web_current_index = 0
            st.session_state.web_score = 0
            st.session_state.web_selected_option = None
            st.session_state.web_answer_submitted = False

# Functions to handle quiz operations
def submit_answer(quiz_type):
    if quiz_type == 'doc':
        selected_option = st.session_state.doc_selected_option
        quiz_data = st.session_state.doc_quiz_data
        current_index = st.session_state.doc_current_index
    else:
        selected_option = st.session_state.web_selected_option
        quiz_data = st.session_state.web_quiz_data
        current_index = st.session_state.web_current_index

    if selected_option is not None:
        if quiz_type == 'doc':
            st.session_state.doc_answer_submitted = True
            if selected_option == quiz_data[current_index].answer:
                st.session_state.doc_score += 1
        else:
            st.session_state.web_answer_submitted = True
            if selected_option == quiz_data[current_index].answer:
                st.session_state.web_score += 1

def next_question(quiz_type):
    if quiz_type == 'doc':
        if st.session_state.doc_current_index < len(st.session_state.doc_quiz_data) - 1:
            st.session_state.doc_current_index += 1
            st.session_state.doc_selected_option = None
            st.session_state.doc_answer_submitted = False
        else:
            st.write(f"Quiz completed! Your score is: {st.session_state.doc_score} / {len(st.session_state.doc_quiz_data)}")
            st.button('Restart', key='restart_doc_quiz', on_click=lambda: restart_quiz('doc'))
    else:
        if st.session_state.web_current_index < len(st.session_state.web_quiz_data) - 1:
            st.session_state.web_current_index += 1
            st.session_state.web_selected_option = None
            st.session_state.web_answer_submitted = False
        else:
            st.write(f"Quiz completed! Your score is: {st.session_state.web_score} / {len(st.session_state.web_quiz_data)}")
            st.button('Restart', key='restart_web_quiz', on_click=lambda: restart_quiz('web'))

def restart_quiz(quiz_type):
    if quiz_type == 'doc':
        st.session_state.doc_current_index = 0
        st.session_state.doc_score = 0
        st.session_state.doc_selected_option = None
        st.session_state.doc_answer_submitted = False
    else:
        st.session_state.web_current_index = 0
        st.session_state.web_score = 0
        st.session_state.web_selected_option = None
        st.session_state.web_answer_submitted = False

# Display quiz for document upload
if st.session_state.doc_quiz_started and 'doc_quiz_data' in st.session_state:
    st.header("Document Quiz")
    progress_bar_value = (st.session_state.doc_current_index + 1) / len(st.session_state.doc_quiz_data)
    st.metric(label="Score", value=f"{st.session_state.doc_score} / {len(st.session_state.doc_quiz_data)}")
    st.progress(progress_bar_value)

    question_item = st.session_state.doc_quiz_data[st.session_state.doc_current_index]
    st.subheader(f"Question {st.session_state.doc_current_index + 1}")
    st.title(f"{question_item.question}")

    st.markdown(""" ___""")

    options = question_item.options
    correct_answer = question_item.answer

    if st.session_state.doc_answer_submitted:
        for option in options:
            if option == correct_answer:
                st.success(f"{option} (Correct answer)")
            elif option == st.session_state.doc_selected_option:
                st.error(f"{option} (Incorrect answer)")
            else:
                st.write(option)
    else:
        for option in options:
            if st.button(option, key=f"doc-{option}"):
                st.session_state.doc_selected_option = option

    st.markdown(""" ___""")

    if st.session_state.doc_answer_submitted:
        if st.session_state.doc_current_index < len(st.session_state.doc_quiz_data) - 1:
            st.button('Next', key='next_doc_question', on_click=lambda: next_question('doc'))
        else:
            st.write(f"Quiz completed! Your score is: {st.session_state.doc_score} / {len(st.session_state.doc_quiz_data)}")
            st.button('Restart', key='restart_doc_quiz', on_click=lambda: restart_quiz('doc'))
    else:
        st.button('Submit', key='submit_doc_answer', on_click=lambda: submit_answer('doc'))

# Display quiz for web search
if st.session_state.web_quiz_started and 'web_quiz_data' in st.session_state:
    st.header("Web Quiz")
    progress_bar_value = (st.session_state.web_current_index + 1) / len(st.session_state.web_quiz_data)
    st.metric(label="Score", value=f"{st.session_state.web_score} / {len(st.session_state.web_quiz_data)}")
    st.progress(progress_bar_value)

    question_item = st.session_state.web_quiz_data[st.session_state.web_current_index]
    st.subheader(f"Question {st.session_state.web_current_index + 1}")
    st.title(f"{question_item.question}")

    st.markdown(""" ___""")
   
    
    options = question_item.options
    correct_answer = question_item.answer
    if st.session_state.web_selected_option is None:
        st.write("No option is selected (First click on the option after confirmation, click on submit)")
    else:
        st.write("One option is selected. Now click on Submit")

    if st.session_state.web_answer_submitted:
        for option in options:
            if option == correct_answer:
                st.success(f"{option} (Correct answer)")
            elif option == st.session_state.web_selected_option:
                st.error(f"{option} (Incorrect answer)")
            else:
                st.write(option)
    else:
        for option in options:
            if st.button(option, key=f"web-{option}"):
                st.session_state.web_selected_option = option

    st.markdown(""" ___""")

    if st.session_state.web_answer_submitted:
        if st.session_state.web_current_index < len(st.session_state.web_quiz_data) - 1:
            st.button('Next', key='next_web_question', on_click=lambda: next_question('web'))
        else:
            st.write(f"Quiz completed! Your score is: {st.session_state.web_score} / {len(st.session_state.web_quiz_data)}")
            st.button('Restart', key='restart_web_quiz', on_click=lambda: restart_quiz('web'))
    else:
        st.button('Submit', key='submit_web_answer', on_click=lambda: submit_answer('web'))
