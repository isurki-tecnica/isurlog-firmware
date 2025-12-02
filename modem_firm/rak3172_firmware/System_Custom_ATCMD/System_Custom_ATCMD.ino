/***
 *  This example shows custom AT command with led control.
***/

void setup()
{
    Serial.begin(115200);
    Serial1.begin(115200, RAK_AT_MODE);
    delay(2000);
    Serial.println("RAKwireless Custom ATCMD Example");
    Serial.println("------------------------------------------------------");

}

void loop()
{

  
}
