from business.usecase.conversation.use_case_with_convo_repo import UsecaseWithConversationRepository


class GetLatestMessageOfConversationUsecase(UsecaseWithConversationRepository):

    def execute(self, convo_id: str):
        return self._repo.get_latest_message(convo_id)
