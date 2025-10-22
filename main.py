import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from docx import Document
from streamlit import spinner

st.set_page_config(page_title="ClassRoom AI", page_icon="🎓")
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; padding-top: 30px; color: gray; font-size: 14px;'>
    <div style='text-align: left;'><b>©Yego Senior</b></div>
    <div style='text-align: center;'><b>🏆Helping you drive good grades home🎓.</b></div>
    <div style='text-align: right;'><b>©ClassRoom AI🎓</b></div>
</div>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center; color: #2E86C1;'>ClassRoom AI🎓</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Ace your exams — Revise Like a Pro with AI</h3>", unsafe_allow_html=True)

st.write("Upload your class notes and past papers for AI-powered topic analysis, simple explanations, and smart practice questions — get your answered papers marked instantly with AI, or chat directly for explanations, help, and revision support.")
genai.configure(api_key="AIzaSyARKbi8gr-3sLsw5KOEsZMUsudHA53sxBA")
model = genai.GenerativeModel("gemini-2.5-flash")

level = st.selectbox(
    "📚 Select your education level:",
    ["-- Select Level --", "Lower Primary (Grade 1-5)", "Upper Primary (Grade 6-9)",
     "High School (Grade 10-12)", "College/University"]
)

def get_level_prompt(level):
    if "Lower Primary" in level:
        return """
        The learner is in LOWER PRIMARY (Grade 1-5 in Kenyan CBC).
        ✅ Use VERY SIMPLE English or Kiswahili-friendly explanations.
        ✅ Explain like teaching a young child.
        ✅ Use fun and relatable examples: toys, food, animals, school games, cartoons, family.
        ✅ Use very short sentences and a friendly, encouraging tone.
        ✅ Avoid complex terms or deep logic.
        """

    elif "Upper Primary" in level:
        return """
        The learner is in UPPER PRIMARY (Grade 6-9 in Kenyan CBC).
        ✅ Use simple English with slightly more structure.
        ✅ Give relatable examples from school life, hobbies, friends, simple science.
        ✅ Explain concepts step-by-step with basic logic.
        ✅ Avoid heavy jargon but introduce mildly academic terms.
        ✅ Tone should be supportive like a helpful school tutor.
        """

    elif "High School" in level:
        return """
        The learner is in HIGH SCHOOL (Grade 10-12 in Kenyan CBC, previously Form 2-4).
        ✅ Explain concepts clearly as if preparing for KCSE.
        ✅ Use relatable teenage examples (e.g., sports, daily life, technology, career dreams).
        ✅ Use moderate academic language but ensure clarity.
        ✅ Balance simplicity with exam-based depth and reasoning.
        """

    else:  # College/University
        return """
        The learner is a COLLEGE/UNIVERSITY student (Year 1-5).
        ✅ Use advanced academic and technical explanations.
        ✅ Provide structured and logical reasoning.
        ✅ You may introduce theories, formulas, frameworks, or case studies.
        ✅ Assume some level of critical thinking and curiosity.
        ✅ Tone can be professional but still clear.
        """

if level=="-- Select Level --":
    st.warning("Please select your education level to proceed!")


mode = st.radio("Choose Study Mode:", ["📄 Analyze Notes/Past Papers", "💬 Ask AI a Question","Mark My Answers"])
if mode == "📄 Analyze Notes/Past Papers" and level=="-- Select Level --":
    st.warning("Please select your education level to proceed!")

