/**
 * German translation
 * @author JPG & Mace <dev@flying-datacenter.de>
 * @version 2011-07-26
 */
if (elFinder && elFinder.prototype && typeof(elFinder.prototype.i18) == 'object') {
	elFinder.prototype.i18.de = {
		translator : 'JPG & Mace &lt;dev@flying-datacenter.de&gt;',
		language   : 'Deutsch',
		direction  : 'ltr',
		messages   : {
			
			/********************************** errors **********************************/
			'error'                : 'Fehler',
			'errUnknown'           : 'Unbekannter Fehler.',
			'errUnknownCmd'        : 'Unbekannter Befehl.',
			'errJqui'              : 'Ungültige jQuery UI Konfiguration. Die Komponenten Selectable, draggable und droppable müssen inkludiert sein.',
			'errNode'              : 'Für elFinder muss das DOM Element erstellt werden.',
			'errURL'               : 'Ungültige elFinder Konfiguration! Die URL Option nicht gesetzt.',
			'errAccess'            : 'Zugriff verweigert.',
			'errConnect'           : 'Verbindung zum Backend fehlgeschlagen',
			'errAbort'             : 'Verbindung abgebrochen.',
			'errTimeout'           : 'Zeitüberschreitung der Verbindung.',
			'errNotFound'          : 'Backend nicht gefunden.',
			'errResponse'          : 'Ungültige Backend Antwort.',
			'errConf'              : 'Ungültige Backend Konfiguration.',
			'errJSON'              : 'PHP JSON Modul nicht vorhanden.',
			'errNoVolumes'         : 'Lesbare Volumes nicht vorhanden.',
			'errCmdParams'         : 'Ungültige Parameter für Befehl: "$1".',
			'errDataNotJSON'       : 'Daten nicht im JSON Format.',
			'errDataEmpty'         : 'Daten sind leer.',
			'errCmdReq'            : 'Backend Anfrage benötigt Befehl.',
			'errOpen'              : 'Kann "$1" nicht öffnen',
			'errNotFolder'         : 'Objekt ist kein Verzeichnis.',
			'errNotFile'           : 'Objekt ist keine Datei.',
			'errRead'              : 'Kann "$1" nicht öffnen.',
			'errWrite'             : 'Kann nicht in "$1" schreiben.',
			'errPerm'              : 'Zugriff verweigert.',
			'errLocked'            : '"$1" ist gelockt und kann nicht umbenannt, verschoben oder gelöscht werden.',
			'errExists'            : 'Die Datei "$1" existiert bereits.',
			'errInvName'           : 'Ungültiger Datei Name.',
			'errFolderNotFound'    : 'Verzeichnis nicht gefunden.',
			'errFileNotFound'      : 'Datei nicht gefunden.',
			'errTrgFolderNotFound' : 'Zielverzeichnis "$1" nicht gefunden.',
			'errPopup'             : 'Der Browser hat das Pop-Up-Fenster unterbunden. Um die Datei zu öffnen, Pop-Ups in den Browser Einstellungen aktivieren.',
			'errMkdir'             : 'Kann Verzeichnis "$1" nicht erstellen.',
			'errMkfile'            : 'Kann Datei "$1" nicht erstellen.',
			'errRename'            : 'Kann "$1" nicht umbenennen.',
			'errCopyFrom'          : 'Kopieren von Dateien von "$1" nicht erlaubt.',
			'errCopyTo'            : 'Kopieren von Dateien nach "$1" nicht erlaubt.',
			'errUploadCommon'      : 'Upload Fehler.',
			'errUpload'            : 'Kann "$1" nicht hochladen.',
			'errUploadNoFiles'     : 'Keine Dateien zum Hochladen gefunden.',
			'errMaxSize'           : 'Daten überschreiten die Maximalgröße.',
			'errFileMaxSize'       : 'Die Datei überschreitet die Maximalgröße',
			'errUploadMime'        : 'Dateityp nicht zulässig.',
			'errUploadTransfer'    : '"$1" Transfer Fehler.', 
			'errSave'              : 'Kann "$1" nicht speichern.',
			'errCopy'              : 'Kann "$1" nicht kopieren.',
			'errMove'              : 'Kann "$1" nicht verschieben.',
			'errCopyInItself'      : '"$1" kann sich nicht in sich selbst kopieren.',
			'errRm'                : 'Kann "$1" nicht enfernen.',
			'errExtract'           : 'Kann "$1" nicht entpacken .',
			'errArchive'           : 'Archiv konnte nicht erstellt werden.',
			'errArcType'           : 'Archivtyp nicht untersützt.',
			'errNoArchive'         : 'Bei der Datei handelt es nicht um ein Archiv oder der Archivtyp nicht unterstütz.',
			'errCmdNoSupport'      : 'Das Backend unterstütz diesen Befehl nicht.',
			
			/******************************* commands names ********************************/
			'cmdarchive'   : 'Archiv erstellen',
			'cmdback'      : 'Zurück',
			'cmdcopy'      : 'Kopieren',
			'cmdcut'       : 'Ausschreiden',
			'cmddownload'  : 'Herunterladen',
			'cmdduplicate' : 'Duplizieren',
			'cmdedit'      : 'Datei bearbeiten',
			'cmdextract'   : 'Archiv entpacken',
			'cmdforward'   : 'Vorwärts',
			'cmdgetfile'   : 'Datei auswählen',
			'cmdhelp'      : 'über diese Software',
			'cmdhome'      : 'Startverzeichnis',
			'cmdinfo'      : 'Informationen',
			'cmdmkdir'     : 'Neues Verzeichnis',
			'cmdmkfile'    : 'Neue Textdatei',
			'cmdopen'      : 'öffnen',
			'cmdpaste'     : 'Einfügen',
			'cmdquicklook' : 'Vorschau',
			'cmdreload'    : 'Neuladen',
			'cmdrename'    : 'Umbenennen',
			'cmdrm'        : 'Löschen',
			'cmdsearch'    : 'Suchen',
			'cmdup'        : 'Ins übergeordnete Verzeichnis wechseln',
			'cmdupload'    : 'Datei hochladen',
			'cmdview'      : 'Ansehen',
			
			/*********************************** buttons ***********************************/ 
			'btnClose'  : 'Schließen',
			'btnSave'   : 'Speichern',
			'btnRm'     : 'Entfernen',
			'btnCancel' : 'Abbrechen',
			'btnNo'     : 'Nein',
			'btnYes'    : 'Ja',
			
			/******************************** notifications ********************************/
			'ntfopen'     : 'öffne Verzeichnis',
			'ntffile'     : 'öffne Datei',
			'ntfreload'   : 'Verzeichnisinhalt neu',
			'ntfmkdir'    : 'Erstelle Verzeichnis',
			'ntfmkfile'   : 'Erstelle Dateien',
			'ntfrm'       : 'Lösche Dateien',
			'ntfcopy'     : 'Kopiere Dateien files',
			'ntfmove'     : 'Verschiebe Dateien',
			'ntfprepare'  : 'Kopiervorgang initialisieren',
			'ntfrename'   : 'Benenne Dateien um',
			'ntfupload'   : 'Uploading files',
			'ntfdownload' : 'Downloading files',
			'ntfsave'     : 'Speichere Datei',
			'ntfarchive'  : 'Erstelle Archiv',
			'ntfextract'  : 'Entpacke Dateien',
			'ntfsearch'   : 'Suche',
			'ntfsmth'     : 'Bin beschäftigt >_<',
			
			/************************************ dates **********************************/
			'dateUnknown' : 'unbekannt',
			'Today'       : 'Heute',
			'Yesterday'   : 'Gestern',
			'Jan'         : 'Jan',
			'Feb'         : 'Feb',
			'Mar'         : 'Mär',
			'Apr'         : 'Apr',
			'May'         : 'Mai',
			'Jun'         : 'Jun',
			'Jul'         : 'Jul',
			'Aug'         : 'Aug',
			'Sep'         : 'Sep',
			'Oct'         : 'Okt',
			'Nov'         : 'Nov',
			'Dec'         : 'Dez',

			/******************************** sort variants ********************************/
            'sortname'          : 'nach Name', 
            'sortkind'          : 'nach freundlicher', 
            'sortsize'          : 'nach Größe',
            'sortdate'          : 'nach Datum',
            'sortFoldersFirst'  : 'Ordner zuerst',

			/********************************** messages **********************************/
			'confirmReq'      : 'Bestätigung Benötigt',
			'confirmRm'       : 'Sollen die Dateien gelöscht werden?<br/>Dies kann nicht rückgängig gemacht werden!',
			'confirmRepl'     : 'Datei ersetzen?',
			'apllyAll'        : 'Alles bestätigen',
			'name'            : 'Name',
			'size'            : 'Größe',
			'perms'           : 'Berechtigungen',
			'modify'          : '&Auml;nderungsdatum',
			'kind'            : 'Typ',
			'read'            : 'lesen',
			'write'           : 'schreiben',
			'noaccess'        : 'Kein Zugriff',
			'and'             : 'und',
			'unknown'         : 'unbekannt',
			'selectall'       : 'Alle Dateien auswählen',
			'selectfiles'     : 'Dateien auswählen',
			'selectffile'     : 'Erste Datei auswhählen',
			'selectlfile'     : 'Letzte Datei auswählen',
			'viewlist'        : 'Spaltenansicht',
			'viewicons'       : 'Symbolansicht',
			'places'          : 'Orte',
			'calc'            : 'Berechne', 
			'path'            : 'Pfad',
			'aliasfor'        : 'Verknüpfund zu',
			'locked'          : 'Gesperrt',
			'dim'             : 'Bildgröße',
			'files'           : 'Dateien',
			'folders'         : 'Verzeichnise',
			'items'           : 'Objekte',
			'yes'             : 'ja',
			'no'              : 'nein',
			'link'            : 'Link',
			'searcresult'     : 'Suchergebnisse',  
			'selected'        : 'Objekte ausgewählt',
			'about'           : 'über',
			'shortcuts'       : 'Tastenkombinationen',
			'help'            : 'Hilfe',
			'webfm'           : 'Web Datei Manager',
			'ver'             : 'Version',
			'protocolver'     : 'Protokol Version',
			'homepage'        : 'Projekt Website',
			'docs'            : 'Dokumentation',
			'github'          : 'Forke uns auf Github',
			'twitter'         : 'Folge uns auf twitter',
			'facebook'        : 'Begleite uns auf facebook',
			'team'            : 'Team',
			'chiefdev'        : 'Chefentwickler',
			'developer'       : 'Entwickler',
			'contributor'     : 'Üntersützer',
			'maintainer'      : 'Maintainer',
			'translator'      : 'Übersetzer',
			'icons'           : 'Icons',
			'dontforget'      : 'und vergess dein Handtuch nicht',
			'shortcutsof'     : 'Shortcuts disabled',
			'dropFiles'       : 'Dateien hier ablegen',
			'or'              : 'oder',
			'selectForUpload' : 'Dateien zum Upload auswählen',
			'moveFiles'       : 'Dateien verschieben',
			'copyFiles'       : 'Dateien kopieren',
						
			/********************************** mimetypes **********************************/
			'kindUnknown'     : 'Unbekannt',
			'kindFolder'      : 'Verzeichnis',
			'kindAlias'       : 'Verknüpfung',
			'kindAliasBroken' : 'Defekte Verknüpfung',
			// applications
			'kindApp'         : 'Programm',
			'kindPostscript'  : 'Postscript Dokument',
			'kindMsOffice'    : 'Microsoft Office Dokument',
			'kindMsWord'      : 'Microsoft Word Dokument',
			'kindMsExcel'     : 'Microsoft Excel Dokument',
			'kindMsPP'        : 'Microsoft Powerpoint Präsentation',
			'kindOO'          : 'Open Office Dokument',
			'kindAppFlash'    : 'Flash Programm',
			'kindPDF'         : 'Portables Dokumentenformat (PDF)',
			'kindTorrent'     : 'Bittorrent Datei',
			'kind7z'          : '7z Archiv',
			'kindTAR'         : 'TAR Archiv',
			'kindGZIP'        : 'GZIP Archiv',
			'kindBZIP'        : 'BZIP Archiv',
			'kindZIP'         : 'ZIP Archiv',
			'kindRAR'         : 'RAR Archiv',
			'kindJAR'         : 'Java JAR Datei',
			'kindTTF'         : 'True Type Schrift',
			'kindOTF'         : 'Open Type Schrift',
			'kindRPM'         : 'RPM Paket',
			// texts
			'kindText'        : 'Text Dokument',
			'kindTextPlain'   : 'Text Dokument',
			'kindPHP'         : 'PHP Quelltext',
			'kindCSS'         : 'Cascading Stylesheet',
			'kindHTML'        : 'HTML Dokument',
			'kindJS'          : 'Javascript Quelltext',
			'kindRTF'         : 'Formatierte Textdatei',
			'kindC'           : 'C Quelltext',
			'kindCHeader'     : 'C Header Quelltext',
			'kindCPP'         : 'C++ Quelltext',
			'kindCPPHeader'   : 'C++ Header Quelltext',
			'kindShell'       : 'Unix-Shell-Skript',
			'kindPython'      : 'Python Quelltext',
			'kindJava'        : 'Java Quelltext',
			'kindRuby'        : 'Ruby Quelltext',
			'kindPerl'        : 'Perl Script',
			'kindSQL'         : 'SQL Quelltext',
			'kindXML'         : 'XML Dokument',
			'kindAWK'         : 'AWK Quelltext',
			'kindCSV'         : 'Komma getrennte Daten',
			'kindDOCBOOK'     : 'Docbook XML Dokument',
			// images
			'kindImage'       : 'Bild',
			'kindBMP'         : 'Bitmap Bild',
			'kindJPEG'        : 'JPEG Bild',
			'kindGIF'         : 'GIF Bild',
			'kindPNG'         : 'PNG Bild',
			'kindTIFF'        : 'TIFF Bild',
			'kindTGA'         : 'TGA Bild',
			'kindPSD'         : 'Adobe Photoshop Bild',
			'kindXBITMAP'     : 'X Bitmap Bild',
			'kindPXM'         : 'Pixelmator Bild',
			// media
			'kindAudio'       : 'Audiodatei',
			'kindAudioMPEG'   : 'MPEG Audio',
			'kindAudioMPEG4'  : 'MPEG-4 Audio',
			'kindAudioMIDI'   : 'MIDI Audio',
			'kindAudioOGG'    : 'Ogg Vorbis Audio',
			'kindAudioWAV'    : 'WAV Audio',
			'AudioPlaylist'   : 'MP3 Playlist',
			'kindVideo'       : 'Videodatei',
			'kindVideoDV'     : 'DV Film',
			'kindVideoMPEG'   : 'MPEG Film',
			'kindVideoMPEG4'  : 'MPEG-4 Film',
			'kindVideoAVI'    : 'AVI Film',
			'kindVideoMOV'    : 'Quick Time Film',
			'kindVideoWM'     : 'Windows Media Film',
			'kindVideoFlash'  : 'Flash Film',
			'kindVideoMKV'    : 'Matroska Film',
			'kindVideoOGG'    : 'Ogg Film'
		}
	}
}
