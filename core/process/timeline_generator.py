from typing import Iterable

from ai.prompts.event_prompts import EventPrompts
from core.model import Timeline, TimelineNode
from core.model.timeline_node import TimelineContent, TimelineConnection, ConnectionType


class TimelineGenerator:
    @staticmethod
    def generate_timeline(input_text: str) -> Timeline:
        result: EventPrompts.CheckIsEvent = EventPrompts.CheckIsEvent.do_query(input_text)
        t = Timeline(heading=result.heading, description=result.description)
        root_node = TimelineNode(
            heading=result.heading,
            contents=[TimelineContent(content=result.short_description)],
            date_start=result.date_start,
            date_end=result.date_end,
        )
        t.add_node(root_node)
        return t

    @staticmethod
    def continue_timeline(timeline: Timeline, max_new_nodes: int = None) -> Iterable[TimelineNode]:
        event_to_continue_from = [n for n in timeline.nodes if n.id == timeline.root_id][0]
        result: EventPrompts.ContinueEvents = EventPrompts.ContinueEvents.do_query(
            event_to_continue_from, max_new_nodes
        )
        event_list = result.event_list
        visited_events: dict[int, TimelineNode] = {}
        for i, event_data in enumerate(event_list):
            new_event_result = EventPrompts.DetailContinuedEvents.do_query(
                event_data,
                [visited_events[j] for j in range(i)]
            )
            new_event = TimelineNode(
                heading=event_data.heading,
                contents=[TimelineContent(content=new_event_result.description)],
                date_start=event_data.date_start,
                date_end=event_data.date_end,
            )
            timeline.add_node(new_event)
            visited_events[i] = new_event
            for new_connection in new_event_result.relevant_events:
                prev_event_index = new_connection.event_index
                if prev_event_index not in visited_events:
                    continue
                prev_event = visited_events[prev_event_index]
                tc = TimelineConnection(
                    from_id=prev_event.id,
                    to_id=new_event.id,
                    connection_type=ConnectionType(new_connection.relevancy_type),
                )
                prev_event.connections.append(tc)
                new_event.connections.append(tc)
                timeline.arcs.append(tc)
            yield new_event