elif mode == "📄 Analyze Notes/Past Papers":
    lecture_file = st.file_uploader("📘 Upload Lecture Notes (PDF, TXT, or DOCX)", type=["pdf", "txt", "docx"])
    pastpaper_file = st.file_uploader("📄 Upload Past Papers/Exams (PDF, TXT, or DOCX)", type=["pdf", "txt", "docx"])


    def extract_text(uploaded_file):
        if uploaded_file is None:
            return ""

        # Get file type
        file_type = uploaded_file.name.split(".")[-1].lower()

        # If it's a TXT file
        if file_type == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore")

        # If it's a PDF file
        elif file_type == "pdf":
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text

        # If it's a DOCX file
        elif file_type == "docx":
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text

        else:
            return "Unsupported file type"


    def extract_study_topics(lecture_text, pastpaper_text):
       prompt = f"""
       {get_level_prompt(level)}
       You are an educational AI assistant. Compare the following documents (lecture notes and past papers) and perform the following:
    
       1. Identify the **top 5 most frequently tested or emphasized concepts** based on past papers vs lecture content.
       2. For each concept, provide a **short, simple, and student-friendly explanation**.
       3. Be concise, clear, and avoid unnecessary jargon.
       4. Format the response using the structure below:
    
       **📌 KEY CONCEPTS:**
       - List the 5 concepts clearly in bullet form.
    
       **📘 EXPLANATIONS:**
       For each key concept, provide:
       Concept Name:
       Short Explanation (2–3 sentences max).
    
       Ensure the formatting is clean and easy for students to read and revise.
       Lecture Notes:
           {lecture_text[:]}
    
           Past Paper:
           {pastpaper_text[:]}
           """

       response = model.generate_content(prompt)
       return response.text

    def simplify(lecture_text, pastpaper_text):
        prompt = f"""
        {get_level_prompt(level)}
          You are a patient tutor who explains concepts in the simplest way possible using real-life analogies, examples, and step-by-step breakdowns. Assume the learner is a slow learner.

          Using the results below, explain each concept clearly in everyday language:

          RESULTS:
          {result}

          Now, based on the context in the lecture notes and past papers, further clarify using relatable analogies:

          LECTURE NOTES:
          {lecture_text}

          PAST PAPERS:
          {pastpaper_text}

          ✅ Your task:
          1. For each concept in the results, explain it as if teaching a slow learner.
          2. Use at least one everyday analogy for each concept.
          3. Break complex concepts into smaller steps.
          4. Give an easy example a high school student can understand.
          5. Keep explanations short, friendly, and encouraging.

          📘 Format like this:

          **Concept Name:**
          🔹 Simple Explanation:
          🔹 Analogy (real-life comparison):
          🔹 Example:
          🔹 Why it matters:

          Make it feel like a supportive tutor is guiding the student gently.
          """

        response = model.generate_content(prompt)
        return response.text

    def generate_practice_questions(lecture_text, pastpaper_text):
       prompt = f"""
                {get_level_prompt(level)}
                You are an expert academic examiner and educational AI. Carefully analyze and compare the concepts that appear in BOTH the lecture notes and past papers provided below. From the overlapping or recurring concepts:
        
               ✅ Generate exactly **30 well-structured, high-quality exam-style questions**.
               ✅ Use a natural mix of question types, such as:
                  - Short-answer questions
                  - Structured/descriptive questions
                  - Calculation or problem-solving questions (ONLY if applicable to the subject)
               ✅ Include a natural progression of difficulty (a blend of easier, moderately challenging, and advanced questions), but do NOT label or categorize difficulty levels.
               ✅ Ensure conceptual coverage is broad yet focused on repeated topics.
               ✅ Questions should feel professionally set, as in a formal college/university exam.
               ✅ DO NOT include multiple-choice questions.
               ✅ DO NOT provide any answers.
        
               📘 Format your response clearly as:
        
               **📚 EXAM QUESTION SET (30 Questions):**
        
               1. ...
               2. ...
               3. ...
               ...
               30. ...
        
               ---
        
               Here are the lecture notes:
               {lecture_text[:]}
        
               Here are the past papers:
               {pastpaper_text[:]}
             """

       response = model.generate_content(prompt)
       return response.text

    if lecture_file and pastpaper_file:
           with st.spinner("🤖 AI is thinking... hang tight!"):
               st.success("✅Files received")
               st.subheader("I’m now carefully analyzing your content—this may take a few seconds. ⏳")
               lecture_text = extract_text(lecture_file)
               pastpaper_text = extract_text(pastpaper_file)
               practice_questions = generate_practice_questions(lecture_text, pastpaper_text)
               with st.spinner("🚀 Powering up your success... analyzing now!"):
                       result = extract_study_topics(lecture_text, pastpaper_text)
                       st.success("🚀 Your AI-powered revision pack is ready!🔥")
                       st.balloons()
                       st.subheader("Your personalized study guide is now ready - time to grow smarter")
                       st.write(result)

               if st.button("Simplify explanation"):
                           explanation=simplify(lecture_text, pastpaper_text)
                           st.write(explanation)
               st.download_button(
                           label="📥 Download Practice Questions",
                           data=practice_questions,
                           file_name="practice_questions.txt",
                           mime="text/plain"
                       )


    else:
        st.warning("Please upload both files in PDF, TXT, or DOCX format to continue.")
elif mode == "💬 Ask AI a Question" and level=="-- Select Level --":
    st.warning("Please select your education level to proceed!")

