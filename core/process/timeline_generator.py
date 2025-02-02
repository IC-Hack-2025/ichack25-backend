import logging
from typing import Iterable, Optional

from ai.prompts.event_prompts import EventPrompts
from core.model import Timeline, TimelineNode
from core.model.timeline_node import TimelineContent, TimelineConnection, ConnectionType, ContentType, \
    TimelineImageContent, TimelineTextContent
from util.scrape import search_google_images


class TimelineGenerator:
    @staticmethod
    def generate_timeline(timeline: Timeline, input_text: str):
        result: EventPrompts.CheckIsEvent = EventPrompts.CheckIsEvent.do_query(input_text)
        timeline.heading = result.heading
        timeline.description = result.description
        root_node = TimelineNode(
            heading=result.heading,
            contents=[TimelineTextContent(content=result.short_description)] +
                     [TimelineTextContent(content=misconception, content_type=ContentType.MISCONCEPTION) for
                      misconception in result.misconceptions],
            date_start=result.date_start,
            date_end=result.date_end,
        )
        image_urls = search_google_images(result.heading)
        if len(image_urls) > 0:
            title, image_url, link = image_urls[0]
            root_node.main_image_url = TimelineImageContent(
                title=title, image_url=image_url, link=link
            )
        timeline.add_node(root_node)

    @staticmethod
    def continue_timeline(
            timeline: Timeline, max_new_nodes: int = None, continue_id: Optional[int] = None
    ) -> Iterable[TimelineNode]:
        if continue_id is None:
            continue_id = timeline.root_id
        event_to_continue_from = [n for n in timeline.nodes if n.id == continue_id][0]
        result: EventPrompts.ContinueEvents = EventPrompts.ContinueEvents.do_query(
            event_to_continue_from, max_new_nodes
        )
        child_event_list = result.event_list
        visited_events: dict[int, TimelineNode] = {0: event_to_continue_from}
        i = 1
        for i, event_data in enumerate(child_event_list):
            logging.info(f"Expanding on event {i} ({i + 1}/{len(child_event_list)}): {event_data.heading}")
            child_event_result = EventPrompts.DetailContinuedEvents.do_query(
                event_data,
                [visited_events[j] for j in range(i)]
            )
            new_event = TimelineNode(
                heading=event_data.heading,
                contents=[TimelineTextContent(content=child_event_result.description)] +
                         [TimelineTextContent(content=misconception, content_type=ContentType.MISCONCEPTION) for
                          misconception in child_event_result.misconceptions],
                date_start=event_data.date_start,
                date_end=event_data.date_end,
            )
            image_urls = search_google_images(new_event.heading)
            if len(image_urls) > 0:
                main_image_title, main_image_url, main_image_link = image_urls[0]
                new_event.main_image_url = TimelineImageContent(
                    title=main_image_title, image_url=main_image_url, link=main_image_link
                )
            for search_query in child_event_result.key_searches:
                sub_images = search_google_images(search_query)
                if len(sub_images) == 0:
                    continue
                title, image_url, link = sub_images[0]
                new_event.contents.append(TimelineImageContent(title=title, image_url=image_url, link=link))
            timeline.add_node(new_event)
            visited_events[i] = new_event
            yield new_event
            for new_connection in child_event_result.relevant_events:
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
                timeline.add_arc(tc)
            i += 1
