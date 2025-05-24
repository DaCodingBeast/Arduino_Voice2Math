#include <WiFiS3.h>
#include "secrets.h"
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

WiFiServer server(80);
LiquidCrystal_I2C lcd(0x27, 16, 2);

String TEXTDISPLAY = "Waiting...";
String pageList[20];
int pageCount = 0;
int currentPage = 0;
unsigned long lastSwitchTime = 0;

// Decode Strings
String urlDecode(const String &input) {
  String decoded = "";
  char temp[] = "0x00";
  unsigned int len = input.length();
  unsigned int i = 0;

  while (i < len) {
    char c = input.charAt(i);
    if (c == '+') {
      decoded += ' ';
    } else if (c == '%' && i + 2 < len) {
      temp[2] = input.charAt(i + 1);
      temp[3] = input.charAt(i + 2);
      char hexChar = (char) strtol(temp, NULL, 16);
      decoded += hexChar;
      i += 2;
    } else {
      decoded += c;
    }
    i++;
  }
  return decoded;
}


// Remove symbols (that come from transporting python lists)
String cleanInputString(String input) {
  String output = "";
  for (int i = 0; i < input.length(); i++) {
    char c = input.charAt(i);
    if (c != '[' && c != ']' && c != '\'' && c != '"') {
      output += (c == ',') ? ' ' : c;
    }
  }
  output.trim();
  return output;
}

String getLastWord(String input) {
  input.trim();
  int lastSpace = input.lastIndexOf(' ');
  return (lastSpace == -1) ? input : input.substring(lastSpace + 1);
}

// Seperate words into groups that can fit on the LCD Display
void paginateText(String text) {
  pageCount = 0;
  currentPage = 0;
  text.trim();

  String word = "";
  String currentPageText = "";

  for (int i = 0; i < text.length(); i++) {
    char c = text.charAt(i);
    if (c == ' ' || i == text.length() - 1) {
      if (i == text.length() - 1 && c != ' ') word += c;
      if (currentPageText.length() + word.length() + (currentPageText.length() > 0 ? 1 : 0) <= 32) {
        if (currentPageText.length() > 0) currentPageText += ' ';
        currentPageText += word;
      } else {
        pageList[pageCount++] = currentPageText;
        currentPageText = word;
        if (pageCount >= 20) break;
      }
      word = "";
    } else {
      word += c;
    }
  }

  if (currentPageText.length() > 0 && pageCount < 20) {
    pageList[pageCount++] = currentPageText;
  }
}

//init
void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  WiFi.begin(SECRET_SSID, SECRET_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin();
  paginateText(TEXTDISPLAY);
}

void loop() {
  WiFiClient client = server.available();
//while client connected
  if (client) {
    while (client.connected()) {
      if (client.available()) {
        String req = client.readStringUntil('\r');
        client.read();

        int msgIndex = req.indexOf("msg=");
        if (msgIndex != -1) {
          int endIndex = req.indexOf(' ', msgIndex);
          String msg = req.substring(msgIndex + 4, endIndex != -1 ? endIndex : req.length());
          TEXTDISPLAY = urlDecode(msg);
          TEXTDISPLAY = cleanInputString(TEXTDISPLAY);
          paginateText(TEXTDISPLAY);
        }

        String lastWord = getLastWord(TEXTDISPLAY);
//these messages neccessary
        client.println("HTTP/1.1 200 OK");
        client.println("Content-Type: text/plain");
        client.println("Connection: close");
        client.println();
        client.println(lastWord);
        break;
      }
    }
    client.stop();
  }
//every 3 seconds switch LCD Page
  if (millis() - lastSwitchTime >= 3000 && pageCount > 0) {
    lcd.clear();
    String page = pageList[currentPage];
    lcd.setCursor(0, 0);
    if (page.length() <= 16) {
      lcd.print(page);
    } else {
      lcd.print(page.substring(0, 16));
      lcd.setCursor(0, 1);
      lcd.print(page.substring(16));
    }

    currentPage = (currentPage + 1) % pageCount;
    lastSwitchTime = millis();
  }
}
