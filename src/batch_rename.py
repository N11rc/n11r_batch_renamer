import os, sys, json, datetime, time
import re 

def resource_path(relative_path):
    """
    PyInstaller'ın paketlenmiş ortamında dosyaların (örneğin logo) 
    doğru yolunu bulur. Normal ortamda ise düz yolu kullanır.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller'ın geçici klasör yolu
        return os.path.join(sys._MEIPASS, relative_path)
    # Normal Python ortamı
    return os.path.join(os.path.abspath("."), relative_path)

try:
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, 
        QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, 
        QLabel, QGroupBox, QSpacerItem, QSizePolicy, QHeaderView, QCompleter,
        QMessageBox, QMenu, QTextEdit, QFileDialog, QScrollArea, QFrame,
        QTabWidget, QWidget 
    )
    from PyQt6.QtCore import Qt, QTimer, QStringListModel, QSettings 
    from PyQt6.QtGui import QColor, QFont, QIcon 
except ImportError:
    print("HATA: PyQt6 modülü bulunamadı. Lütfen 'pip3 install PyQt6' ile kurun.")
    sys.exit(1)

SETTINGS_KEY_GROUP = "BatchRenamerSettings"
SETTINGS_KEY_TEMPLATE = "RenameTemplate"
SETTINGS_KEY_COUNTER_START = "CounterStart"
SETTINGS_KEY_COUNTER_PAD = "CounterPad"
SETTINGS_KEY_COUNTER_STEP = "CounterStep"
SETTINGS_KEY_TR_MAP = "TrMap"
SETTINGS_KEY_SPACE_US = "SpaceToUnderscore"
SETTINGS_KEY_TO_LOWER = "ToLower"
SETTINGS_KEY_LANGUAGE = "Language" 
SETTINGS_KEY_REGEX      = "UseRegex" 

DEFAULT_TEMPLATE    = "" 
DEFAULT_COUNTER_START = 1
DEFAULT_COUNTER_PAD   = 3
DEFAULT_COUNTER_STEP  = 1 
DEFAULT_TR_MAP        = True
DEFAULT_SPACE_US      = True
DEFAULT_TO_LOWER      = False
DEFAULT_REGEX           = False 
DEFAULT_CLEAN_AFTER_APPLY = True 
DEFAULT_LANGUAGE      = "tr" 

TOKEN_MAP_DATA = {
    "%Counter":    ("counter", "Sayıcı (Pad, Start, Step arayüzden alınır)", "Counter (Pad, Start, Step taken from UI)"),
    "%ClipName":   ("orig", "Orijinal Clip/Veritabanı Adı (uzantı dahil)", "Original Clip/Database Name (incl. extension)"),
    "%FileName":   ("filename", "Diskteki Orijinal Dosya Adı (uzantı dahil)", "Original File Name on Disk (incl. extension)"), 
    "%NameOnly":   ("extless", "Uzantısız Clip/Veritabanı Adı", "Clip/Database Name without Extension"),
    "%Reel":       ("reel", "Klibin Reel/Tape Adı", "Clip's Reel/Tape Name"),
    "%TCStart":    ("tcstart", "Klibin Başlangıç Timecode'u", "Clip's Start Timecode"),
    "%MarkerName": ("marker_name", "Klibin başlangıcındaki ilk markerın adı", "Name of the first marker at the clip's start"), 
    "%Date":       ("date", "YYYYMMDD formatında geçerli tarih", "Current Date in YYYYMMDD format"),
    "%Time":       ("time", "HHMMSS formatında geçerli saat", "Current Time in HHMMSS format"),
    "%FPS":        ("fps", "Klibin kare hızı", "Clip's Frame Rate (FPS)"),
    "%Res":        ("res", "Klibin çözünürlüğü", "Clip's Resolution"),
}
TOKEN_LIST = list(TOKEN_MAP_DATA.keys()) 

try:
   
    RESOLVE_API_PATH = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"

    
    if os.path.isdir(RESOLVE_API_PATH) and RESOLVE_API_PATH not in sys.path:
        sys.path.append(RESOLVE_API_PATH)

    import DaVinciResolveScript as bmd
    resolve = bmd.scriptapp("Resolve")
except ImportError:
    if not os.environ.get("DAVINCI_RESOLVE_SCRIPT_API"):
        print("HATA: DaVinciResolveScript modülü bulunamadı.")
    resolve = None

pm = None
project = None
mp = None

if resolve:
    pm = resolve.GetProjectManager()
    if pm:
        project = pm.GetCurrentProject()
        if project:
            mp = project.GetMediaPool()
        
if not resolve: print("UYARI: DaVinci Resolve API'ye bağlanılamadı. Uygulama sadece önizleme modunda çalışacaktır.")


LANG_MAP = {
    "tr": {
        "title": "n11r Batch Renamer v01", 
        "scope_group": "Kapsam",
        "chk_selected": "Sadece seçili klipler",
        "btn_refresh": "Listeyi Yenile",
        "btn_metadata": "Meta Veri Raporu",
        "rename_group": "Yeniden Adlandırma Ayarları",
        "tpl_label": "Adlandırma Şablonu:",
        "info_label": "Tokenları eklemek için metin kutusuna '%' yazın VEYA 'Token Ekle' butonunu kullanın.",
        "btn_insert_token": "Token Ekle",
        "btn_save_template": "Ayarları Kaydet",
        "btn_load_template": "Ayarları Yükle",
        "count_start": "Sayıcı Başlangıç:",
        "count_pad": "Pad (Basamak):",
        "count_step": "Adım (Step):",
        "chk_tr": "Karakterleri Çevir",
        "chk_space": "Boşlukları '_' yap",
        "chk_lower": "Küçük harfe çevir",
        "chk_dry": "Dry Run (Sadece Önizleme)",
        "fr_group": "Bul ve Değiştir (Token Uygulamasından Sonra)",
        "fr_find": "Bul (Find):",
        "fr_replace": "Değiştir (Replace):",
        "chk_case_sensitive": "Büyük/küçük harf duyarlı yap",
        "chk_regex": "Regex (Düzenli İfade) Kullan", 
        "preview_label": "Önizleme (Uygulanacak Değişiklikler):",
        "header_old": "Eski Ad",
        "header_new": "Yeni Ad",
        "btn_preview": "Önizleme Oluştur",
        "btn_apply": "Uygula",
        "chk_clean_after_apply": "Uygulamadan sonra listeyi temizle",
        "btn_close": "Kapat",
        "lang_label": "Dil:     ",
        "btn_help": "Yardım",
        "btn_about": "Hakkında",
        "msg_saved": "Adlandırma şablonu ve ayarları kaydedildi.",
        "msg_loaded": "Adlandırma şablonu ve ayarları yüklendi.",
        "err_no_resolve": "DaVinci Resolve'a bağlanılamadığı için değişiklikler uygulanamıyor.",
        "err_no_clip": "Uygulama iptal edildi: İşlenecek klip yok.",
        "msg_dry_run": "Dry Run (önizleme) aktif. Değişiklikler uygulanmadı.",
        "msg_success": "İŞLEM SONUÇLANDI: {count_total} klip denendi, {count_success} klip adı güncellendi.",
        "no_clips_in_list": "(İşlenebilir Klip Yok)",
        "cleaned_after_apply": "(Liste Uygulamadan Sonra Temizlendi)",
        "metadata_viewer_title": "Seçili Kliplerin Meta Veri Raporu",
        "metadata_btn_txt": "TXT Olarak Kaydet",
        "metadata_btn_csv": "CSV Olarak Kaydet",
        "metadata_btn_close": "Kapat",
        "err_file_save": "Dosya kaydedilirken bir hata oluştu: {error}",
        "metadata_report_empty": "İşlenecek klip bulunamadı.",
        "about_title": "n11r - Batch Renamer",
        "help_title": "Yardım ve Kılavuz",
        "help_description": "Bu araç, DaVinci Resolve Media Pool'daki seçili klipleri toplu olarak yeniden adlandırmanıza olanak tanır.",
        "help_tab_tokens": "Tokenlar ve Açıklamalar",
        "help_tab_guide": "Kullanım Kılavuzu",
        "guide_text": """
        <h3>Kullanım Adımları:</h3>
        <ol>
            <li>**Kapsam Belirleme:** Media Pool'da adlandırmak istediğiniz klipleri seçin ve **'Sadece seçili klipler'** kutucuğunu işaretleyin (ya da tüm klipleri adlandırın).</li>
            <li>**Listeyi Yenile:** Listeyi Media Pool'daki güncel kliplerle doldurmak için **'Listeyi Yenile'** butonuna tıklayın.</li>
            <li>**Şablon Oluşturma:** **'Adlandırma Şablonu'** alanına istediğiniz yapıyı yazın. Tokenları eklemek için '%' yazmaya başlayın veya **'Token Ekle'** butonunu kullanın. Örnek: <code>SHOT_{Counter}_{NameOnly}</code></li>
            <li>**Sayaç Ayarları:** <code>%Counter</code> kullanıyorsanız, Başlangıç, Basamak (Pad) ve Adım (Step) değerlerini ayarlayın.</li>
            <li>**Ön İşleme:** Türkçe karakter çevirisi, boşlukları alt çizgi yapma ve küçük harfe çevirme seçeneklerini etkinleştirin.</li>
            <li>**Bul ve Değiştir:** Tokenlar uygulandıktan sonra metinde son düzeltmeleri yapmak için bu bölümü kullanın. **'Regex (Düzenli İfade) Kullan'** kutucuğunu işaretlerseniz, gelişmiş kalıp eşleştirme yapabilirsiniz.</li>
            <li>**Önizleme:** **'Önizleme Oluştur'** butonuna tıklayarak değişikliklerinizi kontrol edin. Mavi renkle vurgulananlar değişecek olanlardır.</li>
            <li>**Uygulama:** Her şey doğruysa, **'Uygula'** butonuna tıklayarak adlandırma işlemini Media Pool'a yansıtın.</li>
            <li>**Dry Run:** Eğer 'Dry Run' işaretliyse, Önizleme aktif kalır ve 'Uygula' butonu hiçbir değişiklik yapmaz.</li>
        </ol>
        <br>
        <h4>Regex (Düzenli İfade) Kılavuzu:</h4>
        <p>Regex, metin içinde karmaşık kalıpları aramak ve değiştirmek için kullanılır. Tekrarlayan sayıları silmek gibi işlemler için çok güçlüdür. **'Regex Kullan'** kutucuğunu işaretlemeyi unutmayın.</p>
        
        <p><strong>Örnek Senaryo:</strong> <code>a_0010_0010</code> klip adını <code>a_0010</code> yapmak.</p>
        <ul>
            <li>**Regex Kutucuğu:** **✓ İşaretli**</li>
            <li>**Bul (Find):** <code>(.*)_(\\d+)_\\2</code></li>
            <li>**Değiştir (Replace):** <code>\\1_\\2</code></li>
        </ul>
        <p><strong>Açıklama:</strong></p>
        <ul>
            <li><code>(.*)</code>: Klip adının başındaki sabit kısmı (bu örnekte <code>a</code>) yakalar ve bunu **Grup 1** (<code>\\1</code>) olarak kaydeder.</li>
            <li><code>(\\d+)</code>: İlk sayı dizisini (<code>0010</code>) yakalar ve bunu **Grup 2** (<code>\\2</code>) olarak kaydeder.</li>
            <li><code>_\\2</code>: Geriye kalan alt çizgiyi ve tekrarlayan sayıyı (<code>_0010</code>) eşleştirir ve değiştirme işleminde yok sayılmasını sağlar.</li>
            <li>**Sonuç:** Sadece Grup 1 ve Grup 2'nin arasına alt çizgi eklenerek (<code>\\1_\\2</code>) yeni ad oluşturulur.</li>
        </ul>
        """
    },
    "en": {
        "title": "n11r Batch Renamer v01", 
        "scope_group": "Scope",
        "chk_selected": "Only selected clips",
        "btn_refresh": "Refresh List",
        "btn_metadata": "Metadata Report",
        "rename_group": "Renaming Settings",
        "tpl_label": "Rename Template:",
        "info_label": "Type '%' in the text box or use the 'Insert Token' button to add tokens.",
        "btn_insert_token": "Insert Token",
        "btn_save_template": "Save Settings",
        "btn_load_template": "Load Settings",
        "count_start": "Counter Start:",
        "count_pad": "Pad:",
        "count_step": "Step:",
        "chk_tr": "Convert Characters",
        "chk_space": "Replace spaces with '_'",
        "chk_lower": "Convert to lowercase",
        "chk_dry": "Dry Run (Preview Only)",
        "fr_group": "Find and Replace (After Token Application)",
        "fr_find": "Find:",
        "fr_replace": "Replace:",
        "chk_case_sensitive": "Case sensitive",
        "chk_regex": "Use Regex (Regular Expression)", 
        "preview_label": "Preview (Changes to be Applied):",
        "header_old": "Old Name",
        "header_new": "New Name",
        "btn_preview": "Generate Preview",
        "btn_apply": "Apply",
        "chk_clean_after_apply": "Clear list after applying",
        "btn_close": "Close",
        "lang_label": "Language:",
        "btn_help": "Help",
        "btn_about": "About",
        "msg_saved": "Renaming template and settings saved.",
        "msg_loaded": "Renaming template and settings loaded.",
        "err_no_resolve": "Cannot apply changes: Could not connect to DaVinci Resolve.",
        "err_no_clip": "Application aborted: No clips to process.",
        "msg_dry_run": "Dry Run is active. Changes were not applied.",
        "msg_success": "OPERATION COMPLETE: {count_total} clips attempted, {count_success} clip names updated.",
        "no_clips_in_list": "(No Processable Clips)",
        "cleaned_after_apply": "(List Cleared After Apply)",
        "metadata_viewer_title": "Selected Clips Metadata Report",
        "metadata_btn_txt": "Save as TXT",
        "metadata_btn_csv": "Save as CSV",
        "metadata_btn_close": "Close",
        "err_file_save": "An error occurred while saving the file: {error}",
        "metadata_report_empty": "No clips found to process.",
        "about_title": "About: n11r Batch Renamer",
        "help_title": "Help and Guide",
        "help_description": "This tool allows you to batch rename selected clips in the DaVinci Resolve Media Pool.",
        "help_tab_tokens": "Tokens and Descriptions",
        "help_tab_guide": "User Guide",
        "guide_text": """
        <h3>Usage Steps:</h3>
        <ol>
            <li>**Set Scope:** Select the clips you want to rename in the Media Pool and check the **'Only selected clips'** box (or rename all clips).</li>
            <li>**Refresh List:** Click **'Refresh List'** to populate the list with the current clips from the Media Pool.</li>
            <li>**Create Template:** Type the desired structure into the **'Rename Template'** field. Start typing '%' or use the **'Insert Token'** button to add tokens. Example: <code>SHOT_{Counter}_{NameOnly}</code></li>
            <li>**Counter Settings:** If you use <code>%Counter</code>, adjust the Start, Pad, and Step values.</li>
            <li>**Pre-processing:** Enable options for Turkish character conversion, replacing spaces with underscores, and converting to lowercase.</li>
            <li>**Find and Replace:** Use this section to make final adjustments to the text after tokens are applied. Check the **'Use Regex (Regular Expression)'** box to enable advanced pattern matching.</li>
            <li>**Preview:** Click **'Generate Preview'** to check your changes. Highlighted in blue are the names that will be changed.</li>
            <li>**Apply:** If everything is correct, click **'Apply'** to reflect the renaming in the Media Pool.</li>
            <li>**Dry Run:** If 'Dry Run' is checked, the Preview remains active and the 'Apply' button will make no changes.</li>
        </ol>
        <br>
        <h4>Regex (Regular Expression) Guide:</h4>
        <p>Regex is used to search for and replace complex patterns within text, which is powerful for tasks like removing repeating numbers. Ensure the **'Use Regex'** box is checked.</p>
        
        <p><strong>Example Scenario:</strong> To change a clip name like <code>a_0010_0010</code> to <code>a_0010</code>.</p>
        <ul>
            <li>**Regex Checkbox:** **✓ Checked**</li>
            <li>**Find (Bul):** <code>(.*)_(\\d+)_\\2</code></li>
            <li>**Replace (Değiştir):** <code>\\1_\\2</code></li>
        </ul>
        <p><strong>Explanation:</strong></p>
        <ul>
            <li><code>(.*)</code>: Captures the fixed part at the beginning of the clip name (e.g., <code>a</code>) and saves it as **Group 1** (<code>\\1</code>).</li>
            <li><code>(\\d+)</code>: Captures the first sequence of digits (<code>0010</code>) and saves it as **Group 2** (<code>\\2</code>).</li>
            <li><code>_\\2</code>: Matches the remaining underscore and the repeating number, ensuring they are ignored during the replacement.</li>
            <li>**Result:** The new name is constructed using only Group 1 and Group 2 separated by an underscore (<code>\\1_\\2</code>).</li>
        </ul>
        """
    }
}
current_language = DEFAULT_LANGUAGE 

def get_ui_text(key):
    global current_language 
    return LANG_MAP.get(current_language, LANG_MAP["en"]).get(key, f"MISSING TEXT: {key}")

TR_MAP = {'ğ':'g','Ğ':'G','ş':'s','Ş':'S','ı':'i','İ':'I','ü':'u','Ü':'U','ö':'o','O':'O','ç':'c','Ç':'C'}
def sanitize_name(s, convert_tr=True, space_to_underscore=True, to_lower=False):
    if convert_tr:
        for k,v in TR_MAP.items(): s = s.replace(k,v)
    if space_to_underscore: s = s.replace(' ','_')
    for ch in '\\/:*?"<>|': s = s.replace(ch,'-')
    s = s.replace('\\', '-') 
    return s.lower() if to_lower else s

def get_selected_items():
    if not mp: return []
    items = []
    
    raw_selection = []
    try:
        result = mp.GetSelectedClips()
        if isinstance(result, dict): raw_selection = list(result.values())
        elif isinstance(result, list): raw_selection = result
        if not raw_selection: raw_selection = mp.GetSelectedItems() 
    except Exception: 
        raw_selection = mp.GetSelectedItems() if mp else []


    for item in raw_selection:
        props = {}
        try: props = item.GetClipProperty() or {}
        except: pass

        clip_type = props.get("Type")
        
        if clip_type in ["Multicam", "CompoundClip", "Timeline", "Generator", "Adjustment Clip"]:
            continue
            
        items.append(item)
            
    return items

def get_target(scope_selected):
    return get_selected_items()

def get_props(item):
    try: return item.GetClipProperty() or {}
    except: return {}

def token_value(token_key, item, idx, counter_start, counter_pad, counter_step): 
    now = datetime.datetime.now()
    props = get_props(item)
    
    if token_key == "counter":
        pad = counter_pad 
        counter_val = counter_start + (idx * counter_step)
        return str(counter_val).zfill(pad)
    
    if token_key == "marker_name":
        markers = {}
        try:
            markers = item.GetMarkers() or {}
        except:
            pass 
            
        if markers:
            first_frame = min(markers.keys())
            return markers[first_frame].get('name', '')
        return "" 
        
    clip_name = props.get("Clip Name") or props.get("Name") or ""
    
    mapping = {
        "orig": clip_name,
        "filename": props.get("File Name") or "", 
        "extless": clip_name.split('.')[0],
        "reel": props.get("Reel Name") or props.get("Reel") or "",
        "tcstart": props.get("Start TC") or "",
        "date": now.strftime("%Y%m%d"),
        "time": now.strftime("%H%M%S"),
        "fps":  props.get("FPS") or "",
        "res":  props.get("Resolution") or "",
        "bin":  "", 
    }
    return mapping.get(token_key, "")

def apply_template(tpl, item, idx, counter_start, counter_pad, counter_step):
    out, i = "", 0
    while i < len(tpl):
        if tpl[i] == '{':
            j = tpl.find('}', i+1)
            if j != -1:
                token_display_name = tpl[i+1:j] 
                token_key = ""
                for display, (key, *_) in TOKEN_MAP_DATA.items():
                    if display.strip('%') == token_display_name:
                        token_key = key
                        break

                if token_key:
                    out += str(token_value(token_key, item, idx, counter_start, counter_pad, counter_step)) 
                else:
                    out += "{" + token_display_name + "}" 
                
                i = j+1
                continue
        out += tpl[i]; i += 1
    return out

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(get_ui_text("about_title"))
        self.layout = QVBoxLayout(self)
        
        about_text = "Brought to you by Nehir Atabek.\nBatch Renamer v01" 
        
        label_text = QLabel(about_text)
        font = QFont()
        font.setPointSize(14)
        label_text.setFont(font)
        label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(label_text)
        
        btn_close = QPushButton("OK") 
        btn_close.clicked.connect(self.close)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(btn_close)
        h_layout.addStretch(1)
        
        self.layout.addLayout(h_layout)


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(get_ui_text("help_title"))
        self.resize(700, 500)
        
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        token_widget = QWidget()
        token_layout = QVBoxLayout(token_widget)
        
        token_desc_label = QLabel(get_ui_text("help_description"))
        token_desc_label.setWordWrap(True)
        token_layout.addWidget(token_desc_label)
        
        token_tree = QTreeWidget()
        token_tree.setColumnCount(2)
        token_tree.setHeaderLabels(["Token", get_ui_text("help_tab_tokens").split(" ")[-1]]) 
        token_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        token_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        current_lang_in_dialog = current_language 
        
        for token, (key, tr_desc, en_desc) in TOKEN_MAP_DATA.items():
            desc = tr_desc if current_lang_in_dialog == "tr" else en_desc
            QTreeWidgetItem(token_tree, [token, desc])

        token_layout.addWidget(token_tree)
        self.tabs.addTab(token_widget, get_ui_text("help_tab_tokens"))
        
        guide_widget = QWidget()
        guide_layout = QVBoxLayout(guide_widget)
        
        guide_text_area = QTextEdit()
        guide_text_area.setHtml(get_ui_text("guide_text"))
        guide_text_area.setReadOnly(True)
        
        guide_layout.addWidget(guide_text_area)
        self.tabs.addTab(guide_widget, get_ui_text("help_tab_guide"))
        
        btn_close = QPushButton(get_ui_text("metadata_btn_close"))
        btn_close.clicked.connect(self.close)
        main_layout.addWidget(btn_close)


class MetadataViewer(QDialog):
    def __init__(self, items, parent=None):
        super(MetadataViewer, self).__init__(parent)
        self.setWindowTitle(get_ui_text("metadata_viewer_title"))
        self.setGeometry(200, 200, 700, 600)
        self.items = items
        
        self.layout = QVBoxLayout(self)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)
        
        self.button_layout = QHBoxLayout()
        self.btn_save_txt = QPushButton(get_ui_text("metadata_btn_txt"))
        self.btn_save_csv = QPushButton(get_ui_text("metadata_btn_csv"))
        self.btn_close = QPushButton(get_ui_text("metadata_btn_close"))
        
        self.button_layout.addWidget(self.btn_save_txt)
        self.button_layout.addWidget(self.btn_save_csv)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.btn_close)
        
        self.layout.addLayout(self.button_layout)
        
        self.btn_save_txt.clicked.connect(lambda: self.save_report("txt"))
        self.btn_save_csv.clicked.connect(lambda: self.save_report("csv"))
        self.btn_close.clicked.connect(self.close)
        
        self.generate_report()

    def generate_report(self):
        if not self.items:
            self.text_area.setText(get_ui_text("metadata_report_empty"))
            return

        report_text = f"*** DaVinci Resolve Metadata Report ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ***\n\n"
        
        for idx, item in enumerate(self.items):
            props = get_props(item)
            
            report_text += f"--- CLIP {idx + 1}: {props.get('Clip Name') or 'Unknown'} ---\n"
            
            sorted_keys = sorted(props.keys())
            
            for key in sorted_keys:
                value = props[key]
                report_text += f"  {key.ljust(15)}: {value}\n"
            
            report_text += "\n"
            
        self.text_area.setText(report_text)

    def save_report(self, format_type):
        if not self.items: return
        
        if format_type == "txt":
            file_filter = "Text Files (*.txt)"
            dialog_title = get_ui_text("metadata_btn_txt")
            report_content = self.text_area.toPlainText()
        elif format_type == "csv":
            file_filter = "CSV Files (*.csv)"
            dialog_title = get_ui_text("metadata_btn_csv")
            report_content = self.generate_csv_content()
        else:
            return

        default_name = f"Resolve_Metadata_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
        file_name, _ = QFileDialog.getSaveFileName(self, dialog_title, default_name, file_filter)

        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8-sig') as f:
                    f.write(report_content)
                QMessageBox.information(self, "Success", f"Report successfully saved:\n{file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", get_ui_text("err_file_save").format(error=e))

    def generate_csv_content(self):
        if not self.items: return ""

        all_keys = set()
        data_rows = []

        for item in self.items:
            props = get_props(item)
            all_keys.update(props.keys())

        sorted_keys = sorted(list(all_keys))
        
        ordered_keys = ['Clip Name', 'File Name', 'Reel Name', 'Timecode', 'Start TC']
        for key in reversed(ordered_keys):
            if key in sorted_keys:
                sorted_keys.remove(key)
                sorted_keys.insert(0, key)

        csv_content = ",".join(['# Clip Index'] + sorted_keys) + "\n"

        for idx, item in enumerate(self.items):
            props = get_props(item)
            row_data = [str(idx + 1)]
            
            for key in sorted_keys:
                value = str(props.get(key, ''))
                if '"' in value or ',' in value or '\n' in value:
                    value = f'"{value.replace("\"", "\"\"")}"' 
                
                row_data.append(value)
            
            data_rows.append(",".join(row_data))

        csv_content += "\n".join(data_rows)
        return csv_content

class BatchRenamerUI(QDialog):
    def __init__(self, parent=None):
        super(BatchRenamerUI, self).__init__(parent)
        
        self.setWindowTitle("n11r - Batch Renamer v01")
        
        try:
           
            icon_path = resource_path('n11r_logo.icns') 
            self.setWindowIcon(QIcon(icon_path)) 
        except Exception as e:
            print(f"UYARI: Pencere İkonu yüklenemedi: {e}")
            
    
        self.settings = QSettings("PyQtBatchRenamer", SETTINGS_KEY_GROUP)
        self.load_settings()
        
        self.setWindowTitle(get_ui_text("title"))
        self.setGeometry(100, 100, 900, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.layout = QVBoxLayout(self)
        self.items_to_process = []
        
        self.setup_ui_elements(recreate=False) 
        self.setup_completer() 
        self.connect_signals()
        self.refresh_preview()
        
    def set_language(self, lang_code):
        global current_language 
        
        if current_language == lang_code: return 
        
        try: self.cmb_lang.currentIndexChanged.disconnect()
        except TypeError: pass
        
        current_language = lang_code
        self.settings.setValue(SETTINGS_KEY_LANGUAGE, lang_code)
        
        self.setup_ui_elements(recreate=True)
        self.setup_completer() 
        self.connect_signals() 
        self.refresh_preview()

    def load_settings(self):
        global current_language 
        current_language = self.settings.value(SETTINGS_KEY_LANGUAGE, DEFAULT_LANGUAGE)
        
        self.loaded_template = self.settings.value(SETTINGS_KEY_TEMPLATE, DEFAULT_TEMPLATE)
        self.loaded_start = int(self.settings.value(SETTINGS_KEY_COUNTER_START, DEFAULT_COUNTER_START))
        self.loaded_pad = int(self.settings.value(SETTINGS_KEY_COUNTER_PAD, DEFAULT_COUNTER_PAD))
        self.loaded_step = int(self.settings.value(SETTINGS_KEY_COUNTER_STEP, DEFAULT_COUNTER_STEP))
        self.loaded_tr = self.settings.value(SETTINGS_KEY_TR_MAP, DEFAULT_TR_MAP, type=bool)
        self.loaded_space = self.settings.value(SETTINGS_KEY_SPACE_US, DEFAULT_SPACE_US, type=bool)
        self.loaded_lower = self.settings.value(SETTINGS_KEY_TO_LOWER, DEFAULT_TO_LOWER, type=bool)
        self.loaded_regex = self.settings.value(SETTINGS_KEY_REGEX, DEFAULT_REGEX, type=bool) 
        self.loaded_clean_after_apply = self.settings.value("CleanAfterApply", DEFAULT_CLEAN_AFTER_APPLY, type=bool)

    def save_settings(self):
        self.settings.setValue(SETTINGS_KEY_TEMPLATE, self.tpl_edit.text())
        self.settings.setValue(SETTINGS_KEY_COUNTER_START, self.sp_start.value())
        self.settings.setValue(SETTINGS_KEY_COUNTER_PAD, self.sp_pad.value())
        self.settings.setValue(SETTINGS_KEY_COUNTER_STEP, self.sp_step.value())
        self.settings.setValue(SETTINGS_KEY_TR_MAP, self.chk_tr.isChecked())
        self.settings.setValue(SETTINGS_KEY_SPACE_US, self.chk_space.isChecked())
        self.settings.setValue(SETTINGS_KEY_TO_LOWER, self.chk_lower.isChecked())
        self.settings.setValue(SETTINGS_KEY_REGEX, self.chk_regex.isChecked()) 
        self.settings.setValue("CleanAfterApply", self.chk_clean_after_apply.isChecked())
        
        QMessageBox.information(self, get_ui_text("msg_saved"), get_ui_text("msg_saved"))

    def load_template_to_ui(self):
        self.tpl_edit.setText(self.loaded_template)
        self.sp_start.setValue(self.loaded_start)
        self.sp_pad.setValue(self.loaded_pad)
        self.sp_step.setValue(self.loaded_step)
        self.chk_tr.setChecked(self.loaded_tr)
        self.chk_space.setChecked(self.loaded_space)
        self.chk_lower.setChecked(self.loaded_lower)
        self.chk_regex.setChecked(self.loaded_regex) 
        self.chk_clean_after_apply.setChecked(self.loaded_clean_after_apply)
        
        QMessageBox.information(self, get_ui_text("msg_loaded"), get_ui_text("msg_loaded"))
        self.refresh_preview()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def setup_ui_elements(self, recreate=False):
        
        if recreate:
            self.setWindowTitle(get_ui_text("title"))
            
            self.lang_label.setText(get_ui_text("lang_label")) 
            self.btn_help.setText(get_ui_text("btn_help"))
            self.btn_about.setText(get_ui_text("btn_about"))
            
            self.scope_group.setTitle(get_ui_text("scope_group"))
            self.chk_selected.setText(get_ui_text("chk_selected"))
            self.btn_refresh.setText(get_ui_text("btn_refresh"))
            self.btn_metadata.setText(get_ui_text("btn_metadata"))
            
            self.rename_group.setTitle(get_ui_text("rename_group"))
            self.tpl_label.setText(get_ui_text("tpl_label"))
            self.info_label.setText(get_ui_text("info_label"))
            self.btn_insert_token.setText(get_ui_text("btn_insert_token"))
            self.btn_save_template.setText(get_ui_text("btn_save_template"))
            self.btn_load_template.setText(get_ui_text("btn_load_template"))
            
            self.count_start_label.setText(get_ui_text("count_start"))
            self.count_pad_label.setText(get_ui_text("count_pad"))
            self.count_step_label.setText(get_ui_text("count_step"))
            self.chk_tr.setText(get_ui_text("chk_tr"))
            self.chk_space.setText(get_ui_text("chk_space"))
            self.chk_lower.setText(get_ui_text("chk_lower"))
            self.chk_dry.setText(get_ui_text("chk_dry"))

            self.fr_group.setTitle(get_ui_text("fr_group"))
            self.fr_find_label.setText(get_ui_text("fr_find"))
            self.fr_replace_label.setText(get_ui_text("fr_replace"))
            self.chk_case_sensitive.setText(get_ui_text("chk_case_sensitive"))
            if hasattr(self, 'chk_regex'): 
                self.chk_regex.setText(get_ui_text("chk_regex")) 

            self.preview_label.setText(get_ui_text("preview_label"))
            headers = [get_ui_text("header_old"), get_ui_text("header_new")]
            self.preview_tree.setHeaderLabels(headers)

            self.btn_preview.setText(get_ui_text("btn_preview"))
            self.btn_apply.setText(get_ui_text("btn_apply"))
            self.chk_clean_after_apply.setText(get_ui_text("chk_clean_after_apply"))
            self.btn_close.setText(get_ui_text("btn_close"))
            
            return

        self.menu_layout = QHBoxLayout()
        self.lang_label = QLabel(get_ui_text("lang_label")) 
        self.menu_layout.addWidget(self.lang_label)
        
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("Türkçe", "tr")
        self.cmb_lang.addItem("English", "en")
        index = self.cmb_lang.findData(current_language)
        if index != -1:
            self.cmb_lang.setCurrentIndex(index)
        
        self.menu_layout.addWidget(self.cmb_lang)
        
        self.menu_layout.addStretch(1)
        
        self.btn_help = QPushButton(get_ui_text("btn_help"))
        self.btn_about = QPushButton(get_ui_text("btn_about"))
        
        self.btn_help.setFixedSize(60, 24)
        self.btn_about.setFixedSize(60, 24)
        
        self.menu_layout.addWidget(self.btn_help)
        self.menu_layout.addWidget(self.btn_about)
        
        self.layout.addLayout(self.menu_layout)
        self.h_line = QFrame(self, frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken)
        self.layout.addWidget(self.h_line)
        
        self.scope_group = QGroupBox(get_ui_text("scope_group"))
        scope_layout = QHBoxLayout(self.scope_group)
        self.chk_selected = QCheckBox(get_ui_text("chk_selected"))
        self.chk_selected.setChecked(True)
        self.btn_refresh = QPushButton(get_ui_text("btn_refresh"))
        self.btn_metadata = QPushButton(get_ui_text("btn_metadata"))

        scope_layout.addWidget(self.chk_selected)
        scope_layout.addStretch(1)
        scope_layout.addWidget(self.btn_metadata)
        scope_layout.addWidget(self.btn_refresh)
        self.layout.addWidget(self.scope_group)

        self.rename_group = QGroupBox(get_ui_text("rename_group"))
        rename_layout = QVBoxLayout(self.rename_group)
        
        tpl_layout = QHBoxLayout()
        self.tpl_label = QLabel(get_ui_text("tpl_label"))
        tpl_layout.addWidget(self.tpl_label)
        
        self.tpl_edit = QLineEdit(self.loaded_template) 
        tpl_layout.addWidget(self.tpl_edit)
        
        self.btn_insert_token = QPushButton(get_ui_text("btn_insert_token"))
        tpl_layout.addWidget(self.btn_insert_token)

        self.btn_save_template = QPushButton(get_ui_text("btn_save_template"))
        self.btn_load_template = QPushButton(get_ui_text("btn_load_template"))
        tpl_layout.addWidget(self.btn_save_template)
        tpl_layout.addWidget(self.btn_load_template)
        
        rename_layout.addLayout(tpl_layout)

        self.info_label = QLabel(get_ui_text("info_label"))
        self.info_label.setWordWrap(True)
        rename_layout.addWidget(self.info_label)

        counter_layout = QHBoxLayout()
        self.count_start_label = QLabel(get_ui_text("count_start"))
        counter_layout.addWidget(self.count_start_label)
        
        self.sp_start = QSpinBox()
        self.sp_start.setRange(0, 999999)
        self.sp_start.setValue(self.loaded_start)
        counter_layout.addWidget(self.sp_start)
        
        self.count_pad_label = QLabel(get_ui_text("count_pad"))
        counter_layout.addWidget(self.count_pad_label)
        self.sp_pad = QSpinBox()
        self.sp_pad.setRange(1, 8)
        self.sp_pad.setValue(self.loaded_pad)
        counter_layout.addWidget(self.sp_pad)
        
        self.count_step_label = QLabel(get_ui_text("count_step"))
        counter_layout.addWidget(self.count_step_label)
        self.sp_step = QSpinBox()
        self.sp_step.setRange(1, 1000)
        self.sp_step.setValue(self.loaded_step)
        counter_layout.addWidget(self.sp_step)
        
        self.chk_tr = QCheckBox(get_ui_text("chk_tr"))
        self.chk_tr.setChecked(self.loaded_tr)
        counter_layout.addWidget(self.chk_tr)
        
        self.chk_space = QCheckBox(get_ui_text("chk_space"))
        self.chk_space.setChecked(self.loaded_space)
        counter_layout.addWidget(self.chk_space)
        
        self.chk_lower = QCheckBox(get_ui_text("chk_lower"))
        self.chk_lower.setChecked(self.loaded_lower)
        counter_layout.addWidget(self.chk_lower)

        self.chk_dry = QCheckBox(get_ui_text("chk_dry"))
        self.chk_dry.setChecked(True)
        counter_layout.addWidget(self.chk_dry)
        
        rename_layout.addLayout(counter_layout)
        self.layout.addWidget(self.rename_group)
        
        self.fr_group = QGroupBox(get_ui_text("fr_group"))
        fr_v_layout = QVBoxLayout(self.fr_group)
        
        fr_h_layout = QHBoxLayout()
        self.fr_find_label = QLabel(get_ui_text("fr_find"))
        fr_h_layout.addWidget(self.fr_find_label)
        
        self.find_edit = QLineEdit()
        fr_h_layout.addWidget(self.find_edit)
        self.fr_replace_label = QLabel(get_ui_text("fr_replace"))
        fr_h_layout.addWidget(self.fr_replace_label)
        
        self.replace_edit = QLineEdit()
        fr_h_layout.addWidget(self.replace_edit)
        fr_v_layout.addLayout(fr_h_layout)

        fr_settings_layout = QHBoxLayout()
        self.chk_case_sensitive = QCheckBox(get_ui_text("chk_case_sensitive"))
        self.chk_case_sensitive.setChecked(False) 
        self.chk_regex = QCheckBox(get_ui_text("chk_regex")) 
        self.chk_regex.setChecked(self.loaded_regex) 
        
        fr_settings_layout.addWidget(self.chk_case_sensitive)
        fr_settings_layout.addWidget(self.chk_regex) 
        fr_settings_layout.addStretch(1)
        fr_v_layout.addLayout(fr_settings_layout)
        self.layout.addWidget(self.fr_group) 

        self.preview_tree = QTreeWidget()
        self.preview_tree.setColumnCount(2)
        
        headers = [get_ui_text("header_old"), get_ui_text("header_new")]
        self.preview_tree.setHeaderLabels(headers)
        
        self.preview_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.preview_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.preview_label = QLabel(get_ui_text("preview_label"))
        self.layout.addWidget(self.preview_label)
        self.layout.addWidget(self.preview_tree)

        action_layout = QHBoxLayout()
        self.btn_preview = QPushButton(get_ui_text("btn_preview"))
        self.btn_apply = QPushButton(get_ui_text("btn_apply"))
        self.btn_close = QPushButton(get_ui_text("btn_close"))
        
        self.chk_clean_after_apply = QCheckBox(get_ui_text("chk_clean_after_apply"))
        self.chk_clean_after_apply.setChecked(self.loaded_clean_after_apply)
        

        action_layout.addWidget(self.btn_preview)
        action_layout.addWidget(self.btn_apply)
        action_layout.addWidget(self.chk_clean_after_apply)
        action_layout.addStretch(1)
        action_layout.addWidget(self.btn_close)
        self.layout.addLayout(action_layout)


    def setup_completer(self):
        token_names_only = [t.strip('%') for t in TOKEN_LIST] 
        model = QStringListModel(token_names_only)
        
        self.completer = QCompleter(self)
        self.completer.setModel(model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains) 
        self.completer.setWidget(self.tpl_edit)
        self.completer.setCompletionPrefix("") 

        try: self.completer.activated.disconnect()
        except TypeError: pass 
        self.completer.activated.connect(self.insert_completed_token) 
    def force_refresh(self):
        """Listeyi zorla yenile - Resolve'dan güncel seçimi al"""
        global resolve, pm, project, mp
        
       
        try:
            import DaVinciResolveScript as bmd
            resolve = bmd.scriptapp("Resolve")
            if resolve:
                pm = resolve.GetProjectManager()
                if pm:
                    project = pm.GetCurrentProject()
                    if project:
                        mp = project.GetMediaPool()
        except Exception:
            pass
        
      
        self.items_to_process = []
        self.preview_tree.clear()
        
      
        self.items_to_process = self.collect_items()
        
       
        self.refresh_preview()

    def connect_signals(self):
        
        try:
            self.btn_refresh.clicked.disconnect()
            self.btn_preview.clicked.disconnect()
            self.btn_apply.clicked.disconnect()
            self.btn_close.clicked.disconnect()
            self.btn_save_template.clicked.disconnect()
            self.btn_load_template.clicked.disconnect()
            self.btn_metadata.clicked.disconnect()
            self.find_edit.textChanged.disconnect()
            self.replace_edit.textChanged.disconnect()
            self.chk_case_sensitive.toggled.disconnect()
            if hasattr(self, 'chk_regex'): 
                try: self.chk_regex.toggled.disconnect()
                except TypeError: pass
            self.tpl_edit.textChanged.disconnect()
            self.sp_start.valueChanged.disconnect()
            self.sp_pad.valueChanged.disconnect()
            self.sp_step.valueChanged.disconnect()
            self.chk_tr.toggled.disconnect()
            self.chk_space.toggled.disconnect()
            self.chk_lower.toggled.disconnect()
            self.btn_help.clicked.disconnect()
            self.btn_about.clicked.disconnect()
            self.cmb_lang.currentIndexChanged.disconnect()
        except (TypeError, AttributeError):
            pass
        
        self.btn_refresh.clicked.connect(self.force_refresh) 
        self.btn_preview.clicked.connect(self.refresh_preview)
        self.btn_apply.clicked.connect(self.apply_changes) 
        self.btn_close.clicked.connect(self.close)
        
        self.sp_start.valueChanged.connect(self.refresh_preview)
        self.sp_pad.valueChanged.connect(self.refresh_preview)
        self.sp_step.valueChanged.connect(self.refresh_preview)
        self.chk_tr.toggled.connect(self.refresh_preview)
        self.chk_space.toggled.connect(self.refresh_preview)
        self.chk_lower.toggled.connect(self.refresh_preview)
        self.btn_metadata.clicked.connect(self.show_metadata_viewer)
        self.btn_save_template.clicked.connect(self.save_settings)
        self.btn_load_template.clicked.connect(self.load_template_to_ui)
        self.btn_help.clicked.connect(self.show_help_dialog)
        self.btn_about.clicked.connect(self.show_about_dialog)
        
        self.cmb_lang.currentIndexChanged.connect(lambda: self.set_language(self.cmb_lang.currentData()))
        
        self.setup_token_menu()

  # batch_rename.py dosyasında, BatchRenamerUI sınıfı içinde, show_metadata_viewer metodunun yeni hali:

    def show_metadata_viewer(self):
        global resolve, pm, project, mp
        
        # --- BAĞLANTIYI KONTROL ET VE YENİLE ---
        # Resolve objesi veya Media Pool objesi yoksa yeniden bağlanmayı dene.
        if not resolve or not mp:
            try:
                # DaVinciResolveScript'i tekrar içeri aktarma (API'ye bağlanmanın en güvenli yolu)
                import DaVinciResolveScript as bmd 
                resolve = bmd.scriptapp("Resolve")
                if resolve:
                    pm = resolve.GetProjectManager()
                    if pm:
                        project = pm.GetCurrentProject()
                        if project:
                            mp = project.GetMediaPool()
            except Exception:
                pass # Hata olsa bile sessizce yakala
        
        # Final Kontrol: Bağlantı kuruldu mu?
        if not resolve or not mp:
            QMessageBox.critical(self, get_ui_text("scope_group"), get_ui_text("err_no_resolve"))
            return
        # ----------------------------------------

        items = self.collect_items()
        if not items:
            QMessageBox.warning(self, get_ui_text("scope_group"), get_ui_text("err_no_clip"))
            return

        viewer = MetadataViewer(items, self)
        viewer.exec()

        
    def show_about_dialog(self):
        AboutDialog(self).exec()

    def show_help_dialog(self):
        HelpDialog(self).exec()


    def insert_token_into_editor(self, token_name):
        token_template = f"{{{token_name}}}"
        cursor = self.tpl_edit.cursorPosition()
        current_text = self.tpl_edit.text()
        
        new_text = current_text[:cursor] + token_template + current_text[cursor:]
        self.tpl_edit.setText(new_text)
        self.tpl_edit.setCursorPosition(cursor + len(token_template))
        self.refresh_preview()

    def insert_completed_token(self, completed_name):
        current_text = self.tpl_edit.text()
        cursor_pos = self.tpl_edit.cursorPosition()
        prefix_start = -1; i = cursor_pos - 1
        
        while i >= 0:
            char = current_text[i]
            if char.isalnum() or char == '_': i -= 1
            elif char == '%': prefix_start = i; break
            else: break

        if prefix_start != -1:
            try: self.tpl_edit.textChanged.disconnect(self.handle_template_input)
            except TypeError: pass
            
            token_template = f"{{{completed_name}}}"
            new_text = current_text[:prefix_start] + token_template + current_text[cursor_pos:]
            self.tpl_edit.setText(new_text)
            
            new_cursor_pos = prefix_start + len(token_template)
            self.tpl_edit.setCursorPosition(new_cursor_pos)
            
            self.tpl_edit.textChanged.connect(self.handle_template_input)
            self.refresh_preview()

    def handle_template_input(self, text):
        current_text = self.tpl_edit.text()
        cursor_pos = self.tpl_edit.cursorPosition()
        
        token_start = -1; i = cursor_pos - 1
        
        while i >= 0:
            char = current_text[i]
            if char.isalnum() or char == '_': i -= 1
            elif char == '%': token_start = i; break
            else: break
        
        if token_start != -1:
            prefix = current_text[token_start:cursor_pos]
            
            if prefix.startswith('%'):
                completion_prefix = prefix[1:]
                self.completer.setCompletionPrefix(completion_prefix)
                
                if len(prefix) >= 1: 
                     if not self.completer.popup().isVisible(): self.completer.complete()
                else: 
                    self.completer.popup().hide()
            else: 
                self.completer.popup().hide()
        else: 
            self.completer.popup().hide()
            
        self.refresh_preview() 
            
    def setup_token_menu(self):
        menu = QMenu(self)
        current_lang_in_menu = current_language 
        for token_display, (_, tr_desc, en_desc) in TOKEN_MAP_DATA.items():
            desc = tr_desc if current_lang_in_menu == "tr" else en_desc
            action = menu.addAction(f"{token_display.strip('%')} - ({desc})")
            action.triggered.connect(lambda checked, t=token_display.strip('%'): self.insert_token_into_editor(t))
        
        self.btn_insert_token.setMenu(menu)

    def collect_items(self):
        self.items_to_process = get_target(scope_selected=self.chk_selected.isChecked())
        return self.items_to_process

    def refresh_preview(self):
        
        global resolve, pm, project, mp
        if not resolve:
            try:
                import DaVinciResolveScript as bmd
                resolve = bmd.scriptapp("Resolve")
                if resolve:
                    pm = resolve.GetProjectManager()
                    if pm:
                        project = pm.GetCurrentProject()
                        if project:
                            mp = project.GetMediaPool()
            except Exception:
                pass
        
        if not hasattr(self, 'tpl_edit'):
            return 

        tpl = self.tpl_edit.text().strip()
        s   = int(self.sp_start.value())
        p   = int(self.sp_pad.value())
        step = int(self.sp_step.value())
        tr  = self.chk_tr.isChecked()
        spc = self.chk_space.isChecked()
        low = self.chk_lower.isChecked()
        
        find_str = self.find_edit.text()
        replace_str = self.replace_edit.text()
        case_sensitive = self.chk_case_sensitive.isChecked()
        use_regex = self.chk_regex.isChecked() 
        
        if not self.items_to_process or self.preview_tree.topLevelItemCount() == 0:
             self.items_to_process = self.collect_items()

        self.preview_tree.clear()
        
        if not self.items_to_process:
            QTreeWidgetItem(self.preview_tree, [get_ui_text("no_clips_in_list"), ""])
            return

        re_flags = 0 if case_sensitive else re.IGNORECASE

        for idx, item in enumerate(self.items_to_process):
            props = get_props(item)
            old_name = props.get("Clip Name") or props.get("Name") or ""
            
            new_name = apply_template(tpl, item, idx, s, p, step) 
            
            if find_str:
                try:
                    if use_regex: 
                        new_name = re.sub(find_str, replace_str, new_name, flags=re_flags) 
                    else:
                        new_name = re.sub(re.escape(find_str), replace_str, new_name, flags=re_flags)
                except re.error:
                    pass
                
            new_name = sanitize_name(new_name, tr, spc, low)
            
            item_widget = QTreeWidgetItem(self.preview_tree, [old_name, new_name])
            
            if old_name != new_name:
                item_widget.setForeground(1, QColor(Qt.GlobalColor.blue))
            else:
                item_widget.setForeground(1, QColor(Qt.GlobalColor.darkGreen))


    def apply_changes(self):
        if not resolve:
            QMessageBox.critical(self, get_ui_text("btn_apply"), get_ui_text("err_no_resolve"))
            return

        if not self.items_to_process:
            QMessageBox.warning(self, get_ui_text("btn_apply"), get_ui_text("err_no_clip"))
            return

        tpl = self.tpl_edit.text().strip()
        s   = int(self.sp_start.value())
        p   = int(self.sp_pad.value())
        step = int(self.sp_step.value())
        tr  = self.chk_tr.isChecked()
        spc = self.chk_space.isChecked()
        low = self.chk_lower.isChecked()
        dry = self.chk_dry.isChecked()
        clean_after_apply = self.chk_clean_after_apply.isChecked()

        find_str = self.find_edit.text()
        replace_str = self.replace_edit.text()
        case_sensitive = self.chk_case_sensitive.isChecked()
        use_regex = self.chk_regex.isChecked() 

        if dry:
            QMessageBox.information(self, get_ui_text("btn_apply"), get_ui_text("msg_dry_run"))
            self.refresh_preview()
            return
            
        undo_active = False
        if mp and hasattr(mp, 'BeginUndo') and callable(mp.BeginUndo):
            try: mp.BeginUndo(); undo_active = True
            except: pass 
            
        re_flags = 0 if case_sensitive else re.IGNORECASE
        success_count = 0

        try:
            for idx, item in enumerate(self.items_to_process):
                new = apply_template(tpl, item, idx, s, p, step)
                
                if find_str:
                    try: 
                        if use_regex: 
                            new = re.sub(find_str, replace_str, new, flags=re_flags)
                        else:
                            new = re.sub(re.escape(find_str), replace_str, new, flags=re_flags) 
                    except re.error: pass
                new = sanitize_name(new, tr, spc, low)
                
                renamed_successfully = False
                try: 
                    if item.SetName(new): renamed_successfully = True
                except Exception: 
                    try: 
                        if item.SetClipProperty({"Clip Name": new}): renamed_successfully = True
                    except Exception: pass
                
                if renamed_successfully:
                    success_count += 1
                
        finally:
            if undo_active and hasattr(mp, 'EndUndo') and callable(mp.EndUndo):
                try: mp.EndUndo()
                except: pass

        try:
             current_folder = project.GetMediaPool().GetCurrentFolder()
             if current_folder and hasattr(current_folder, 'RefreshInfo'):
                 current_folder.RefreshInfo()
        except Exception: 
             pass
        self.items_to_process = self.collect_items()
        self.refresh_preview()
        if clean_after_apply:
            
            QTreeWidgetItem(self.preview_tree, [get_ui_text("cleaned_after_apply"), ""])
        else:
            self.refresh_preview()
            
        msg = get_ui_text("msg_success").format(count_total=len(self.items_to_process), count_success=success_count)
        QMessageBox.information(self, get_ui_text("btn_apply"), msg)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = BatchRenamerUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"\n======================================")
        print(f"FATAL HATA: Program başlatılamadı.")
        print(f"======================================")
        print(f"Hata Türü: {type(e).__name__}")
        print(f"Hata Detayı: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)