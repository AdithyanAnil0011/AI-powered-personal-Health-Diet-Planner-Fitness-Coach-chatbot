
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
load_dotenv()


GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

#initialise session state
if 'health_profile' not in st.session_state:
    st.session_state.health_profile ={
        'goals':'to build muscles and improve endurance in 3 months',
        'conditions':'none',
        'routines':'strength training 4x/week, weekend cycling',
        'preferences':'veg/non veg,high protein,low sugar',
        'restrictions':'No fried items/limit processed sugar'
    }

def get_gemini_response(input_prompt,image_data=None):
    model=genai.GenerativeModel('gemini-2.5-flash')

    content= [input_prompt]
    
    if image_data:
         content.extend(image_data)

    try:
        response =model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response:{str(e)}"

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
            bytes_data=uploaded_file.getvalue()
            image_parts=[{
                  "mime_type":uploaded_file.type,
                  "data":bytes_data
             }]
            return image_parts
    return None

   

st.set_page_config(page_title="AI Health Companion",layout="wide")
# st.header("AI Health Profile")
st.markdown("""
<h1 style='text-align: center; color: #2E86C1;'>
🧠 AI Personal Health & Fitness Assistant
</h1>
<p style='text-align: center; font-size:18px;'>
Smart nutrition • Intelligent fitness • Personalized health insights
</p>
""", unsafe_allow_html=True)

with st.sidebar:
    #  st.subheader('Your Health Profile')
     st.sidebar.markdown("## 👤 Your Health Profile")
     st.sidebar.markdown("---")
    
    #  with st.sidebar.expander("Health Goals"):
     health_goals=st.text_area("Health Goals",
                               value=st.session_state.health_profile['goals'])
     medical_conditions=st.text_area('Medical Conditions',
                                     value=st.session_state.health_profile['conditions'])
     fitness_routines=st.text_area('Fitness Routines',
                                   value=st.session_state.health_profile['routines'])
     food_preferences=st.text_area('Food Preference',
                                   value=st.session_state.health_profile['preferences'])
     restrictions=st.text_area('Dietary Restrictions',
                               value=st.session_state.health_profile['restrictions'])
     
     
     if st.button("Update Profile"):
          st.session_state.health_profile={
               'goals':health_goals,
               'conditions':medical_conditions,
               'routines':fitness_routines,
               'preferences':food_preferences,
               'restrictions':restrictions
          }
          st.success('Profile updated !')

tab1,tab2,tab3,tab4,tab5=st.tabs(["🍴Meal Planning","📷Food Analysis","🧠Health Insights","📊Health Metrics"," 🏋️ AI Fitness Coach"])

with tab1:
    st.subheader("Personalised Meal Planning")
    col1,col2=st.columns(2)

    with col1:
     st.write("### Your Current Needs")
     user_input=st.text_area("Describe any specific requirements for your meal plans:",
                         placeholder="e.g., 'I need quick meals for work days'")
                    
    with col2:
        st.write("### Your Health Profile")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalied meal plan"):
        if not any(st.session_state.health_profile.values()):
                st.warning("Please complete your health profile in the side first")
        else:
            with st.spinner('Creating your personalised meal plan...'):
                         #construct the prompt
                prompt=f"""
                        Create a personalised meal plan based on the following health priorities
                          Health Goals:{st.session_state.health_profile['goals']} 
                          Medical Conditions:{st.session_state.health_profile['conditions']}
                          Fitness routines:{st.session_state.health_profile['routines']}
                          Food Preferences:{st.session_state.health_profile['preferences']}
                          Dietary Restrictions:{st.session_state.health_profile['restrictions']}

Additional Requirements:{user_input if user_input else "None"}

Provide:
1. A 7 day meal plan with breakfast,lunch,dinner and snacks
2.Nutritional breakdown eachday
3.Contextual explanation why each meal was chosen
4.Shopping list organised by category
5.Preparation tips and time saving suggestions

Format the output clearly with heading and bullet points.
"""
                response=get_gemini_response(prompt)
                st.subheader("Your personalised meal plan")
                st.markdown(response)

                st.download_button(
                    label="Download Meal Plan",
                    data=response,
                    file_name="Personalised_meal_plan.txt",
                    mime="text/plain"
                     )
                   
with tab2:
 st.subheader("Food Analysis")
 uploaded_file=st.file_uploader("Upload an image of your food",
                                                 type=['jpg','jpeg','png'])
 if uploaded_file is not None:
    image=Image.open(uploaded_file)
    st.image(image,caption="Uploaded Food Image.",use_column_width=True)
    if st.button("Analyse Food"):
        with st.spinner('Analysing Food...'):
         image_data=input_image_setup(uploaded_file)
        prompt=f"""

You are an expert nutritionist.Analyse this food image.
Provide detailed information about:
-estimated calories
-macronutrient breakdown
-potential health benefits
-any concerns based on common dietary restrictions
-suggested portion sizes
If the food contains multiple items,analyse each of them separately.
"""
        response =get_gemini_response(prompt,image_data)
        st.subheader("Food analysis result")
        st.markdown(response)

