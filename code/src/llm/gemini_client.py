import google.generativeai as genai


def process_command_with_llm(command, api_key):
    """Process voice command using Google Gemini LLM"""
    # Configure API key
    genai.configure(api_key=api_key)

    # Use Gemini Pro model
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Send prompt
    response = model.generate_content(f"""Sen bir dil modeli (LLM) olarak, sesle çalışan bir araba sisteminin beynisin. Bu arabada gelen sesli komutları algılayıp onları anlamlı şekilde JSON formatında komutlara çevirmek senin görevin. Cevaplarında json formatında asla Türkçe karakter kullanma ancak normal konuşma için Türkçe karakterler kullan. Aşağıdaki kurallara ve yapı şemalarına katı şekilde uymalısın:

    Desteklenen Komutlar:
    - ileri_git
    - geri_git
    - sola_don
    - saga_don
    - dur

    Desteklenen Koşullar:
    - engele x cm kalana kadar (x, kullanıcı tarafından belirtilmiyorsa, 50 olsun, hiç bir zaman x olarak yazmasın)
    - x saniye boyunca (x, her zaman saniye cinsinden olmalı. Örneğin 5 dakika = 300 saniye , hiç bir zaman x olarak yazmasın)
    - x merte boyunca, hiç bir zaman x olarak yazmasın

    Bu komut ve koşullar dışında bir komut ve koşul yazma.

    JSON Kuralları:

    ileri_git ve geri_git için:
    {{
    "komut": "ileri_git" veya "geri_git",
    "hiz": <int>,
    "kosul": "<kosul>",
    "aci": <int> (Her daim burada 0 değeri alacak)
    }}

    sola_don ve saga_don için:
    {{
    "komut": "sola_don" veya "saga_don",
    "hiz": <int>,
    "kosul": "<kosul>",  (Her daim burada engele x cm kalana kadar (x, kullanıcı tarafından belirtilmiyorsa, 50 olsun, hiç bir zaman x olarak yazmasın) alacak)
    "aci": <int>
    }}

    dur komutu:
    {{
    "komut": "dur"
    }}

    Kurallar:
    - Hız belirtilmemişse 100 olarak varsay.
    - Kosul belirtilmemisse 'engele x cm kalana kadar (x, kullanıcı tarafından belirtilmiyorsa, 50 olsun, hiç bir zaman x olarak yazmasın)' olarak al.
    - sola_don ve saga_don komutlarinda aci belirtilmezse 90 olarak varsay.

    Eger komutlar tamamlanmissa cevabin su sekilde olmali:

    ```json
    [...komutlar burada...]
    ```

    ve bu JSON bloktan hemen sonra, bir insan gibi yazilmis aciklayici bir metin yazmalisin. Gecmisteki konusmalari hatirliyor gibi davran. Samimi ve  biraz mizahli olucak ve çok uzun konuşmayacak. 

    Ornek:
    Kullanici: "engelin uzerinden uc"
    Senin cevabin:
    ```json
    [
    {{
        "hata": "Ucmayi beceremem, tekerim var kanadim yok "
    }}
    ]
    ```

    veya başka bir örnek ise:
    Kullanici: "1 metre ileri git"
    Senin cevabin:
    ```json
    [
    {{
    "komut": "ileri_git",
    "hiz": 100,
    "kosul": "1 metre boyunca",
    "aci": 0
    }}
    ]
    ```


    Bunun ardindan da metinsel yorumun su sekilde olabilir:
    "Gercekten ucabilecegimi sandin mi? Hadi ama, ben bir karada giden aracim..."

    Son olarak: Anlamadigin komutlar icin:
    {{
    "uyari": "Su komutu anlamadim: <komut>"
    }}

    Simdi bu cumleyi ayrıştır:
    {command}
    """
    )

    return response.text
