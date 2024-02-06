from src import education_collection, job_role_collection, target_job_role_collection, memory, chat_completion_request, recap_needed, attributes


# TODO add tool_choice for checker tools to force recording? If accuracy gets worse this might be somethiing to do.
def checker_tool_education(education):
    return_message = ''
    for edu in education:
        result = education_collection.query(
            query_texts=[edu.title()],
            n_results=5,
        )
        print(
            f"closest educations: {list(zip(result['ids'][0], result['distances'][0]))}")

        if result['distances'][0][0] > 0.15:
            nearby_jobs = ", ".join(result['ids'][0])
            return_message += f'''Tell the user that unfortunately {edu} is not a known major in Singapore.Other similar educations that are supported: {nearby_jobs}. '''
        else:
            return_message += f"{edu} is mapped to {result['ids'][0][0]}, which is an acceptable education. This education should be passed to the recorder tool. "
    return return_message.strip()


def checker_tool_target_job_role(target_job_role):
    result = target_job_role_collection.query(
        query_texts=[target_job_role.title()],
        n_results=5,
    )
    print(
        f"closest target job roles: {list(zip(result['ids'][0], result['distances'][0]))}")

    if result['distances'][0][0] > 0.1:
        nearby_jobs = ", ".join(result['ids'][0])
        return f'''Tell the user that unfortunately the desired job role is not a known or valid ICT or Retail job in Singapore. Other similar job roles that are supported: {nearby_jobs}'''
    else:
        return f"{target_job_role} is mapped to {result['ids'][0][0]}, which is an acceptable target job role. This target job role should be passed to the recorder tool."


def checker_tool_job_role(job_role):
    result = job_role_collection.query(
        query_texts=[job_role.title()],
        n_results=5,
    )
    print(
        f"closest job roles: {list(zip(result['ids'][0], result['distances'][0]))}")

    if result['distances'][0][0] > 0.2:
        nearby_jobs = ", ".join(result['ids'][0])
        return f'''Tell the user that unfortunately the job is not a known or valid job role in Singapore. Other similar job roles that are supported: {nearby_jobs}'''
    else:
        return f"{job_role} is mapped to {result['ids'][0][0]}, which is an acceptable job role. This previous job role experience should be passed to the recorder tool."


def recorder_tool(target_job_role=None, education=None, prior_work_experiences=None, work_preferences=None):
    global recap_needed
    ready_for_recap = True
    if target_job_role is not None:
        memory['target_job_role'] = target_job_role
        recap_needed = True
    if education is not None:
        memory['education'] = education
        recap_needed = True
    if prior_work_experiences is not None:
        memory['prior_work_experiences'] = prior_work_experiences
        recap_needed = True
    if work_preferences is not None:
        memory['work_preferences'] = work_preferences
        recap_needed = True

    def format(att):
        formatted_att = ' '.join(att.split('_')).title()
        info = memory[att]
        if isinstance(info, list):
            formatted_info = ', '.join(info)
        else:
            formatted_info = info
        return f'{formatted_att} - {formatted_info}'
    received_information_string = ', '.join([format(att) for att in memory])
    return_message = f"Successfully recorded the information down. I now have their following information: {received_information_string}."
    if all([att in memory for att in attributes]):
        return_message += "I now have all the information required from the client, proceeed to recap tool."
    else:
        missing = []
        for att in attributes:
            if att not in memory:
                ready_for_recap = False
                formatted_att = ' '.join(att.split('_')).title()
                missing.append(formatted_att)
        return_message += f" I'm missing {', '.join(missing)} information. Will have to ask the user."
    return return_message, ready_for_recap


def recap_tool():
    global recap_needed
    for att in attributes:
        if att not in memory:
            return f"User has not yet indicated their {att}, please ask the user for it."

    messages = []
    messages.append({"role": "system", "content": "You are acting as a career advisor trying to recap what has been discussed in the career session. You will be provided bullet point information. Please recap what has been said only from the information provided. Be precise and succint."})
    formatted_memory_str = '\n'.join(
        [f"{key}:{memory[key]}" for key in memory])
    messages.append(
        {"role": "user", "content": f"Here are the information:\n{formatted_memory_str}"})
    chat_response = chat_completion_request(
        messages
    )
    assistant_message = chat_response.choices[0].message
    recap_needed = False
    return f"This is the recap of the conversation.\nRecap: {assistant_message.content}. I'm not sure if it is correct. Show this recap to the user to verify. If user changes anything, check(if necessary) and record it again. If no changes, call the done tool."


def done_tool():
    for att in attributes:
        if att not in memory:
            return f"User has not yet indicated their {att}, please ask the user for it.", False
    if not recap_needed:
        print(f"User is done!")
        return 'All necessary information is gathered, end conversation with user and proceed to choices tool', True
    else:
        return "please call the recap tool and ask the user to validate it's latest output", False


functions = {
    'checker_for_target_job_role': checker_tool_target_job_role,
    'checker_for_education': checker_tool_education,
    'checker_for_prior_work_experiences': checker_tool_job_role,
    'recorder': recorder_tool,
    'recap': recap_tool,
    'done': done_tool,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "checker_for_target_job_role",
            "description": "check if the target/desired job role exists in the database, inputs have to be in english, so translate if needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_job_role": {
                        "type": "string",
                        "description": "Target job role to check. e.g. Software Engineer",
                    },
                },
                "required": ["target_job_role"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checker_for_prior_work_experiences",
            "description": "check if previous job role exists in the database, inputs have to be in english, so translate if needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_role": {
                        "type": "string",
                        "description": "Job role to check. e.g. Engineer",
                    },
                },
                "required": ["job_role"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checker_for_education",
            "description": "check if the education exists in the database. inputs have to be in english, so translate if needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "education": {
                        "type": "array",
                        "description": "education(s) to check. e.g. Biology",
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": ["education"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recorder",
            "description": "upserts important information after checking that it exists in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_job_role": {
                        "type": "string",
                        "description": "User's target job role",
                    },
                    "education": {
                        "type": "array",
                        "description": "User's education",
                        "items": {
                            "type": "string"
                        }
                    },
                    "prior_work_experiences": {
                        "type": "array",
                        "description": "User's prior work experiences, or just input ['nothing'] if they do not have any",
                        "items": {
                            "type": "string"
                        }
                    },
                    "work_preferences": {
                        "type": "string",
                        "description": "User's work preferences, or just say 'nothing' if they do not have any",
                    },
                },
                "required": []
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recap",
            "description": "Used to formulate a recap to show the user",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "call this tool to end the conversation after user ahs verbally acknowledged the recap",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
]
