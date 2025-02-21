
# Hand-DJ

Hand DJ, el hareketlerini kullanarak sesi kontrol eden bir ses görselleştirme uygulamasıdır. OpenCV, MediaPipe ve PyAudio gibi kütüphaneler kullanılarak geliştirilmiştir.


## Özellikler

- Ellerin Takibi: MediaPipe kullanarak sağ ve sol elin başparmak ve işaret parmak uçlarını algılar.
- Ses Kontrolü: İki el arasındaki mesafeye göre sesi kontrol eder (uzaklık arttıkça ses artar, azaldıkça ses azalır).
- Gerçek Zamanlı Ses Görselleştirme: Ses dalgalarını tespit edilen el konumlarına göre ekrana yansıtır.
- MP3 Desteği: MP3 formatındaki ses dosyalarını WAV formatına çevirerek oynatır.
- Gerçek Zamanlı Video İşleme: OpenCV ile kameradan gelen görüntüler işlenir.
  
## Gereksinimler

Bu projeyi çalıştırmadan önce aşağıdaki bağımlılıkları yüklemeniz gerekmektedir:

```
pip install opencv-python numpy pyaudio wave pydub mediapipe
```
  
## Kullanım/Örnekler

+ Ses Dosyanızı Belirleyin: ```mp3_filename``` değişkenine MP3 formatındaki ses dosyanızın yolunu yazın.
+ Kodu Çalıştırın:
```
python hand-DJ.py
```
## El Hareketleriyle Kontrol:

- İki el arasındaki mesafeyi artırarak sesi yükseltin.

- Mesafeyi azaltarak sesi kısın.

- Çizilen ses dalgalarını ve ellerinizin hareketlerini ekranda gözlemleyin.

- ```q``` tuşuna basarak uygulamadan çıkabilirsiniz.

  
## Dosya Açıklamaları

- ```hand-DJ.py```: Uygulamanın ana kod dosyası.

- ```*.py```: Uygulamanın geliştirilirken hatalar sonucu ortaya çıkan veya amaç olmasa bile kullanılabilir versiyonları.

- ```temp.wav```: MP3 dosyasının geçici olarak çevrildiği WAV dosyası.

## Çalışma Mantığı
- OpenCV kullanarak kameradan gelen görüntüyü işler.

- MediaPipe ile el hareketleri algılanır ve başparmak ile işaret parmak arasındaki mesafe hesaplanır.

- PyAudio ile ses dosyası oynatılır ve ses seviyesi el hareketlerine göre ayarlanır.

- Gerçek zamanlı olarak ses dalgaları ekrana çizilir.
## Lisans

Bu proje [MIT](https://choosealicense.com/licenses/mit/) Lisansı altında dağıtılmaktadır.

Copyright © 2025

![Logo](https://github.com/Bavsimus/Bavsimus/blob/main/logo.png?raw=true)

    