EXAMPLE_1_QUERY = """
55 yaşında erkek hasta, Covid enfeksiyonu geçirmiş (1 ay önce), tedavi görmüş, iyileşmiş. Covid tedavisi ile eş zamanlı başlayan mide ağrısı tanımlıyor. Gastroenteroloji polikliniğine başvurmuş. PPI ve antiasid başlanmış. Gastroskopi yapılmış. Patolojik bulgu saptanmamış. Bilinen bir hastalığı yok. 8 ay önce diyabet tespit edilmiş, Hba1c % 8 miş. Yaşam tarzı değişiklikleri önerilmiş. Metformin 2x1 başlanmış. Pandemiden dolayı kontrole gelememiş. BKI: 25 kg/m2, Bel çevresi: 94 cm, TA: 125/ 82 mmHg, Nb: 84/dk/R, Diğer FM bulguları doğal. AKŞ: 118 mg/dl, TKŞ: 178mg/dl, Üre:38mg/dl, Krea:1,1mg/dl, LDL Kol: 98mg/dl, HDL: 47mg/dl, Hba1c: % 7.8, Vit B12: 148 mg/dl, Üst batın USG: Grade 1-2 hepatosteatoz, Diğer parametreler doğal. Metformin stoplandı. Vitamin B12 replasmanı başlandı. Yaşam tarzı önerileri tekrarlandı. Hangi ilacı verelim?
"""

EXAMPLE_1_COMPILATION = """
## Tip 2 Diyabet ve Tedavi Yaklaşımları
### Diyabetin Yönetimi ve Yaşam Tarzı Değişiklikleri
Tip 2 diyabetin yönetiminde yaşam tarzı değişiklikleri temel bir bileşendir. Diyabetin önlenmesi ve yönetiminde diyet ve fiziksel aktivitenin teşvik edildiği programlar, geleneksel yaklaşımlarla kıyaslandığında tip 2 diyabet ve diğer kardiyometabolik risk faktörlerini azaltmada etkili bulunduğu ifade edilmektedir [1]. Diyabetin önlenmesi için önerilen yaşam tarzı değişiklikleri arasında haftada en az 150-175 dakika egzersiz ve %5 ile %7 arası kilo kaybı hedefleyen kalori kısıtlaması içeren beslenme önerileri bulunmaktadır [1, 2]. 

### Farmakolojik Tedavi Seçenekleri
Tip 2 diyabet tedavisinde farmakolojik ajanların seçimi, bireyselleştirilmiş tedavi hedeflerine göre yapılmalıdır. Tedavi planının, kardiyovasküler ve renal komorbiditeler, etkinlik, hipoglisemi riski, kilo üzerindeki etkiler, maliyet ve erişim, advers reaksiyon riski ve bireysel tercihler dikkate alınarak düzenlenmesi gerektiği belirtilmektedir [3]. 

#### Metformin
Metformin, tip 2 diyabet tedavisinde ilk basamak tedavi olarak yaygın şekilde kullanılmaktadır. Metformin, yüksek etkinlik, düşük hipoglisemi riski ve nötr veya potansiyel kilo kaybı etkisi olduğu bildirilmektedir [29]. Ancak, metformin kullanımı sırasında B12 vitamini eksikliği görülebilir ve bu nedenle periyodik olarak B12 düzeylerinin kontrol edilmesi önerilmektedir [21, 22, 29].

#### GLP-1 Reseptör Agonistleri
GLP-1 reseptör agonistleri (GLP-1 RA), yüksek glisemik etkinlik ve kilo kaybı sağlama potansiyeli olduğu bildirilmektedir. Semaglutid ve tirzepatid gibi ajanlar, çok yüksek kilo kaybı etkinliği gösterirken, dulaglutid ve liraglutid gibi ajanların yüksek kilo kaybı etkinliği gösterdiği ifade edilmektedir [11]. GLP-1 RA'ların ayrıca kardiyovasküler ve renal faydalar sağlayabildiğine işaret edilmiştir [15, 41].

#### SGLT2 İnhibitörleri
SGLT2 inhibitörleri, orta ila yüksek glisemik etkinlik ve kilo kaybı sağlama potansiyeli olduğu bildirilmektedir. Bu ajanların ayrıca kardiyovasküler ve renal faydalar sağlayabildiği belirtilmektedir [29]. SGLT2 inhibitörlerinin etkinliğinin, düşük eGFR seviyelerinde azalabildiğine dikkat çekilmektedir [29].

### Hepatosteatoz ve Diyabet
Hepatosteatoz, tip 2 diyabetli hastalarda sık görülen bir durumdur ve bu hastalarda kardiyometabolik riskinin daha yüksek olduğu ifade edilmektedir [34, 53]. Pioglitazon ve GLP-1 RA'lar, biyopsi ile doğrulanmış NASH tedavisinde önerilmektedir [47]. Ayrıca, SGLT2 inhibitörlerinin de kardiyometabolik faydalar sağlayabildiği belirtilmektedir [47].

### Vitamin B12 Eksikliği
Metformin kullanımı sırasında B12 vitamini eksikliği görülebileceği ve bu durumun nöropati gibi komplikasyonlara yol açabileceğine dikkat çekilmektedir [20, 21, 22]. Bu nedenle, metformin kullanan hastalarda periyodik olarak B12 düzeylerinin kontrol edilmesi ve eksiklik durumunda replasman yapılması önerilmektedir [21, 22, 29].

### Sonuç
Tip 2 diyabet tedavisinde yaşam tarzı değişiklikleri temel bir bileşen olup, farmakolojik tedavi seçenekleri bireyselleştirilmiş tedavi hedeflerine göre belirlenmelidir. Metformin, GLP-1 RA'lar ve SGLT2 inhibitörleri gibi ajanlar, glisemik kontrol sağlama ve kardiyovasküler riskleri azaltma potansiyeline sahiptir. Hepatosteatoz ve B12 vitamini eksikliği gibi komorbid durumlar da tedavi planında dikkate alınmalıdır.
"""

