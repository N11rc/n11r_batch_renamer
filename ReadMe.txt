=====================================================
BATCH RENAMER v01 HAKKINDA (README)
=====================================================

UYGULAMA ADI: Batch Renamer v01

YÖNTEM 1: OTOMATIK KURULUM (ÖNERİLEN)
-----------------------------------------------------
1. DMG dosyasını açın
2. "Install.command" dosyasına çift tıklayın
3. Şifrenizi girin (sistem güvenliği için gerekli)
4. Kurulum tamamlandı! Applications klasöründen açabilirsiniz.

YÖNTEM 2: MANUEL KURULUM
-----------------------------------------------------
1. DMG'yi açın
2. "n11r Batch Renamer.app" dosyasını Applications klasörüne sürükleyin
3. Terminal'i açın
4. Şu komutu kopyalayıp çalıştırın:
   
   xattr -cr "/Applications/n11r Batch Renamer.app"

5. Artık uygulamayı açabilirsiniz

İLK AÇILIŞ UYARISI
-----------------------------------------------------
Eğer "bozuk" veya "açılamıyor" hatası alırsanız:
1. Uygulamaya SAĞ TIKLAYIN (çift tıklama değil!)
2. "Aç" seçeneğini seçin
3. Çıkan uyarıda "Aç" butonuna basın
4. Sonraki açılışlarda normal çalışacaktır

NE İŞE YARAR?
-----------------------------------------------------
Batch Renamer v01, Blackmagic Design DaVinci Resolve yazılımının Media Pool (Medya Havuzu) içindeki klipleri toplu olarak yeniden adlandırmak için tasarlanmış bağımsız (standalone) bir masaüstü uygulamasıdır. 

Uygulama, Fusion penceresine bağımlı olmadan çalışır ve Resolve API'sini kullanarak adlandırma işlemlerini gerçekleştirir.

Temel Özellikler:
* Gelişmiş Şablonlama: Kliplerin Reel Adı, Timecode, Tarih ve Sayaçlar gibi metadata alanlarını kullanarak esnek adlandırma.
* Düzenli İfade (Regex) Desteği: Bul ve Değiştir bölümünde karmaşık metin kalıplarını bulma ve değiştirme yeteneği.


GELİŞTİRME ÖNERİLERİ VE İLETİŞİM
-----------------------------------------------------
Bu uygulama sürekli geliştirilmektedir. Eğer:
* Bir hata (bug) tespit ederseniz,
* Yeni bir özellik veya token (metadata alanı) eklenmesini isterseniz,
* Uygulamanın performansını artıracak bir öneriniz olursa,

Lütfen benimle iletişime geçmekten çekinmeyin. Kullanıcı geri bildirimleri, uygulamanın geleceği için çok değerlidir.

Geliştirici: Nehir Atabek
İletişim Kanalı: nehircanatabek@yandex.com

=====================================================



=====================================================
ABOUT BATCH RENAMER v01 (README)
=====================================================

APPLICATION NAME: Batch Renamer v01

METHOD 1: AUTOMATIC INSTALLATION (RECOMMENDED)

1. Open the DMG file
2. Double-click the "Install.command" file
3. Enter your password (required for system security)
4. Done! You can now launch it from the Applications folder.

METHOD 2: MANUAL INSTALLATION

1. Open the DMG
2. Drag the "n11r Batch Renamer.app" file into the Applications folder
3. Open Terminal
4. Copy and run the following command:
   xattr -cr "/Applications/n11r Batch Renamer.app"
5. You can now launch the app

FIRST LAUNCH WARNING
If you get a "damaged" or "can’t be opened" warning:

1. RIGHT-CLICK the app (not double-click!)
2. Select "Open"
3. In the dialog that appears, click "Open"
4. It will run normally on subsequent launches


WHAT DOES IT DO?
-----------------------------------------------------
Batch Renamer v01 is a standalone desktop application designed to batch rename clips within the Media Pool of Blackmagic Design's DaVinci Resolve software.

The application operates independently of the Fusion window and uses the Resolve API to execute renaming operations.

Key Features:
* Advanced Templating: Flexible renaming using metadata fields like Reel Name, Timecode, Date, and custom Counters.
* Regular Expression (Regex) Support: Ability to find and replace complex text patterns in the Find and Replace section.


DEVELOPMENT SUGGESTIONS AND CONTACT
-----------------------------------------------------
This application is under continuous development. If you:
* Encounter a bug,
* Wish to suggest a new feature or token (metadata field),
* Have a suggestion to improve the application's performance,

Please do not hesitate to contact me. User feedback is highly valuable for the future of the application.

Developer: Nehir Atabek
Contact Channel: nehircanatabek@yandex.com

=====================================================