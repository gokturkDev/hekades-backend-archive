from abc import abstractmethod
import os
from typing import Optional
from pydantic import BaseModel, Field

from ai.models.standard_llm import StandardLLM
from core.lang.supported_lang import SupportedLanguages


class TagSelectorResponseModel(BaseModel):

    @abstractmethod
    def get_tags(self) -> list[str]:
        pass


class Tags(TagSelectorResponseModel):
    tag_list: list[str] = Field(
        default=[]
    )

    def get_tags(self):
        return self.tag_list


TAG_EXTRACTOR_PROMPT = """
You are given a text about selecting the best tags. Your job is to correctly extract the tags under the "# Best Tags" header and put them to the tag_list array.  
"""

with open(os.path.join(os.path.dirname(__file__), "taglist.txt"), 'r') as file:
    TAGS = file.read().split("\n")
    TAGS = [tag.strip() for tag in TAGS]

with open(os.path.join(os.path.dirname(__file__), "taglist_tr.txt"), 'r', encoding="utf-8") as file:
    TR_TAGS = file.read().split("\n")
    TR_TAGS = [tag.strip() for tag in TR_TAGS]

with open(os.path.join(os.path.dirname(__file__), "taglist_ar.txt"), 'r', encoding="utf-8") as file:
    AR_TAGS = file.read().split("\n")
    AR_TAGS = [tag.strip() for tag in AR_TAGS]

with open(os.path.join(os.path.dirname(__file__), "description.txt"), 'r') as file:
    lines = file.read().split("\n")
    DESCRIPTIONS = {}
    for i in range(len(lines)):
        line = lines[i]
        if not len(line) - len(line.lstrip()) and len(line):  # beginning is empty and line non-empty
            DESCRIPTIONS[line] = lines[i + 2]


class TagSelector:

    def __init__(self, logger, ai_model: StandardLLM, extractor_model: StandardLLM, tag_selection_prompt,
                 extraction_prompt: Optional[str] = TAG_EXTRACTOR_PROMPT,
                 response_model: TagSelectorResponseModel = Tags):
        self.logger = logger
        self.ai_model = ai_model
        self.extractor_model = extractor_model
        self.tag_selection_prompt = tag_selection_prompt
        self.extraction_prompt = extraction_prompt
        self.response_model = response_model

    async def get_tags(self, query: str, tags: Optional[list[str]] = None, use_descriptions: bool = False) -> list[str]:
        self.logger.info("Selecting tags...")
        self.logger.info("Here's the query:\n" + query)
        selection_prompt = self.tag_selection_prompt.format(
            tags=self.get_tag_format(tags, use_descriptions) if tags else "\n".join(TAGS))
        self.logger.info(f"Here's the selection prompt:\n{selection_prompt}")
        tag_reasoning = await self.ai_model.get_response(query, selection_prompt)
        self.logger.info("Here's the reasoning:\n" + tag_reasoning)

        tags = await self.extractor_model.get_response_with_response_model(user_msg=tag_reasoning,
                                                                           prompt=self.extraction_prompt,
                                                                           response_model=self.response_model)
        tag_list = tags.get_tags()
        self.logger.info("Here are the tags:\n" + str(tag_list))
        return tag_list

    def get_tag_description(self, tag: str):
        try:
            return DESCRIPTIONS[tag]
        except:
            return None

    def get_tag_format(self, tags, use_descriptions):
        if use_descriptions:
            forms = []
            for tag in tags:
                description = self.get_tag_description(tag)
                if description:
                    form = f"{tag}\n    {description}"
                    forms.append(form)
            return "\n".join(forms)
        else:
            return "\n".join(tags)

    def localize_tag(english_tag: str, localization_lang: SupportedLanguages):
        tag_index = TAGS.index(english_tag)
        if localization_lang == SupportedLanguages.arabic:
            return AR_TAGS[tag_index]
        elif localization_lang == SupportedLanguages.turkish:
            return TR_TAGS[tag_index]
        else:
            return TAGS[tag_index]