EXAMPLE_2_QUERY = """
52 yaş, erkek, 22 yıllık tip 2 diyabet. Sık hipo ve hiperglisemileri var. Bazal bolus tedavi alıyor. AKŞ: 278 mg/dl, A1c: % 9.6. Bu hasta için tedavi nedir?
"""

EXAMPLE_2_COMPILATION = """
### Hastanın Durumu ve Başlangıç Değerlendirmesi
52 yaşında, erkek hasta 22 yıldır tip 2 diyabet hastasıdır. Sık hipoglisemi ve hiperglisemi atakları yaşamaktadır. Mevcut tedavisi bazal bolus insülin tedavisidir. Açlık kan şekeri (AKŞ) 278 mg/dl ve HbA1c seviyesi %9.6 olarak ölçülmüştür. Bu değerler, hastanın kan şekeri kontrolünün yetersiz olduğunu ve diyabet yönetiminde optimizasyon gerektiğini göstermektedir.

### Tedavi Yaklaşımları ve Öneriler

#### 1. Glisemik Yönetim
Glisemik yönetim, tip 2 diyabet tedavisinin temel taşlarından biri olduğu belirtilmektedir. Hastanın HbA1c seviyesi %9.6 olup, bu değer hedeflenen glisemik kontrolün oldukça üzerindedir. Bu durumda, tedavi stratejilerinin gözden geçirilmesi ve optimize edilmesi gerekmektedir. Glisemik yönetim için önerilen yaklaşımlar şunlardır:

- **Metformin veya Kombinasyon Tedavisi**: Metformin, tip 2 diyabet tedavisinde ilk basamak ilaç olarak önerilmektedir. Ancak, hastanın mevcut tedavisi bazal bolus insülin olduğundan, metformin ile birlikte diğer glukoz düşürücü ajanların kombinasyonunun düşünülebileceği ifade edilmektedir [1, 6].
- **GLP-1 Reseptör Agonistleri ve SGLT2 İnhibitörleri**: Bu ilaçların, yüksek glisemik etkinlikleri ve kardiyovasküler yararları nedeniyle tercih edilebileceği belirtilmektedir. GLP-1 RA ve SGLT2i, hipoglisemi riskini azaltma ve kilo yönetimi açısından da avantajlı olarak gösterilmektedir [1, 4, 6, 12].
- **İnsülin Tedavisinin Gözden Geçirilmesi**: Mevcut bazal bolus insülin tedavisinin etkinliği ve dozajı yeniden değerlendirilmelidir. İnsülin dozunun aşırı yüksek olması durumunda, hipoglisemi riskini azaltmak için doz ayarlamaları yapılabileceği belirtilmektedir [3, 6].

#### 2. Hipoglisemi Yönetimi
Hipoglisemi, tip 2 diyabet tedavisinde sık karşılaşılan bir komplikasyondur ve ciddi sonuçlara yol açabilir. Hipoglisemi yönetimi için öneriler şunlardır:

- **Eğitim ve Farkındalık**: Hastalar ve yakınları, hipoglisemi belirtileri, önleme yöntemleri ve tedavi hakkında bilgilendirilmelidir. Hipoglisemi risk faktörleri belirlenmeli ve bu risklerin minimize edilmesi gerektiği ifade edilmektedir [8, 15, 25].
- **Tedavi Stratejileri**: Hipoglisemi riskini azaltmak için düşük hipoglisemi riski taşıyan ilaçlar tercih edilmelidir. GLP-1 RA, SGLT2i ve DPP-4 inhibitörleri bu açıdan avantajlı olarak gösterilmektedir [12, 15, 17].
- **Kan Şekeri Takibi**: Hipoglisemi riskini azaltmak için kan şekeri düzeyleri sık sık izlenmeli ve özellikle gece saatlerinde kan şekeri ölçümleri yapılması önerilmektedir [8, 15].

#### 3. Kardiyovasküler ve Renal Risk Yönetimi
Tip 2 diyabet hastalarında kardiyovasküler ve renal risklerin yönetimi büyük önem taşır. Bu risklerin azaltılması için öneriler şunlardır:

- **Kardiyovasküler Risk Azaltıcı İlaçlar**: GLP-1 RA ve SGLT2i, kardiyovasküler hastalık riskini azaltmada etkilidir. Bu ilaçların, özellikle kardiyovasküler hastalık öyküsü olan veya yüksek risk taşıyan hastalarda tercih edilmesi önerilmektedir [4, 9, 16].
- **Renal Koruma**: SGLT2i grubu ilaçların, kronik böbrek hastalığı olan hastalarda böbrek fonksiyonlarını korumada etkili oldukları ve bu ilaçların böbrek fonksiyonlarını iyileştirme ve kardiyovasküler olayları azaltma potansiyeline sahip olduğu belirtilmektedir [4, 16].

#### 4. Yaşam Tarzı Değişiklikleri ve Eğitim
Yaşam tarzı değişiklikleri ve hasta eğitimi, tip 2 diyabet yönetiminde kritik öneme sahiptir. Öneriler şunlardır:

- **Beslenme ve Egzersiz**: Akdeniz diyeti, düşük karbonhidratlı diyet ve DASH diyeti gibi beslenme modelleri önerilebilir. Haftada en az 150 dakika orta şiddette egzersiz yapılmasının teşvik edilmesi önerilmektedir [2, 10, 26].
- **Diyabet Eğitimi**: Hastaların, diyabet yönetimi, kan şekeri takibi, insülin kullanımı ve hipoglisemi yönetimi konularında düzenli olarak eğitilmesinin gerekliliği vurgulanmaktadır [21].

### Sonuç
52 yaşındaki erkek hastanın tip 2 diyabet yönetimi, glisemik kontrolün optimize edilmesi, hipoglisemi riskinin azaltılması, kardiyovasküler ve renal risklerin yönetimi ve yaşam tarzı değişiklikleri ile desteklenmelidir. Tedavi planı, hastanın bireysel ihtiyaçlarına göre düzenlenmeli ve düzenli aralıklarla gözden geçirilmelidir. Bu süreçte, hasta eğitimi ve destek programları da önemli bir rol oynamaktadır. 


"""

