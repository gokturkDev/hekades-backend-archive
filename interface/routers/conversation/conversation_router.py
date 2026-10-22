import json
import logging
from datetime import datetime
from typing import Iterator, Union, Annotated, AsyncIterator, Optional

import inject
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, WebSocketException
from pydantic import ValidationError

from business.ai.ai_facade import ResponsePacketType, ResponsePacket
from business.entity.conversation.conversation_entity import ConversationType
from business.entity.conversation.message_entity import SystemMessageEntity
from business.entity.user.user_entity import UserEntity, UserRole
from business.usecase.conversation.add_user_message import AddUserMessageUsecase
from business.usecase.conversation.get_conversations_of_user_usecase import GetConversationsOfUserUsecase
from business.usecase.conversation.get_messages_of_conversation_usecase import GetMessagesOfConversationUsecase
from business.usecase.conversation.start_conversation_usecase import StartConversationUsecase
from core.lang.supported_lang import SupportedLanguages
from interface.auth.auth import get_current_active_user, get_current_active_user_from_websocket
from interface.routers.conversation.schemas import WebsocketUserPacket, WebsocketUserPacketType
from interface.serialization.serialize_conversation import serialize_message_entities, serialize_conversation_entities
from main.dependency_container import DepContainer

router = APIRouter(prefix="/conversation", tags=["conversation"])
logger = logging.getLogger("hekades")

ws_connections_dict = {}


@router.websocket("/")
async def convo(websocket: WebSocket,
                token: Annotated[Union[str, None], Query()] = None):
    user = await get_current_active_user_from_websocket(token=token)
    # Auth checks
    if ws_connections_dict.get(user.email) is None:
        ws_connections_dict[user.email] = 0
    if user.role != UserRole.ADMIN and ws_connections_dict[user.email] > 9:
        await websocket.close(code=4003, reason="Too many connections")
        return

    await websocket.accept()

    ws_connections_dict[user.email] += 1
    logger.info("Web socket accepted for user " + user.email)

    while True:
        try:
            packet = WebsocketUserPacket.model_validate(await websocket.receive_json())
            if packet.type == WebsocketUserPacketType.NEW_CONVO:
                await _handle_new_conversation(user, packet, websocket)
            elif packet.type == WebsocketUserPacketType.PUBMED_REQUEST:
                await _handle_pubmed_search(packet, websocket)


        except WebSocketDisconnect as e:
            logger.info(f"User disconnected from websocket with {str(e)}")
            break
        except ValidationError as e:
            logger.error(f"Malformed packet: {str(e)}")
            await websocket.send_json({"error": "Malformed packet"})
            continue
        except Exception:
            logger.exception("Unexpected error")
            await websocket.send_json({"error": "Unexpected error"})
            break

    ws_connections_dict[user.email] -= 1
    logger.info("Web socket closed for" + user.email)


async def _handle_new_conversation(user, packet, websocket):
    message = packet.content.message
    language = packet.content.language
    patient_id = packet.content.patient_id
    patient = None

    if patient_id is not None:
        patient = await _get_patient(patient_id, user)

    conversation = _start_conversation(title=message, user_email=user.email, patient_id=patient_id)
    logger.info(f"Conversation started with {user.email}: {conversation.convo_id}")
    system_message = _initialize_system_message(conversation.convo_id)
    _add_user_message_to_conversation(conversation.convo_id, message)
    try:
        await websocket.send_text(_get_conversation_info_response_packet(conversation).model_dump_json())
        async for response_packet in _stream_response_and_save(user_message=message,
                                                               system_message=system_message,
                                                               conversation=conversation,
                                                               language=language,
                                                               patient=patient):
            await websocket.send_json(response_packet.model_dump())
        _upload_message(system_message=system_message)
        _update_conversation(conversation)
        logger.info(f"Conversation ended: {conversation.convo_id}")
    except WebSocketDisconnect as e:
        logger.info(
            f"Web socket disconnected during generation with {str(e.code) + e.reason + str(e)}\n Upload message and propagate error")
        _upload_message(system_message=system_message)
        raise WebSocketDisconnect(code=4001, reason="User disconnected during generation")


async def _get_patient(patient_id, user):
    patients = inject.instance(DepContainer).patient_repo.get_all_patients(user.email)
    patient_ids = [patient.patient_id for patient in patients]
    can_access_patient = True if patient_id in patient_ids else False
    if not can_access_patient:
        raise WebSocketException(code=4003, reason="User does not have access to this patient")
    return patients[patient_ids.index(patient_id)]


async def _handle_pubmed_search(packet: WebsocketUserPacket, websocket):
    convo_id = packet.content.conversation_id
    logger.info(f"Pubmed search request for conversation {convo_id}")

    messages = inject.instance(DepContainer).convo_repo.get_conversation_messages(convo_id)
    user_query = messages[0].content

    convo = inject.instance(DepContainer).convo_repo.get_conversation_by_id(convo_id)
    patient = inject.instance(DepContainer).patient_repo.get_patient(convo.patient_id) if convo.patient_id else None

    try:
        async for packet in inject.instance(DepContainer).ai_facade.pubmed_search(
                convo_id=convo_id,
                language=packet.content.language,
                user_message=user_query,
                patient=patient
        ):
            if packet.type == ResponsePacketType.LITERATURE_SUMMARY_TOKEN:
                if convo.pubmed_summary is None:
                    convo.pubmed_summary = ""
                convo.pubmed_summary += packet.content
            elif packet.type == ResponsePacketType.LITERATURE_DOCUMENTS:
                convo.literature_docs = packet.content

            await websocket.send_json(packet.model_dump())
        logger.info(f"Pubmed search ended for conversation {convo_id}")
        _update_conversation(convo)
    except WebSocketDisconnect as e:
        logger.info(
            f"Web socket disconnected during pubmed search with {e.code}, saving progress and propagating error")
        _update_conversation(convo)
        raise WebSocketDisconnect(code=4001, reason="User disconnected during pubmed search")


