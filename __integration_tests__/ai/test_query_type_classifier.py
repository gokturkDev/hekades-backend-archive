import pytest

from ai.models.gpt_models.gpt_model import OpenAIModel
from ai.query_type_classifier import QueryTypeClassifier
from ai.schemas import RouteName


@pytest.mark.parametrize("query,expected_route_name", [
    ("Diyabetli hastada dirençli HT ve anemi var. Bu hasta için hangi konsültasyonlar istenmelidir?", RouteName.CASE),
    ("Glisemi regülasyonunda obez hastalarda kaçınılması gereken ilaçlar hangileridir?", RouteName.INFORMATION),
    ("Gemfibrozil kullanan ve gfr 25 olan bir hastada repaglinid nasıl kullanılır?", RouteName.CASE),
    (
            "Diyabetli hastada Proteinüri söz konusu olduğunda diyabet tedavisi için ilk tercih nedir?",
            RouteName.CASE),
    (
            "Açlık kan şekeri 250 ve hedef kan glukozu 120 olan bir hastada İDF 20 ise bu hastada insülin dozu nasıl düzletilir?",
            RouteName.CASE),
    ("Hangi hastalarda natriüretik ölçülmelidir?", RouteName.INFORMATION),
    ("Beta hücre rezervi sınırda olan bir hastada tedavi planı nasıl olmalıdır?", RouteName.CASE),
    ("Tip 1 diyabette bazal insülin tedavisi planı nasıl yapılır?", RouteName.INFORMATION),
])
def test_query_type_analyzer(query: str, expected_route_name: RouteName):
    ai_model = OpenAIModel()
    times = 5
    for _ in range(times):
        route_name = QueryTypeClassifier.get_query_route_name(query, ai_model)
        assert route_name == expected_route_name
