import json
import time
import tiktoken
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, StoppingCriteria
from transformers.generation.stopping_criteria import StoppingCriteriaList

# Load the LLaMA model and tokenizer
#BASE_MODEL = "mistralai/Mistral-7B-v0.1"
# BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
#BASE_MODEL = "HuggingFaceH4/zephyr-7b-beta"
#BASE_MODEL = "google/gemma-7b"
#BASE_MODEL = "facebook/bart-base"
#BASE_MODEL = "stabilityai/stablelm-3b-4e1t"
#BASE_MODEL = "stabilityai/stablelm-2-12b-chat"
#BASE_MODEL = "CohereForAI/c4ai-command-r-plus"
BASE_MODEL = "CohereForAI/c4ai-command-r-v01-4bit"
#BASE_MODEL = "ai21labs/Jamba-v0.1"
#BASE_MODEL = "apple/OpenELM-3B"
#BASE_MODEL = "meta-llama/Meta-Llama-3-8B"
#BASE_MODEL = "meta-llama/Llama-2-7b-chat-hf"
#BASE_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, device_map="auto", load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token_id = tokenizer.eos_token_id

# Move the model to the available GPUs
#if torch.cuda.device_count() > 1:
    #print(f"Using {torch.cuda.device_count()} GPUs")
    #model = torch.nn.DataParallel(model)

# Set the device
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#model.to(device)


# Define the stop sequence and convert it to token IDs
stop_sequence = "###"
stop_token_ids = tokenizer(stop_sequence, return_tensors='pt')['input_ids']

class StoppingCriteriaSub(StoppingCriteriaList):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs):
        if stop_token_ids.numel() == 0:  # Check if stop_token_ids is empty
            return False

        # Check if the stop sequence appears at the end of the generated text
        if (input_ids[0][-len(stop_token_ids[0]):] == stop_token_ids[0]).all():
            return True
        return False

# Initialize the stopping criteria
stopping_criteria = StoppingCriteriaSub()

# ... (rest of the code remains the same)

# Define the stop sequence and convert it to token IDs
#stop_sequence = "###"
#stop_token_ids = tokenizer(stop_sequence, return_tensors='pt')['input_ids'].to(device)

#class StoppingCriteriaSub(StoppingCriteria):
#    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs):
#        if stop_token_ids.numel() == 0:  # Check if stop_token_ids is empty
#            return False
#
#        # Check if the stop sequence appears at the end of the generated text
#        if (input_ids[0][-len(stop_token_ids[0]):] == stop_token_ids[0]).all():
#            return True
#        return False

# Initialize the stopping criteria
#stopping_criteria = StoppingCriteriaSub()

eng = []
acts = []
eng = json.load(open('../worlds/2D_world_3x.json'))
# eng = json.load(open('../worlds/2D_world_5x.json'))
# eng = json.load(open('../worlds/2D_world_7x.json'))


with open('prompt_3x.txt', 'r') as f:
    prompt = f.read()
    #print("Print ze prompt")
    #print(prompt)

out = []
inp_tokens = 0
inputs = []

# Assuming there's only one entry in the JSON list
#entry = data[0]
#agent_as_a_point = entry.get('agent_as_a_point', '')

# Count the number of words in the agent_as_a_point field
#word_count = len(agent_as_a_point.split())

for i in range(len(eng)):
    try:
        prompt_ = f"""{prompt}  
<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
{eng[i]['nl_description']}
<|END_OF_TURN_TOKEN|> 
"""
        #print("Prompt piece")
        #print(prompt)
        #print("Complete feed")
        #print(prompt_)
        #print("Let's see the NL description from JSON")
        #print(eng[i]['nl_description'])
        #print("Printed NL description")
        input_ids = tokenizer.encode(prompt_, return_tensors="pt")
        #print("Extracted input ids")
        # Generate text using LLaMA
        # Assuming there's only one entry in the JSON list
        #entry = eng[i]
        #iagent_as_a_point = entry.get('agent_as_a_point', '')
        agent_as_a_point = eng[i].get('agent_as_a_point', '')
        word_count = len(agent_as_a_point.split())

        # Count the number of words in the agent_as_a_point field
        #word_count = len(agent_as_a_point.split()) + 1
        print("This is word count")
        print(word_count)
        with torch.no_grad():
            output = model.generate(input_ids, max_length = 720, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id, stopping_criteria=stopping_criteria)
        #print("Got output")
        # Decode the generated output
        response = tokenizer.decode(output[0], skip_special_tokens=True)

        # Show the response
          # Show the response
        #print("Let's see the respnse")
        print(response)
        #print("Got reponse")

        test = {
            "english": eng[i]['nl_description'],
            "ground_truth": eng[i]['agent_as_a_point'],
            "predicted": response,
            'world': eng[i]['world'],
        }
        print("Appended a row of data")
        out.append(test)

    except Exception as e:
        #print(e)
        print(f"Error processing entry {i}: {e}")
        time.sleep(60)

with open('results_3x.json', 'w') as fo:
    json_object = json.dumps(out, indent=4)
    fo.write(json_object)
    fo.write('\n')