with tab3:
         st.subheader('Health Insights')
         health_query=st.text_input("ask any health/nutrition-realted questions",
                                    placeholder="e.g.,'how can i improve my gut health'")
         if st.button("get expert insights"):
              if not health_query:
                   st.warning("please enter a health question")
              else:
                   with st.spinner("researching your question"):
                    prompt=f"""

you are a certified nutritionist and health expert.
provide detailed ,science -backed insights about:
{health_query}

consider the user's health profile:
{st.session_state.health_profile}

Include:
1.clear explanation of science
2.practical recommendations
3.any relevant precautions
4.suggested foods/supplements

use simple language but maintain accuracy
"""
                    response =get_gemini_response(prompt)
                    st.subheader("expert health insights")
                    st.markdown(response)

with tab4:
    st.subheader("Health Metrics and Calorie Calculator")
    st.write("Enter your details to understand your health status.")
    col1, col2=st.columns(2)

    with col1:
        height=st.number_input("Height(cm)",min_value=100,max_value=250,value=170)
        weight=st.number_input("Weight (kg)",min_value=30,max_value=200,value=70)
        age=st.number_input("Age",min_value=10,max_value=100,value=25)

    with col2:
        gender=st.selectbox("Gender",["Male","Female"])
        activity = st.selectbox(
           "Activity Level",
            [
              "Sedentary (little exercise)",
              "Lightly active",
              "Moderately active",
              "Very active",
              "Super active"
    ]
)

    calculate= st.button("Calculate health metrics",key="bmi_button")
    if calculate:
            height_m=height/100
            bmi=weight/(height_m**2)

            if bmi <18.5:
                category="Underweight"
            elif bmi <24.9:
                category="Normal weight"
            elif bmi <29.9:
                category="overweight"
            else:
                category="Obese !"

                ## for bmr calculation which help us to calculate a persons daily calorie requiments

            if gender =="Male":
                    bmr=10* weight+6.25 * height -5 * age+5
            else:
                    bmr=10*weight+6.25*height-5 *age - 161

            activity_multiplier = {
                "Sedentary (little exercise)": 1.2,
                "Lightly active": 1.375,
                "Moderately active": 1.55,
                "Very active": 1.725,
                "Super active": 1.9
                }
   
            daily_calories=bmr*activity_multiplier[activity]
            weight_loss_calories=daily_calories - 500

                # if "bmi_result" in st.session_state:

            # st.markdown("### 🧾 Result")
            # st.write(f"**BMI:**{bmi:.2f}")
            # st.write(f"**Category:**{category}")
            # st.write(f"Daily Calories Needed: {daily_calories:.0f} kcal")
            with st.container():
             st.markdown("### 🧾 Your Health Results")
             st.success(f"**BMI:** {bmi:.2f} ({category})")
             st.info(f"Daily Calories: {int(daily_calories)} kcal")

            if bmi <18.5:
                   st.success(f"Calories for Weight Gain: {daily_calories + 500:.0f} kcal/day")
                   st.info("👉 A 500 calorie surplus per day can help gain ~0.5 kg per week.")

            elif 18.5 <=bmi <25:
                  st.info("👉 Maintain current intake to keep your weight stable.") 

            elif 25<=bmi<30:
                 st.success(f"Calories for Weight Loss: {daily_calories - 500:.0f} kcal/day")
                 st.info("👉 A 500 calorie deficit per day can lead to ~0.5 kg weight loss per week.")
          
            else:
              st.success(f"Calories for Weight Loss: {daily_calories - 750:.0f} kcal/day")
              st.info("👉 Reducing 500 - 750 kcal/day supports safe weight loss.")   

              st.session_state["bmi"] = bmi
              st.session_state["bmi_category"] = category
              st.session_state["daily_calories"] = daily_calories




    with tab5:
         st.subheader("🤖 AI Fitness Coach")
         st.write("Get smart fitness and lifestyle advice based on your health profile")

         if "bmi" not in st.session_state:
          st.warning("⚠ If you have not calculated your BMI value.Please calculate your BMI in the ' Health Metrics' tab for more personalized AI advice.")



         fitness_question=st.text_area(
              "Ask your AI fitness coach",
              placeholder="e.g.,How can I lose weight faster? How to stay consistent with workouts?"
         )
         if st.button("Get Coaching Advice"):
              with st.spinner("Analysing your profile..."):
                   
                   prompt=f"""

                   You are a professional fitness coach and health expert.
                   Analyse the users profile and provide personalised coaching advice.

                   USER PROFILE:
                   BMI: {st.session_state.get("bmi", "Not calculated")}
                   BMI Category: {st.session_state.get("bmi_category", "Unknown")}
                   Daily Calorie Requirement: {st.session_state.get("daily_calories", "Unknown")} kcal

                   Health Goal: {st.session_state.health_profile['goals']}
                   Medical Conditions: {st.session_state.health_profile['conditions']}
                   Fitness Routine: {st.session_state.health_profile['routines']}
                   Food Preferences: {st.session_state.health_profile['preferences']}
                   Dietary Restrictions: {st.session_state.health_profile['restrictions']}

                   User Question:
                   {fitness_question if fitness_question else "Provide general fitness improvement advice."}

                   Provide:

                   1. Personalized fitness advice
                   2. Workout improvement suggestions
                   3. Lifestyle improvements (sleep, hydration, stress)
                   4. Nutrition tips aligned with their preferences
                   5. Motivation & consistency tips

                   Keep the response clear, practical, and encouraging.
                   """

                   response = get_gemini_response(prompt)

                   st.subheader("🏋️ Your AI Coach Says:")
                   st.markdown(response)

st.markdown("---")
st.caption("Built using Streamlit + Generative AI | AI-Powered Health Assistant")

         
         
