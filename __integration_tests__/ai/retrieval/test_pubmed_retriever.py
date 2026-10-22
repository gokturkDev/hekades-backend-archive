from ai.models.gpt_models.gpt_model import OpenAIModel
from ai.retrieval.pubmed.pubmed_retriever import PubmedRetriever


class TestPubmedRetriever:
    def setup_method(self):
        self.ai_model = OpenAIModel()

    def test_retrieve(self):
        retriever = PubmedRetriever(self.ai_model)
        test_convo = """
        Diyabetli hastada ekokardiyografi ne zaman yaptırılmalıdır?
        {+}
        Diyabetli hastalarda ekokardiyografi yapılmasına dair endikasyonlar ve detaylar aşağıdaki şekildedir:

        - İstirahatte Nefes Darlığı veya Efor Kapasitesinde Bozulma: Diyabetli bireylerde istirahatte nefes darlığı yaşanması ya da yakın zamanda efor kapasitesinde belirgin bir azalma olması durumunda ekokardiyografi çekilmesi önerilir.
        
        - Hipervolemi Bulguları: Ödem, boyun venöz dolgunluğu gibi hipervolemi (vücutta fazla sıvı birikimi) belirtilerinin varlığı ekokardiyografi endikasyonudur.
        
        - Anjinal Yakınmalar: Anjina, yani göğüste ağrı ya da baskı hissi gibi kardiyak belirtiler varsa, ekokardiyografi yapılması gerekir.
        
        - Elektrokardiyografi (EKG) Bulguları: EKG’de dinamik iskemik değişikliklerin (kalp kasına yeterince kan gitmemesi durumu) veya aritmilerin (düzensiz kalp ritmi) saptanması durumunda ekokardiyografi yapılmalıdır.
        
        - Korunmuş Ejeksiyon Fraksiyonlu Kalp Yetersizliği Tanısı: Kalp yetersizliği belirtilerinin mevcut olmasıyla birlikte, korunmuş ejeksiyon fraksiyonu olan bireylerde ekokardiyografi, tanıyı netleştirmek için gereklidir.
        
        - Kanda Yüksek Natriüretik Peptid (NT-proBNP) Varlığı: Bu durumda, aşağıdaki EKG kriterlerinden en az birinin bulunması da ekokardiyografi yapılması açısından endikasyondur:
        
            - Sol ventrikül hipertrofisi
            - Atriyal dilatasyon (genişleme) bulguları
            - Sinüzal taşikardi (hızlı kalp atışı)
        
        
        - Kalp Yetersizliği Değerlendirmesi:
        
            - Efor kapasitesinde bozulma veya hacim fazlalığı düşünülen hastalarda natriüretik peptidler ölçülmelidir.
            - Sol ventrikül duvar hareketleri, kitlesi, sol atriyum boyutu, ejeksiyon fraksiyonları gibi parametreleri değerlendirmek için ekokardiyografi yapılmalıdır.
            - Kapak hastalıkları ve diyastolik disfonksiyon açısından Doppler parametreleri incelenmelidir.
            - Yeni Kardiyak Semptomlar:
                - Son bir yıl içinde ekokardiyografi yapılmamış veya yeni gelişen herhangi bir kardiyak semptomu olan hastalarda ekokardiyografi çekilmelidir.
        Diyabetli hastalarda rutin takipler, eşlik eden hastalık ve risk faktörlerinin belirlenmesi, komplikasyon taraması ve önleyici tedavi stratejilerinin uygulanması açısından ekokardiyografi büyük önem taşımaktadır. Bu durumlar sayesinde yapısal ve işlevsel kardiyak sorunları erkenden tespit edip, uygun tedavi planı oluşturulabilir.
        
        """
        articles = retriever.retrieve(test_convo)
        assert len(articles) > 0