EXAMPLE_3_QUERY = """
68 yaşında Erkek hasta, 18 yıldır diyabetik, Glimeprid ve metformin kullanmakta, 15 gün önce yol yürürken nefes darlığı olması üzerine gittiği doktor tarafından çekilen EKG de yeni gelişmiş bir sol dal bloğu saptanıyor. Geçirilmiş sessiz MI, kalp yetersizliği olduğu saptanıyor, LAD ye stent takılıyor ve medikal tedavisi düzenleniyor. Losartan 50 + HCTZ 12,5 mg 1x1, Sprinolacton 25 1x1, Dilatrent 12,5 2x1, Atorvastatin 40mg 1x1, ASA 100mg 1x1, Klopidrogel 1x1 başlanıyor. BKI: 29kg/m2, TA: 130/80 mmHg, Nb: 80/dk/R, Her iki akciğer bazalinde minimal krepitan ral mevcut, Pretibial ödem 1+, Tüm odaklarda 1/6 sistolik üfürüm, Diğer FM bulguları doğal. AKŞ: 178 mg/dl, GFR: 55 ml/dl/1.73 m2, Total Kol: 203 mg/dl, HDL Kol: 44 mg/dl, LDL: 125 mg/dl, Trig: 171 mg/dl, Hba1C: %8.4. Bu hasta için hipertansiyon yönetimi nasıl yapılır?
"""

