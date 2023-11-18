# First
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import LLMChain
from langchain.llms import Cohere
from langchain.prompts import PromptTemplate
import base64

COHERE_API_KEY = st.secrets.COHERE_API_KEY

import json
import requests

st.title("📜 FLOWz-IO")
st.subheader(
    "Create interactive flowcharts and mindmaps",
)
st.sidebar.title("Customization Options")

# workflow/ flowchart 
mindorflow = st.sidebar.radio("What would you like to generate?", ["Flowchart","Workflow", "Mind map"])

def generate_kroki_diagram(diagram_code, diagram_type):
    kroki_api_url = "https://kroki.io"
    payload = {
        "diagram_source": diagram_code,
        "diagram_type": diagram_type,
    }
    response = requests.post(f"{kroki_api_url}/{diagram_type}/svg", json=payload)
    return response.text if response.status_code == 200 else None

def mindmapgen(data):
    #edit the svg data here
    svg_file_path = "sample.svg"
    with open(svg_file_path, "r") as svg_file:
        svg_content = svg_file.read()
    return svg_content

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def create_flowchart(newj,wf = 0):#2nd parameter 1 for workflow
    lis = ['A', 'B', 'C', 'D', 'E', "F", "G", "H","I","J", 'K', "L", "M"]
    flowchart = ""
    if wf == 0:
        flowchart = "flowchart TD" + "\n"
    elif wf == 1:
        flowchart = "flowchart LR" + "\n"
    for i in range(len(newj['steps'])):
        try:
            flowchart  = flowchart + "    " + lis[i]+'[' +newj['steps'][i]['subheading'] + ']' + " --> " + lis[i+1] +'[' +newj['steps'][i+1]['subheading'] + ']' + '\n'
        except:
            pass
    return flowchart

def create_flowchart_cohere(query,wf= 0):#2nd parameter 1 for workflow
    template = """{text}
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    llm = Cohere(cohere_api_key=COHERE_API_KEY, max_tokens = 1024)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    side_prompt = """
    use multiple steps to explain in a easy way 
    keep it simple explanations should be only 15 to 30 words long
    and give the output in this format
    it should be json strictly
    example
    {
    "heading" : heading,
    steps: [
    {"subheading" : step , 
    "explain": explain subheading}
    ]
    }
    """

    k = llm_chain.run(query+side_prompt)
    print(k)

    newparse = k[k.find("{"):(len(k)-k[::-1].find('}'))]
    newj = json.loads(newparse)
    flows = ''
    if wf == 1:
        flows = create_flowchart(newj,1)
    else:
        flows = create_flowchart(newj)
    diagram_svg = generate_kroki_diagram(flows, "mermaid")

    render_svg(diagram_svg)

    steps = ""
    for i in range(len(newj['steps'])):
        steps = steps + str(i+1) + ") " + newj['steps'][i]['explain'] + "\n"
    
    return steps


#final
def create_mindmap(newj):
    mindmap = "mindmap"+"\n"
    mindmap = mindmap + "  " + newj['heading'] + "\n"
    for i in list(newj['sub-headings'].keys()):
        mindmap = mindmap + "    " + i + "\n"
        for i in newj['sub-headings'][i]:
            mindmap = mindmap + "      " + i + "\n"
    return mindmap

def create_mindmap_cohere(query):
    template = """{text}
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    llm = Cohere(cohere_api_key=COHERE_API_KEY, max_tokens = 1024)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    side_prompt = """
    for the above text create a tree node hierarchy for the above content
            in this format
            heading
            sub headings
            keywords
            extract as many keywords and sub headings as possible
            there should be about 5 to 20 headings and each of them should have multiple keywords,
            keywords can be key phrases in the length of 1 word to 7 words
            it should maintain a hierarchy
            should return in this json format
            the format should be strictly followed 
            example

            {"heading": heading,
            sub-headings :
            {"sub-heading": sub heading,
            "keyword":[] ,
            },
            {"sub-heading": sub heading,
            "keyword":[] ,
            },
            }"""

    k = llm_chain.run(query+side_prompt)
    newparse = k[k.find("{"):(len(k)-k[::-1].find('}'))]
    newj = json.loads(newparse)

    minds = create_mindmap(newj)

    diagram_svg = generate_kroki_diagram(minds, "mermaid")

    render_svg(diagram_svg)

    return None

if mindorflow == "Mind map":
    mindmap_data = st.text_area("Enter your text:")
    if st.button("Generate"):
        progress_bar = st.progress(0)

        create_mindmap_cohere(mindmap_data)
        progress_bar.progress(100)


if mindorflow == "Flowchart":
    if "messages" not in st.session_state.keys(): # Initialize the chat messages history
        st.session_state.messages = [{"role": "assistant", "content": "Ask me anything!"}]

    if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages: # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                msg = create_flowchart_cohere(prompt)
                st.write(msg)
                message = {"role": "assistant", "content": msg}
                st.session_state.messages.append(message) # Add response to message history

if mindorflow == "Workflow":
    if "messages" not in st.session_state.keys(): # Initialize the chat messages history
        st.session_state.messages = [{"role": "assistant", "content": "Ask me anything!"}]

    if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages: # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                msg = create_flowchart_cohere(prompt,1)
                st.write(msg)
                message = {"role": "assistant", "content": msg}
                st.session_state.messages.append(message) # Add response to message history