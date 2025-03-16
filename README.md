# HandDJ

HandDJ, el hareketleriyle müzik çalmayı ve kontrol etmeyi sağlayan bir Python uygulamasıdır. OpenCV ve MediaPipe kullanarak el hareketlerini algılar ve belirlenen hareketlerle şarkıları oynatır veya durdurur.

## 🚀 Özellikler
- **El hareketleri ile kontrol:** İşaret ve başparmak ile yapılan pinch hareketiyle müziği başlat veya durdur.
- **Gerçek zamanlı kamera işleme:** OpenCV kullanarak anlık görüntü işleme.
- **Ses kontrolü:** PyAudio ile müzik çalma ve durdurma.

## 📦 Kurulum

Öncelikle, bağımlılıkları yüklemek için aşağıdaki komutu çalıştırın:

```bash
pip install opencv-python mediapipe numpy pyaudio wave pydub
```

Ardından, MediaPipe ve diğer bağımlılıkları içeren kodu çalıştırmak için projenizi klonlayın:

```bash
git clone https://github.com/Bavsimus/hand-dj.git
cd hand-dj
```

## 🔧 Kullanım

Python scriptini çalıştırmak için:

```bash
python main.py
```

Kamera açıldıktan sonra:
- **Parmaklarınızı kıstığınızda** müzik çalmaya başlar.
- **Tekrar kıstığınızda** müzik durur.
- **'Q' tuşuna basarak** uygulamayı kapatabilirsiniz.

## 📂 Dosya Yapısı

Kendi şarkılarınızın yolunu ve isimlerini yazmayı unutmayın.
```bash
TEXTS = ["sickomode", "dans et", "boiler", "check my brain", "lazy song"]
SONG_PATHS = {
    "sickomode": r"C:\\Users\\USER\\Music\\cropped\\sickomode.wav",
    "dans et": r"C:\\Users\\USER\\Music\\cropped\\danset.wav",
    "boiler": r"C:\\Users\\USER\\Music\\cropped\\boiler.wav",
    "check my brain": r"C:\\Users\\USER\\Music\\cropped\\checkmybrain.wav",
    "lazy song": r"C:\\Users\\USER\\Music\\cropped\\lazysong.wav"
}
```

Önemli scriptler:
```
hand-gesture-dj/
│── main.py           # Ana betik, kamerayı açar ve işleme başlar.
│── handMenu.py       # Menü için el hareketlerini algılar.
│── handDjNoCam.py    # DJ kontrolü için el hareketlerini işler.
│── ...    # Diğer.
```

## 🤖 Kullanılan Teknolojiler
- **Python**
- **OpenCV** - Gerçek zamanlı görüntü işleme.
- **MediaPipe** - El hareketlerini algılama.
- **PyAudio & pydub** - Ses işleme ve müzik çalma.

## 📜 Lisans
Bu proje MIT Lisansı ile sunulmaktadır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasını inceleyebilirsiniz.

---

💡 **Geri bildirim ve katkılarınızı bekliyoruz!** Eğer projeyi beğendiyseniz ⭐ bırakmayı unutmayın! 😊

