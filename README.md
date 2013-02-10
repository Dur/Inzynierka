/etc/apache2/mods-enabled/reqtimeout.conf - ustawienie mniejszego limitu bajtow na sekunde (na przyklad do 5) dzieki temu apache nie bedzie zamykal polaczenia

/usr/lib/python2.7/dist-packages - dodanie wlasnego pliku cos.pth w ktorym nalezy umiescic sciezke do katalogu w ktorym znajduja sie biblioteki pythna stworzone przez uzytkownika (na przyklad /home/dur/Projects/ServerSide) z tych biblitek bedzie korzystal apache przy probie odwolania sie do jakiegos pliku

Aby serwer mogl zablowac jakis plik przy uzyciu fileLock musi miec dostep do tego pliku i wszystkich katalogow powyzej

Do pliku httpd.conf na apache należy dodać linijkę : PythonOption PROJECT_LOCATION <bezwzgledna sciezka do katalogu z projektem> (W moim przypadku ta liijka wygląda tak: PythonOption PROJECT_LOCATION /home/dur/Projects/)