EXAMPLE_3_COMPILATION = """
### Giriş
68 yaşında erkek hasta, 18 yıldır diyabetik olup Glimeprid ve metformin kullanmaktadır. 15 gün önce yol yürürken nefes darlığı şikayetiyle doktora başvurmuş ve çekilen EKG'de yeni gelişmiş bir sol dal bloğu saptanmıştır. Geçirilmiş sessiz miyokard enfarktüsü (MI) ve kalp yetersizliği tanısı konulmuş, LAD'ye stent takılmış ve medikal tedavisi düzenlenmiştir. Mevcut tedavisi Losartan 50 + HCTZ 12,5 mg 1x1, Spironolakton 25 mg 1x1, Dilatrent 12,5 mg 2x1, Atorvastatin 40 mg 1x1, ASA 100 mg 1x1, Klopidogrel 1x1 şeklindedir. Fizik muayene bulguları arasında BKI: 29 kg/m2, TA: 130/80 mmHg, Nb: 80/dk/R, her iki akciğer bazalinde minimal krepitan ral ve pretibial ödem 1+ bulunmaktadır. Laboratuvar sonuçları AKŞ: 178 mg/dl, GFR: 55 ml/dk/1.73 m2, Total Kol: 203 mg/dl, HDL Kol: 44 mg/dl, LDL: 125 mg/dl, Trig: 171 mg/dl, Hba1C: %8.4 olarak saptanmıştır.

### Hipertansiyon Yönetimi

#### Yaşam Tarzı Değişiklikleri
Hipertansiyon yönetiminde ilk adım yaşam tarzı değişiklikleridir. Bu değişiklikler arasında günlük tuz alımının 2-2,4 gram ile sınırlanması, günde 6 saatten fazla uyku, dengeli beslenme, sürdürülebilir kilo kaybı (%5-10), haftada en az 4 gün 30-60 dakika orta düzeyde fiziksel aktivite, alkol ve sigaranın bırakılması ve stresle mücadele yer almaktadır [26, 27, 50]. Bu yaşam tarzı değişiklikleri, kan basıncının kontrol altına alınmasında önemli rol oynar ve ilaç tedavisinin etkinliğini artırır.

#### İlaç Tedavisi
Hastanın mevcut ilaç tedavisi Losartan + HCTZ, Spironolakton, Dilatrent, Atorvastatin, ASA ve Klopidogrel içermektedir. Bu tedavi rejimi, hipertansiyon ve kalp yetersizliği yönetiminde uygun bir kombinasyon sunmaktadır. Ancak, hastanın kan basıncı hedeflerine ulaşamaması durumunda tedavi planının gözden geçirilmesi gerekebilir.

##### Monoterapi ve İkili Tedavi
Kan basıncı başlangıcı 140-159/90-99 mmHg olan hastalar monoterapi ile tedavi edilirken (ACE-i / ARB), kan basıncı başlangıcı ≥160/100 mmHg olan hastalar için ikili tedavi (ACE-i veya ARB ve Diüretik / KKB) uygulanır [26, 27, 30]. Bu hastada mevcut tedavi rejimi zaten ikili tedavi içermektedir (Losartan + HCTZ ve Spironolakton).

##### Üçüncü İlaç Eklenmesi
3-4 haftalık tedaviye rağmen kan basıncı hedefe ulaşamazsa, ikinci ve üçüncü bir ilaç eklenir (ACE-i veya ARB ve KKB veya diüretik) [26, 27, 30]. Bu aşamada, hastalarda ilaç intoleransı varsa tedavi değişikliği yapılabilir. Mevcut tedavi rejimi göz önüne alındığında, üçüncü bir ilaç olarak KKB eklenmesi düşünülebilir.

##### Dirençli Hipertansiyon
Dirençli hipertansiyon varsa ve MRA grubu bir ilaca ihtiyaç duyuluyorsa tedaviye eklenebilir. Ayrıca, ilaç yetersizliği varsa hasta daha üst düzey bir merkeze sevk edilmelidir [26, 27, 30]. Bu hastada Spironolakton (MRA) zaten tedavi rejiminde bulunmaktadır.

#### Kardiyovasküler ve Renal Risk Yönetimi
Diyabetli hastalarda hipertansiyon yönetiminde kardiyovasküler ve renal risklerin azaltılması büyük önem taşır. Bu amaçla, SGLT2 inhibitörleri gibi ilaçlar eklenebilir. SGLT2 inhibitörleri, kan basıncını düşürür ve tuz duyarlılığını azaltır [26, 27, 30]. Ayrıca, bu ilaçlar kalp yetersizliği nedeniyle hastaneye yatış riskini ve majör kardiyovasküler olay riskini azaltır [5, 14, 15].

#### İlaçların Dozlarının Optimizasyonu
Beta-bloker, RAS Blokeri ve statin tedavilerinin dozlarının optimal olup olmadığı gözden geçirilmelidir [13]. Hipertansif hastalarda RAS blokerleri özellikle sol ventrikül hipertrofisi ve proteinürisi varsa ön planda düşünülmeli ve sabit doz kombinasyon tedavisine erken dönemden itibaren geçilmelidir [13]. Diyabetli hastalarda yüksek yoğunluklu statinler (Atorvastatin 40-80 mg, Rosuvastatin 20-40 mg) kullanılmalı, hedef LDL kolesterol değerine ulaşılamadığında tedaviye Ezetimib eklenmelidir [13].

### Sonuç
68 yaşında diyabetik erkek hastanın hipertansiyon yönetiminde yaşam tarzı değişiklikleri, mevcut ilaç tedavisinin gözden geçirilmesi ve gerekirse ek ilaçların eklenmesi önemlidir. Kardiyovasküler ve renal risklerin azaltılması için SGLT2 inhibitörleri gibi ilaçlar düşünülebilir. İlaç dozlarının optimizasyonu ve düzenli izlem ile hastanın kan basıncı hedeflerine ulaşması sağlanabilir. Bu süreçte, hasta eğitimi ve destek programları da önemli bir rol oynamaktadır.
"""
