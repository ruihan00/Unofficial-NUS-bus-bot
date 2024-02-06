import json


from src import chat_completion_request, memory


class ConversationAssistant():
    GPT_MODEL = 'gpt-3.5-turbo-1106'

    def __init__(self, system_message, tools, functions):
        self.messages = []
        self.messages.append(
            {"role": "system", "content": f"{system_message}"})
        self.begin_conv()
        self.tools = tools
        self.functions = functions

    def begin_conv(self):
        self.messages.append(
            {"role": "user", "content": "Hi, please introduce yourself, alongside what you can do, and your limitations."})

    @staticmethod
    def chat_completion_request(messages, model, tools=None, tool_choice=None):

        return chat_completion_request(
            messages=messages,
            model=model,
            tools=tools,
            tool_choice=tool_choice
        )

    def one_run(self, human_response=None, tool_choice='auto'):
        if human_response is not None:  # only activates after the first run!
            self.messages.append(
                {"role": "user", "content": f"{human_response}"})
        print(self.messages)
        chat_response = self.chat_completion_request(
            self.messages, model=self.GPT_MODEL, tools=self.tools, tool_choice=tool_choice
        )
        tool_choice = 'auto'  # back to default
        response_message = chat_response.choices[0].message
        self.messages.append(response_message)
        tool_calls = response_message.tool_calls

        #  check if the model wanted to call a function
        if tool_calls:
            # Note: the JSON response may not always be valid; be sure to handle errors
            # extend conversation with assistant's reply
            # send the info for each function call and function response to the model
            # TODO add error handling for json
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                print(function_to_call, function_args)
                if function_name == 'done':
                    function_response, is_completed = function_response
                    if is_completed:
                        print(f"Passing {memory} to choices tool")
                        return function_response, is_completed
                if function_name == 'recorder':
                    function_response, ready_for_recap = function_response
                    if ready_for_recap:
                        tool_choice = {"type": "function",
                                       "function": {"name": "recap"}}
                if function_name == 'recap':  # force recap to be shown to the user
                    tool_choice = 'none'
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            return self.one_run(human_response=None, tool_choice=tool_choice)
        else:
            return response_message.content, False

    def run(self, input=None, first_run=False):
        print(f"memory: {memory}")
        if first_run:
            output = self.one_run()
        else:
            output = self.one_run(human_response=input)
        return output