elif mode == "💬 Ask AI a Question":

    # Step 1: Ask for user input
    user_question = st.text_input("Ask a question:")

    # Step 2: Define the function (outside of button)
    def generate_answer(user_question):
        prompt = f"""
        {get_level_prompt(level)}
        You are an expert educational AI tutor who explains academic questions clearly and simply.
        The student asked:

        "{user_question}"

        Please respond with:
        📘 Explanation: Explain in a clear and simple way using an analogy if helpful.
        📍 Summary: Give a quick summary in 2 bullet points.
        📝 Practice Question: Provide 1 similar question for practice (without the answer).
        """

        response = model.generate_content(prompt)  # Your Gemini/OpenAI call
        return response.text  # Adjust if using OpenAI

    # Step 3: Show button and call function
    if st.button("Get Answer"):
        if user_question:
            answer = generate_answer(user_question)
            st.success(answer)
        else:
            st.warning("Please enter a question first.")
elif mode == "💬 Ask AI a Question" and level=="-- Select Level --":
    st.warning("Please select your education level to proceed!")

elif mode=="Mark My Answers":
    quiz = st.file_uploader("Upload your answered questions (PDF or TXT)", type=["pdf", "txt"])

    def answer_questions(question_file):
        prompt = f"""
            {get_level_prompt(level)}
            You are a certified examiner. I will give you:
            1. The answered exam by a student in pdf form. or Answered questions by a student in pdf form.
            Your task is to:
            ✅ Mark the student's answer objectively based on the exam standards.  
            ✅ Give a total score out of the maximum score in the question paper (default is 100 if not provided).  
            ✅ Highlight what the student did correctly and apllaud them.  
            ✅ Identify mistakes or missing key points.  
            ✅ Suggest improvements in simple language.  
            ✅ Provide a full model answer that would score 10/10.
            ⚠️ IMPORTANT: Be strict but fair. Use marking scheme principles used in standard KCSE marking or College exams.
            Exam Question paper/exam:
                    {question_file}
            Now provide your result in the following structure:
            🎯 Score: X/maximum scrore possible then convert it to percentage form
            ✅ Correct Points:
            ❌ Mistakes / Missing Points:
            📘 Suggested Improvements:
            📍 Model Answer that would score all the marks (Perfect 10/10) or basically what would be the most most suitable answer to score the highest:
                        """
        response=model.generate_content(prompt)
        return response.text


    def generating_similar_questions(question_file):
        prompt = f"""
        {get_level_prompt(level)}
        You are an expert KCSE/WAEC question generator.
        Go through the answers provided by the student in {question_file}and identify every question the student got wrong.
        Your task is to:
        ✅ Understand the core concept being tested.  
        ✅ Generate new exam-style questions that test the same concept.
        ✅ Ensure each new question has the same difficulty level as the original.
        ✅ Do NOT provide answers unless I request them separately.
        ✅ Do NOT repeat or rephrase the original question.

        """
        response = model.generate_content(prompt)
        return response.text


    def extract_text(uploaded_file):
        if uploaded_file is None:
            return ""

        # Get file type
        file_type = uploaded_file.name.split(".")[-1].lower()

        # If it's a TXT file
        if file_type == "txt":
            return uploaded_file.read().decode("utf-8", errors="ignore")

        # If it's a PDF file
        elif file_type == "pdf":
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text

        # If it's a DOCX file
        elif file_type == "docx":
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text

        else:
            return "Unsupported file type"


    if quiz:
        st.subheader("🧠 Let’s see how you performed — AI is marking your paper...")
        with spinner("⏳ Sit tight — AI is reviewing your answers. This may take a moment..."):
            question_file = extract_text(quiz)
            result=answer_questions(question_file)
            st.success("✅ Marking complete!")
            st.subheader("📊 Here’s your score and detailed feedback — let’s see how you performed!")

            st.balloons()
            st.write(result)

            similar = generating_similar_questions(question_file)
            st.download_button(
                label="📥 Download Questions Similar To Those You Got Wrong ",
                data=similar,
                file_name="similar_questions.txt",
                mime="text/plain"
            )
    else:
        st.warning("Please upload your answered questions in PDF, TXT, or DOCX format to continue.")
st.markdown("""
<div style='text-align: center; padding-top: 30px; color: gray; font-size: 14px;'>
    🛠️ Built by <b>Papa Yego🐐</b>
</div>
""", unsafe_allow_html=True)