def _update_conversation(convo):
    inject.instance(DepContainer).convo_repo.update_conversation(convo)


@router.get("/all")
def get_conversations_of_user(user: UserEntity = Depends(get_current_active_user)):
    get_conversations_usecase = GetConversationsOfUserUsecase(convo_repo=inject.instance(DepContainer).convo_repo)
    conversations = get_conversations_usecase.execute(user_email=user.email)
    serialized_conversations = serialize_conversation_entities(conversations)
    return serialized_conversations


@router.get("/{conversation_id}/info")
def get_conversation(conversation_id, user: UserEntity = Depends(get_current_active_user)):
    _assert_access_to_convo(conversation_id, user.email)
    conversation = inject.instance(DepContainer).convo_repo.get_conversation_by_id(conversation_id)
    serialized_conversation = conversation.model_dump()
    return serialized_conversation


@router.get("/{conversation_id}")
def get_messages_of_conversation(conversation_id, user: UserEntity = Depends(get_current_active_user)):
    _assert_access_to_convo(conversation_id, user.email)
    get_messages_usecase = GetMessagesOfConversationUsecase(convo_repo=inject.instance(DepContainer).convo_repo)
    messages = get_messages_usecase.execute(conversation_id)
    serialized_messages = serialize_message_entities(messages)
    return serialized_messages


async def _stream_response_and_save(user_message, system_message, conversation, language, patient) -> AsyncIterator[
    ResponsePacket]:
    ai_facade = inject.instance(DepContainer).ai_facade

    async for packet in ai_facade.respond_to_user([], system_message.convo_id, user_message, language, patient):
        if packet.type == ResponsePacketType.TOKEN:
            if system_message.phases.get("answer") is None:
                system_message.phases["answer"] = ""
            system_message.phases["answer"] += packet.content

        elif packet.type == ResponsePacketType.TAKEAWAY_TOKEN:
            if system_message.phases.get("takeaway") is None:
                system_message.phases["takeaway"] = ""
            system_message.phases["takeaway"] += packet.content

        elif packet.type == ResponsePacketType.SOURCES:
            system_message.sources["answer"] = packet.content

        elif packet.type == ResponsePacketType.TAKEAWAY_SOURCES:
            system_message.sources["takeaway"] = packet.content

        elif packet.type == ResponsePacketType.CONFIDENCE_INDEX:
            conversation.confidence_index = packet.content

        elif packet.type == ResponsePacketType.QUESTION_TYPE:
            if packet.content == "information":
                conversation.type = ConversationType.information
            else:
                conversation.type = ConversationType.case

        yield packet


def _initialize_system_message(conversation_id):
    return SystemMessageEntity(
        convo_id=conversation_id,
        order=2,
        created_at=datetime.now(),
    )


def _upload_message(system_message: SystemMessageEntity):
    inject.instance(DepContainer).convo_repo.add_message(system_message)


def _update_message(system_message: SystemMessageEntity):
    inject.instance(DepContainer).convo_repo.update_message(system_message.convo_id, system_message)


def _add_user_message_to_conversation(convo_id, message_content):
    usecase = AddUserMessageUsecase(convo_repo=inject.instance(DepContainer).convo_repo)
    usecase.execute(
        convo_id=convo_id,
        content=message_content,
        created_at=datetime.now()
    )


def _start_conversation(title: str, user_email: str, patient_id: Optional[str] = None):
    start_usecase = StartConversationUsecase(convo_repo=inject.instance(DepContainer).convo_repo)
    conversation = start_usecase.execute(title=title, user_email=user_email, patient_id=patient_id)
    return conversation


def _get_conversation_info_response_packet(conversation):
    return ResponsePacket(
        type=ResponsePacketType.CONVERSATION_INFO,
        content=conversation.model_dump()
    )


def _stream_response_tokens(response_stream) -> Iterator[str]:
    for token in response_stream:
        if isinstance(token, str):
            yield _convert_token_to_packet(token)


def _convert_token_to_packet(token: str):
    token_packet = {
        "type": "token",
        "content": token
    }
    return json.dumps(token_packet) + "\n"


def _yield_token_packets_from_response_stream(response_stream: Iterator[str]):
    for token in response_stream:
        if token is None:
            continue
        yield _convert_token_to_packet(token)


def _assert_access_to_convo(conversation_id: str, email: str):
    conversation = inject.instance(DepContainer).convo_repo.get_conversation_by_id(conversation_id)
    if conversation.user_email != email:
        raise HTTPException(status_code=403, detail="User does not have access to this conversation.")
