from datetime import datetime
from zoneinfo import ZoneInfo
import json
import requests
import os
from dotenv import  load_dotenv
from groq import Groq

load_dotenv()

client=Groq(
    api_key=os.getenv("groq_api_key")
)

# response=client.chat.completions.create(
#     model="openai/gpt-oss-20b",
#     messages=[
#         {
#             "role":"user",
#             "content":"hello,introduce yourself in one sentence."
#         }
#     ]
# )

# print(response.choices[0].message.content)

#-------- Calculaeto Tool ---------------
def calculator(a,b,operation):
    if operation=='add':
        return a+b
    elif operation=='substract':
        return a-b
    elif operation=='multiply':
        return a*b
    elif operation=="divide":
        if b==0:
            return "can not be divided"
        return a/b
    else:
        return "invalid operation"

#----------------weather agent--------------------

def get_weather(city):
    # find city coordinates
    geo_url="https://geocoding-api.open-meteo.com/v1/search"
    geo_params={
        "name":city,
        "count":1,
        "language":"en",
        "format":"json"
    }

    geo_response=requests.get(geo_url,params=geo_params)
    geo_data=geo_response.json()

    if "results" not in geo_data:
        return f"city '{city}' not found"
    location=geo_data["results"][0]
    latitude=location["latitude"]
    longitude=location["longitude"]
    city_name=location["name"]
    country=location.get("country","")

    #get current weather
    weather_url="https://api.open-meteo.com/v1/forecast"
    weather_params={
        "latitude":latitude,
        "longitude":longitude,
        "current":"temperature_2m,relative_humidity_2m,wind_speed_10m"
    }

    weather_response=requests.get(weather_url,params=weather_params)
    weather_data=weather_response.json()
    current=weather_data['current']
    temperature=current["temperature_2m"]
    humidity=current["relative_humidity_2m"]
    wind=current["wind_speed_10m"]

    return (
        f"Weather in {city_name},{country}:"
        f"temperature {temperature}°c,"
        f"Humidity {humidity}%,"
        f"wind speed{wind}km/h."
    )

#------------------Google url --------------
def get_data(question):
    url="https://google.serper.dev/search"

    headers={
        "x-Api-Key":os.getenv("SERPER_API_KEY"),
        "content_type":"application/json"

    }

    data={
        "q":question
    }

    response=requests.post(
        url,
        headers=headers,
        json=data
    )
    results=response.json().get("organic",[])

    if not results:
        results=results[:2]
        print("\nI found 2 results")

    for i in results in enumerate(results,start=1):
        print(f"{i}.{result.get("title")}")
        print(result.get("snippet",""))
        print(result.get("link"))
        print()

    choice=input("choose 1 or 2")
    if choice=="1":
        return result[0]
    elif choice=="2":
        return result[1]
    else:
        return "invalid choice"

#--------------current time -----------------------
def current_time(city):
    #find city coordinates
    geo_url="https://geocoding-api.open-meteo.com/v1/search"
    params={
        "name":city,
        "count":1,
        "language":"en",
        "format":"json"
    }
    response=requests.get(geo_url,params=params)
    data=response.json()

    if "results" not in data:
        return f"City '{city}' not found."
    location=data['results'][0]
    city_name=location['name']
    country=location.get("country","")
    timezone=location['timezone']

    print("timezone",timezone)

    current_time=datetime.now(ZoneInfo(timezone))

    return(
        f"current time in {city_name},{country}:"
        f"{current_time.strftime('%I:%M:%S:%p')}"
    )
    

#-----------Tool defination--------------
tools=[
    {
        "type":"function",
        "function":{
            "name":"calculator",
            "description":"Perform basics mathematical calculation",
            "parameters":{
                "type":"object",
                "properties":{
                    "a":{
                        "type":"number",
                        "description":"first number"
                    },
                    "b":{
                        "type":"number",
                        "description":"second number"
                    },
                    "operation": {
                        "type":"string",
                        "enum":[
                            "add",
                            "substract",
                            "multiply",
                            "divide"
                        ]
                    }
                },
                "required":["a","b","operation"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_weather",
            "description":"Get current weather information for a city",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"Name of the city"
                    }
                },
                "required":["city"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_data",
            "description":"search the web to find the information about the question.",
            "parameters":{
                "type":"object",
                "properties":{
                    "question":{
                        "type":"string",
                        "description":"the question to search the web"
                    }
                },
                "required":["question"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"current_time",
            "description":"Get the current time for a city",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"Name of the city",
                    }
                },
                "required":['city']
            }
        }
    }
]

#-------------user question-------------
user_question=input("You: ")

messages=[
    {
        "role":"user",
        "content":user_question
    }
]

#---------------- first LLm call-----------------
response=client.chat.completions.create(
     model="openai/gpt-oss-20b",
     messages=messages,
     tools=tools,
     tool_choice="auto"
)
message=response.choices[0].message

#------------------check tool calling-----------
if message.tool_calls:
    messages.append(message)

    for tool_call in message.tool_calls:
        function_name=tool_call.function.name
        arguments=json.loads(
            tool_call.function.arguments
        )

        #calculator
        if function_name == "calculator":
            result=calculator(
                arguments["a"],
                arguments["b"],
                arguments["operation"]
            )

            #weather
        elif function_name == "get_weather":
            result=get_weather(
                arguments["city"]
            )

        elif function_name=="get_data":
            result=get_data(arguments["question"])

        elif function_name == "current_time":
            result=current_time(arguments['city'])
        
        else:
            result="unknown tool"
            #send tool result back to llm
        messages.append({
            "role":"tool",
            "tool_call_id":tool_call.id,
            "content":str(result)
        })


        # Final LLm response
        final_response=client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tools,
                tool_choice="none"
                
            
                
            )

        print("AI:",final_response.choices[0].message.content)
else:
        print("AI:",message.content)

    

