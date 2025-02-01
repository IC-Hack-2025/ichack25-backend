from typing import List, Literal

from ai.prompts.prompt import FormattedPromptClass
import pydantic

from core.model import TimelineNode
from core.model.timeline_node import ContentType


class EventPrompts:
    class CheckIsEvent(FormattedPromptClass):
        happened: bool
        description: str
        short_description: str
        date_start: str
        date_end: str
        heading: str

        @classmethod
        def _prompt(cls, user_text: str) -> str:
            prompt = f"""
You are given an input text and your task is to determine whether or not it describes an event that is known to have 
occurred. This event may have happened in real-world human history or fictional history. You are supposed to determine
whether it has happened or whether it is a fakery (i.e. a conspiracy, or a misinformation).

[START OF INPUT TEXT]
{user_text}
[END OF INPUT TEXT]

Instructions steps:
1. Read and understand the input text.
2. Interpret its meaning in the context of events that are part of a narrative, whether it is real or fictional. The 
important thing is whether they are known to have happened as part of that narrative or not.
3. Structure your answer in the following way:
    - If the event is known to have happened, set "happened" to True in the result. Otherwise, set "happened" to False.
    - If the event is known to have happened, give a detailed description of the event in the context of the narrative.
        This should be a string in the "description" key. This should be several paragraphs long, ideally as long and 
        detailed as possible.
    - If the event is NOT known to have happened, give a description of how the event is a misconception or a 
        conspiracy, if that is the case. You must be strictly against misinformation or controversial theories. The 
        description must renounce the idea that the event happened and give evidence for why it did not happen.
    - Reiterate the same information as the description above but shorten it, make it more concise and extract only 
        the key points from it, then set the result into the "short_description" key.
    - Give a precise date for when the event is said to have occurred. If the event occurred over a period of time, 
        set "date_start" to the start of the event and "date_end" to the end of the event. If the event happened within 
        a day, give the date AND time as one string for these values.
    - Finally, a brief heading for the event should be given in the "heading" key. Maximum one sentence, with a short 
        length if the event is given a specific name, or a medium length if there is no specific name for that event.
            """
            return prompt

    class ContinueEvents(FormattedPromptClass):
        class EventListItem(pydantic.BaseModel):
            heading: str
            date_start: str
            date_end: str

        event_list: List[EventListItem]

        @classmethod
        def _prompt(cls, event: TimelineNode, max_num_continued: int = None) -> str:
            prompt = f"""
You are given an event that has happened in human history or in a fictional narrative. Your task is to return a list of
other events that are known to have occurred after the input event. The input contains a heading for the event, as well
as a description, and when it happened.

[START OF INPUT EVENT]
Event heading: "{event.heading}"
Description: "{" ".join(c.content for c in event.contents if c.content_type == ContentType.TEXT)}"
Start date: "{event.date_start}"
End date: "{event.date_end}"
[END OF INPUT EVENT]

Instruction steps:
1. Read the input event carefully and understand the context. You must identify which narrative it has taken place in,
    whether it is in real life or a fictional narrative.
2. Search in your knowledge base for events that chronologically occur after the input event which are either 
    directly caused by the event or indirectly affected by it. Do not include events that are irrelevant to the input 
    event, but be creative and find interesting connections between certain events if they exist.
3. Structure your output in the following way:
    - "event_list" should be a list of items containing data about the events we are interested in.
    - Each item in the "event_list" list should have the following structure:
        - The "heading" is a string that names the event in question. The heading should be short if the event is 
            given a specific and easily recognisable name, or a medium length if the event does not have a specific name 
            or is less well known.
        - "date_start" and "date_end" describe the start and end of the event, using in-narrative date/time formats. 
            If the event started and ended on the same day, the values should contain a timestamp as well as a date.
        - **IMPORTANT: The event list items should be arranged in CHRONOLOGICAL ORDER.
{
            f"""
    - The "event_list" should be only {max_num_continued} items long, no more than this. If fewer relevant events 
        happened than this, you may output fewer items.
"""
            if max_num_continued is not None else ""
}
"""
            return prompt

    class DetailContinuedEvents(FormattedPromptClass):
        class RelevantEventItem(pydantic.BaseModel):
            event_index: int
            relevancy_type: Literal["caused", "influenced"]

        description: str
        relevant_events: List[RelevantEventItem]

        @classmethod
        def _prompt(cls, current_event, previous_events: list[TimelineNode]) -> str:
            prompt = f"""
You are given a short description of an event, as well as the relevant events that preceded it in the narrative. The
narrative may be real-world or fictional. Your task is to fully describe the given event, with more detail than 
given, as well as identify its connections to the previously listed events.

[START OF THE INPUT EVENT]
Heading: "{current_event.heading}"
Start date: "{current_event.date_start}"
End date: "{current_event.date_end}"
[END OF THE INPUT EVENT]

[START OF PREVIOUS EVENTS]
{
    ("-" * 20).join(
        f"""Event {i}:\n"""
        f"""Heading: ""\n"""
        f"""Description: {e.full_description}\n"""
        f"""Start date: "{e.date_start}"\nEnd date: "{e.date_end}"\n"""
        for i, e in enumerate(previous_events)
    )
}
[END OF PREVIOUS EVENTS]

Instruction steps:
1. Read the input event data and understand its context and its narrative.
2. Read the previous events and build up a timeline of the event procession. Understand where the input event fits 
    into the timeline and how it relates to the previous events. Take note of the indexes of the events as they will 
    be important later. Do NOT include the indexes in your output answer, the index is only for internal use.
3. Decide which events in the list of previous events are direct causes to the input event. This may be a subset of 
    the previous event list, instead of all the events. Decide whether the event was absolutely necessary to have 
    occurred for the input event to also have occurred. Identify the relation between the events, if it exists, 
    relevant to the context narrative.
4. Structure your output in the following way:
    - "description" should be a string fully describing the event. The description should include some lines about 
        how the previous events that caused the event to occur are related to the input event. It is important to 
        describe the relevance of these events and give a detailed account of how they relate in the narrative.
    - "relevant_events" should be a list of items with the following structure:
        - "event_index" is an int equal to the index of the previous event that caused the 
            input event. The index MUST be present in the list of previous events.
        - "relevancy" is a string that describes the relevance of the input event. It is either "caused" if the 
            previous event DIRECTLY caused the input event, or "influenced" if the previous event indirectly influenced 
            the causation of the input event. Use accepted interpretations of the history of the narrative context to 
            determine how relevant the event is. Don't use controversial opinions or misleading information / 
            misinformation.
"""
            return prompt
