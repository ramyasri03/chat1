from configure import KEY1, URL, MODEL
from openai import OpenAI
import traceback
import os
import random

# Initialize client with provided config
client = OpenAI(api_key=KEY1, base_url=URL)

# Define the rules from your prompt
RULES = [
    'Call Greeting', 'Did the agent actively listen to the customer and helped ?',
    'Did the agent paraphrase the issue ?', 'Did the agent Provide an assurance statement ?',
    'Did the agent conduct himself / herself in a courteous manner during the call?',
    'Did the agent provide complete and accurate information to the user ?',
    'Did the agent personalize the call?', 'Did the agent avoid interrupting the caller ?',
    'Did the agent respond to the user accordingly ?', 'Did the agent avoid dead air ?',
    'Hold Procedure Followed?', 'Did the agent take control of the call?', 
    'Empathy/Sympathy(if applicable)', 'Was the agent professional throughout the call and took ownership of the issue ?',
    'Closing Script', 'User Verification - First & Last Name, Phone ,email',
    'Did the agent probe effectively by using appropriate questions?',
    'Did the agent check previous case history to understand the case better?',
    'Did agent provide accurate/appropriate solution(information)?',
    'Did the agent create a ticket?', 'Did the agent document all steps documented from diagnostic to troubleshooting?',
    'Did the agent seek user permission to connect and disconnect from remote session?',
    'Did the agent take user concurrence for ticket closure?',
    'Did the agent select appropriate case status (Closed,Open,Pending)?',
    'Did the agent offer ticket number to user?', 'Did the agent inform about feedback link ?',
    'Volume/Rate of Speech', 'Speech/Pronunciation', 'Grammar & Vocabulary',
    'Sentence formation/Question Structure', 'Speech Modulation/Intonation'
]
rules_str = "', '".join(RULES)

# Infrastructure issues, resolutions, sentiments, tones from your prompt
INFRASTRUCTURE_ISSUES = [
    'Unable to login to application', 'Device not active', 'Email not updating',
    'Upgrade link not working', 'Unable to login to PC', 'Multifactor authentication not working',
    'Account locked out and Session hanging'
]

RESOLUTION_STATUSES = ['Resolved', 'Escalated', 'Unresolved']

CUSTOMER_SENTIMENTS = ['Positive', 'Neutral', 'Negative']

AGENT_TONES = ['Polite', 'Neutral', 'Rude']

def generate_single_chat(issue: str, resolution: str, customer_sentiment: str, agent_tone: str, follow_rules: bool) -> str:
    """
    Generate a single chat transcript using OpenAI Chat Completions.
    """
    rule_instruction = "strictly FOLLOW all rules" if follow_rules else "VIOLATE 2-4 rules (e.g., no greeting, vague resolution, overuse of slang)"
    
    prompt = f"""You are simulating a service desk scenario with 2 roles:
1. customer: raising complaint with {customer_sentiment} tone (Positive: enthusiastic; Neutral: factual; Negative: frustrated).
2. agent: helping to resolve the issue with {agent_tone} tone (Polite: courteous; Neutral: straightforward; Rude: curt/dismissive).

Generate a SINGLE full chat transcript (10-20 total messages, alternating customer/agent turns, starting with customer) for the issue: '{issue}'.
End until {resolution}.
{rule_instruction}: {rules_str}

Format as: customer: message\nagent: message\n... (ONLY the chat text—no extra labels or explanations).
Keep concise: 150-250 words max (<400 tokens)."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            n=1,
            messages=[
                {"role": "system", "content": "You are an AI assistant who can generate service desk log."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        traceback.print_exc()
        print(f"Error generating chat: {e}")
        return "Error generating chat transcript."

def main(num_chats: int = 50, output_folder: str = 'chats'):
    """
    Generate num_chats individual chat files in output_folder.
    Half follow rules, half violate (alternating for simplicity).
    """
    os.makedirs(output_folder, exist_ok=True)
    
    for i in range(num_chats):
        # Randomly select params
        issue = random.choice(INFRASTRUCTURE_ISSUES)
        resolution = random.choice(RESOLUTION_STATUSES)
        customer_sentiment = random.choice(CUSTOMER_SENTIMENTS)
        agent_tone = random.choice(AGENT_TONES)
        follow_rules = (i % 2 == 0)  # Alternate: even indices follow rules, odd violate
        
        chat = generate_single_chat(issue, resolution, customer_sentiment, agent_tone, follow_rules)
        
        # Create a descriptive filename
        safe_issue = issue.replace(" ", "_").replace("/", "_").replace("'", "")
        filename = f"{output_folder}/chat_{i+1:03d}_{safe_issue}_{resolution}_{customer_sentiment}_{agent_tone}_{'follow' if follow_rules else 'violate'}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(chat)
        
        print(f"Generated and saved: {filename}")

if __name__ == "__main__":
    main(num_chats=50)  # Adjust num_chats as needed