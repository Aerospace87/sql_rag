from typing import Any, Sequence
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.core.base.llms.types import ChatMessage, ChatResponseAsyncGen, ChatResponse, MessageRole
from huggingface_hub.inference._generated.types import ChatCompletionStreamOutput

    


class HuggingFaceInferenceAPIwithTokenCount(HuggingFaceInferenceAPI):

    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        if self.task == "conversational" or self.task is None:
            model_kwargs = self._get_model_kwargs(**kwargs)

            async def gen() -> ChatResponseAsyncGen:
                response = ""
                tool_call_strs = []
                cur_index = -1
                
                generator = await self._async_client.chat_completion(
                    messages=self._to_huggingface_messages(messages),
                    stream=True,
                    **model_kwargs,
                )
                
                
                
                async for chunk in generator:
                        

                    chunk: ChatCompletionStreamOutput = chunk
                    
                    if len(chunk.choices) != 0:

                        delta = chunk.choices[0].delta.content or ""
                        response += delta
                        tool_call_delta = chunk.choices[0].delta.tool_calls
                        if tool_call_delta:
                            if tool_call_delta.index != cur_index:
                                cur_index = tool_call_delta.index
                                tool_call_strs.append(tool_call_delta.function.arguments)
                            else:
                                tool_call_strs[cur_index] += (
                                    tool_call_delta.function.arguments
                                )

                        tool_calls = self._parse_streaming_tool_calls(tool_call_strs)
                    

                        additional_kwargs = {"tool_calls": tool_calls} if tool_calls else {}

                    yield ChatResponse(
                        message=ChatMessage(
                            role=MessageRole.ASSISTANT,
                            content=response,
                            additional_kwargs=additional_kwargs,
                        ),
                        delta=delta,
                        raw=chunk,
                    )

                await self._async_client.close()

            return gen()
        else:
            prompt = self.messages_to_prompt(messages)
            completion_stream = await self.astream_complete(
                prompt, formatted=True, **kwargs
            )
            return astream_completion_response_to_chat_response(completion_stream)






















