import streamlit as st
import pickle
import numpy as np

##pages configure
st.set_page_config(page_title='House Price Predictor',page_icon='^',layout='centered')

##custom css
st.markdown("""
<style>
    .main{
 background-color:#f5f7fa;
    }
    .title{
text-align:center;
font-size:40px;
color:#2c3e50
    }
    .card{
padding:20px;
border-radius:15px;
background-color:white;
box-shadow:0px 0px 10px rgba(0,0,0,0.1)
    }
</style>

""",unsafe_allow_html=True)

##load model
model=pickle.load(open('model.pkl','rb'))

##title
st.markdown("<p class='title'>^ House Price Prediction</p>",unsafe_allow_html=True)

st.markdown("### Enter Property details")

##card container
with st.container():
    st.markdown('<div class="card">',unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        area=st.number_input("Area (sq ft)",value=1000)
        bedrooms=st.number_input("Bedrooms",value=2)
        bathrooms=st.number_input("Bathrooms",value=2)
        floors=st.number_input("floors",value=1)
    with col2:
        year=st.number_input("year built",value=2010)
        condition=st.slider("* codition(1-4)",1,4,3)
        garage=st.selectbox("Garage",["No","Yes"])
        location=st.selectbox("Location",["Rular","Suburban","Urban"])
        
st.markdown("</div",unsafe_allow_html=True)

## preprocessing 
garage=1 if garage=="Yes" else 0
age=2024-year

rular=suburban=urban=0

if location=="Rular":
    rular=1
elif location=="Suburban":
    suburban=1
else:
    urban=1

features=[area,bedrooms,bathrooms,floors,year,condition,garage,rular,suburban,urban,age]

##predict button
if st.button("predict price",use_container_width=True):
 features=[area,bedrooms,bathrooms,floors,year,condition,garage,rular,suburban,urban,age]
st.write(features)

final=np.array([features])
pred=model.predict(final)



st.markdown(f"""
<div
    style='background-color:#27ae60;padding:20px;border-radius:10px;text-align:center;'>
    <h2 style='color:white;'> Estimated Price</h2>
    <h1 style='color':white;'>{int(pred[0]):,}</h1>
    </div>
""",unsafe_allow_html=True)