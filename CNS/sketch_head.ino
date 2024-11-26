// QList - Version: Latest 
#include <QList.h>

// Adafruit NeoPixel - Version: Latest 
#include <Adafruit_NeoPixel.h>
#include <Servo.h>
#include <MemoryUsage.h>


/*
Head library
Copyright 2017 Jeremy Beha
*/

// definitions
#define EYELEFT 7
#define EYERIGHT 5
#define NECKTILT 9
#define NECKSWIVEL 3
#define EventSpan 25
#define TIMESPAN 400
#define CYCLESYNC 4

class HeadEvent {
  public:
    unsigned char neckTilt = 0;
    unsigned char neckSwivel = 0;
    unsigned char leftEyeColor[3] = {1,1,1};
    unsigned char rightEyeColor[3] = {1,1,1};
    unsigned char leftEyeBrightness = 0;
    unsigned char rightEyeBrightness = 0; 
    unsigned short duration = 0;
};

class Head {
  public:
    // neck servo
    const int neckUpLimit = 240;
    const int neckDownLimit = 0;

    const int neckLeftLimit = 180;
    const int neckRightLimit = 0;
    
    // eyes
    const int defaultBrightness = 10;
    const unsigned char defaultColor[3] = {255,255,255};
    const unsigned char red[3] = {255,0,0};
    const unsigned char blue[3] = {0,0,255};
    const unsigned char off[3] = {0,0,0};

    QList<HeadEvent> events;
    Adafruit_NeoPixel leftEye = Adafruit_NeoPixel(1, EYELEFT, NEO_GRB + NEO_KHZ800);
    Adafruit_NeoPixel rightEye = Adafruit_NeoPixel(1, EYERIGHT, NEO_GRB + NEO_KHZ800);
    Servo neckTilt; 
    Servo neckSwivel;
    bool busy = false;
    
    void init() {
      // initialize event queue
      //this->fillQueue();
      this->initEyes();
      this->initNeck();
    }

    HeadEvent getCurrentState() {
      HeadEvent currentState;
      currentState.neckSwivel = this->neckSwivel.read();
      currentState.neckTilt = this->neckTilt.read();
      currentState.rightEyeBrightness = this->rightEye.getBrightness();
      currentState.leftEyeBrightness = this->leftEye.getBrightness();
      uint32_t rightColor = this->rightEye.getPixelColor(0);
      currentState.rightEyeColor[0] = (rightColor >> 16) & 0xFF;
      currentState.rightEyeColor[1] = (rightColor >> 8) & 0xFF;
      currentState.rightEyeColor[2] = rightColor & 0xFF;
      uint32_t leftColor = this->rightEye.getPixelColor(0);
      currentState.leftEyeColor[0] = (leftColor >> 16) & 0xFF;
      currentState.leftEyeColor[1] = (leftColor >> 8) & 0xFF;
      currentState.leftEyeColor[2] = leftColor & 0xFF;
      
      return currentState;
    }
    
    void fillQueue() {
      this->busy = false;
      for(int i=0;i<TIMESPAN;i++) {
        HeadEvent temp_event;
        this->events.push_back(temp_event);
      }
    }
    
    void initNeck() {
      this->neckTilt.attach(NECKTILT);
      this->neckTilt.write((this->neckUpLimit+this->neckDownLimit)/2);
      this->neckSwivel.attach(NECKSWIVEL);
      this->neckSwivel.write((this->neckLeftLimit+this->neckRightLimit)/2);
    }
    
    void initEyes() {
      this->leftEye.begin();
      this->leftEye.show(); // Initialize all pixels to 'off'
      this->rightEye.begin();
      this->rightEye.show(); // Initialize all pixels to 'off'
      this->leftEye.setPixelColor(0,this->leftEye.Color(this->defaultColor[0],this->defaultColor[1],this->defaultColor[2]));
      this->leftEye.setBrightness(this->defaultBrightness);
      this->leftEye.show();
      this->rightEye.setPixelColor(0,this->rightEye.Color(this->defaultColor[0],this->defaultColor[1],this->defaultColor[2]));
      this->rightEye.setBrightness(this->defaultBrightness);
      this->rightEye.show();
    }
    
    void processQueue() {
      bool eyeActivity[2] = {false, false};
      if(!this->events.size()) {
        return;
      }
      HeadEvent currentEvent = this->events.front();
      if(currentEvent.neckTilt > 0) {
        Serial.print(F("Tilting head to "));
        Serial.println(String(currentEvent.neckTilt));
        if(currentEvent.neckTilt > this->neckUpLimit)
          this->neckTilt.write(this->neckUpLimit);
        else
          this->neckTilt.write(currentEvent.neckTilt);
      }
      if(currentEvent.neckSwivel > 0) {
        //Serial.print(F("Swiveling head to "));
        //Serial.println(String(currentEvent.neckSwivel));
        if(currentEvent.neckSwivel > this->neckLeftLimit)
          this->neckSwivel.write(this->neckLeftLimit);
        else if(currentEvent.neckSwivel < this->neckRightLimit)
          this->neckSwivel.write(this->neckRightLimit);
        else
          this->neckSwivel.write(currentEvent.neckSwivel);
      }
      if(currentEvent.leftEyeBrightness > 0) {
        this->leftEye.setBrightness(currentEvent.leftEyeBrightness);
        eyeActivity[0] = true;        
      }
      if(currentEvent.rightEyeBrightness > 0) {
        this->rightEye.setBrightness(currentEvent.rightEyeBrightness);
        eyeActivity[1] = true;
      }
      if(currentEvent.leftEyeColor[0] != 1) {
        this->leftEye.setPixelColor(0, this->leftEye.Color(currentEvent.leftEyeColor[0], currentEvent.leftEyeColor[1], currentEvent.leftEyeColor[2]));
        eyeActivity[0] = true;
      }
      if(currentEvent.rightEyeColor[0] != 1) {
        this->rightEye.setPixelColor(0, this->rightEye.Color(currentEvent.rightEyeColor[0], currentEvent.rightEyeColor[1], currentEvent.rightEyeColor[2]));
        eyeActivity[1] = true;
      }
      if(eyeActivity[0]) {
        this->leftEye.show();
      }
      if(eyeActivity[1]) {
        this->rightEye.show();
      }
      
      this->events.pop_front();
      //if(!this->events.size()) {
        //this->fillQueue();
      //}
      delay(EventSpan);
    }
        
    int addYesEvent(int start_time, int shakes) {
      for(int i = 0; i < shakes;i++) {
        this->events[start_time+ (i*44)].neckTilt = this->neckUpLimit;
        this->events[start_time + 20 +(i*44)].neckTilt = this->neckDownLimit;
      }
      return start_time + 20 + (shakes*44);
    }
    
    int addWinkEvent(int start_time, char eye, int winks, unsigned char R = 255, unsigned char G = 255, unsigned char B = 255) {
      int timer = start_time;
      for(int i = 0; i < winks;i++) {
        for(int r = this->defaultBrightness; r > 0; r-=1) {
          if(eye == 'L') {
            this->events[timer].leftEyeBrightness = r;
          }
          else {
            this->events[timer].rightEyeBrightness = r;
          }
          timer += 4;
        }
        if(eye == 'L') {
          memcpy(this->events[timer].leftEyeColor, this->off, sizeof(this->off));
        }
        else {
          memcpy(this->events[timer].rightEyeColor, this->off, sizeof(this->off));
        }
        timer+=6;
        if(eye == 'L') {
          this->events[timer].leftEyeColor[0] = R;
          this->events[timer].leftEyeColor[1] = G;
          this->events[timer].leftEyeColor[2] = B;
        }
        else {
          this->events[timer].rightEyeColor[0] = R;
          this->events[timer].rightEyeColor[1] = G;
          this->events[timer].rightEyeColor[2] = B;
        }
        for(int r = 0; r < this->defaultBrightness; r+=1) {
          if(eye == 'L') {
            this->events[timer].leftEyeBrightness = r;
          }
          else {
            this->events[timer].rightEyeBrightness = r;
          }
          timer += 4;
        }
        
      }
      timer += 4;
      if(eye == 'L') {
        this->events[timer].leftEyeBrightness = this->defaultBrightness;
        memcpy(this->events[timer].leftEyeColor, this->defaultColor, sizeof(this->defaultColor));
      }
      else {
        this->events[timer].rightEyeBrightness = this->defaultBrightness;
        memcpy(this->events[timer].rightEyeColor, this->defaultColor, sizeof(this->defaultColor));
      }
      return start_time+20+(winks*30);
    }
    
    int addIceEvent(int start_time, int cycles) {
      memcpy(this->events[0].leftEyeColor, this->blue, sizeof(this->blue));
      memcpy(this->events[0].rightEyeColor , this->blue, sizeof(this->blue));
      memcpy(this->events[cycles*80].leftEyeColor, this->defaultColor, sizeof(this->defaultColor));
      memcpy(this->events[cycles*80].rightEyeColor, this->defaultColor, sizeof(this->defaultColor));
      return cycles*80;
    }
    
    int addOffEvent(int start_time, int cycles) {
      memcpy(this->events[0].leftEyeColor, this->off, sizeof(this->off));
      memcpy(this->events[0].rightEyeColor , this->off, sizeof(this->off));
      memcpy(this->events[cycles*80].leftEyeColor, this->defaultColor, sizeof(this->defaultColor));
      memcpy(this->events[cycles*80].rightEyeColor, this->defaultColor, sizeof(this->defaultColor));
      return cycles*80;
    }
        
    int addRageEvent(int start_time, int cycles) {
      int timer = start_time;
      for(int i = 0; i < cycles;i++) {
        this->events[timer].neckTilt = this->neckUpLimit;
        timer += 40;
        this->events[timer].neckTilt = this->neckDownLimit;
        timer += 40;
      }
      
      // change to using different shades of red
      timer = start_time;
      for(int i = 0; i < cycles;i++) {
        memcpy(this->events[timer].leftEyeColor, this->red, sizeof(this->red));
        memcpy(this->events[timer].rightEyeColor , this->red, sizeof(this->red));
        for(int r = 0; r < 200; r+=12) {
            this->events[timer].leftEyeBrightness = r;
            this->events[timer].rightEyeBrightness = r;
            timer += 2;
        }
        for(int r = 200; r > 0; r-=12) {
            this->events[timer].leftEyeBrightness = r;
            this->events[timer].rightEyeBrightness = r;
            timer += 2;
        }
        
      }
      this->events[timer].neckTilt = (this->neckUpLimit+this->neckDownLimit)/2;
      memcpy(this->events[timer].leftEyeColor, this->defaultColor, sizeof(this->defaultColor));
      memcpy(this->events[timer].rightEyeColor, this->defaultColor, sizeof(this->defaultColor));
      return timer;
    }
    
    int addStutterEvent(int start_time, int cycles) {
      int timer = start_time;
      for(int i = 0; i < (cycles*2);i++) {
        this->events[timer].neckTilt = random((this->neckUpLimit+this->neckDownLimit)/2,this->neckUpLimit);
        timer += 20;
        this->events[timer].neckTilt = random((this->neckUpLimit+this->neckDownLimit)/2,this->neckDownLimit);
        timer += 20;
      }
      this->addWinkEvent(0, 'L', cycles);
      this->addWinkEvent(0, 'R', cycles);
      this->events[timer].neckTilt = (this->neckUpLimit+this->neckDownLimit)/2;
      return timer;
    }
   
};


int freeRam () {
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}

unsigned char* getRandomColor() {
  unsigned char *temp = new unsigned char[3];
  temp[0] = random(1,200);
  temp[1] = random(1,200);
  temp[2] = random(1,200);
  return temp;
}

Head* head = new Head();
char eyes[2] = {'L', 'R'};
int actionWill = 0;
int eye;
unsigned char *color;
void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Starting");
  randomSeed(analogRead(0));
  head->init();
}

void causeRandomEvent() {
  actionWill = random(0,101);
  if(!head->busy) {
    switch(actionWill) {
      case 5:
        head->busy = true;
        head->addWinkEvent(0, eyes[random(0,2)], random(1,5));
        break;
      case 15:
        head->busy = true;
        eye = random(0,2);
        head->addWinkEvent(0, eyes[eye], random(1,5));
        head->addWinkEvent(15, eyes[abs(eye-1)], random(1,5));
        break;
      case 60:
        head->busy = true;
        for(int i = 0 ; i < random(2,4); i++) {
          eye = random(0,2);
          color = getRandomColor();
          head->addWinkEvent(0+(i*92), eyes[eye], 1, color[0], color[1], color[2]);
          head->addWinkEvent(20+(i*92), eyes[abs(eye-1)], 1,  color[0], color[1], color[2]);
          delete[] color;
        }
        break;
      case 20:
        head->busy = true;
        head->addIceEvent(0, random(1,5));
        break;
      case 30:
        head->busy = true;
        head->addOffEvent(0, random(1,5));
        break;
      case 50:
        head->busy = true;
        head->addStutterEvent(0, random(1,5));
        break;
      case 10:
        head->busy = true;
        head->addRageEvent(0, random(3,5));
        break;
      case 100:
        head->busy = true;
        head->addYesEvent(0, random(1,5));
        break;
    } 
  }
}

/*
Protocol:
S[Val]|: Swivel
T[Val]|: Tilt
L[Brightness][R][G][B]|: Left eye
R[Brightness][R][G][B]|: Right eye
D[Val]Z|: duration for event in cycles
E: End Event
*/
void processEvent(char* buf, int buf_index) {
  // current state
  HeadEvent currentState = head->getCurrentState();
  // desired state
  HeadEvent desiredState;
  QList<char*> states;
  char *state;
  state = new char[10];
  int state_index = 0;
  for(int cur = 0; cur < buf_index; cur++) {
    if(buf[cur] == '|') {
      state[state_index] = '\0';
      states.push_back(state);
      state = new char[10];
      state_index = 0;
    }
    else {
      state[state_index++] = buf[cur];
    }
  }


  char *statement;
  while(states.size()) {
    statement = states.front();
    states.pop_front();
    switch(statement[0]) {
      case 'S':
        desiredState.neckSwivel = atoi(statement + 1);
        break;
      case 'T':
        desiredState.neckTilt = atoi(statement + 1);
        break;
      case 'L':
        desiredState.leftEyeBrightness = statement[1];
        desiredState.leftEyeColor[0] = statement[2];
        desiredState.leftEyeColor[1] = statement[3];
        desiredState.leftEyeColor[2] = statement[4];
        break;
      case 'R':
        desiredState.rightEyeBrightness = statement[1];
        desiredState.rightEyeColor[0] = statement[2];
        desiredState.rightEyeColor[1] = statement[3];
        desiredState.rightEyeColor[2] = statement[4];
        break;
      case 'D':
        desiredState.duration = ceil(atoi(statement + 1)/CYCLESYNC);
        break;
    }
    delete []statement;
  }

  // create events to get there
  float neckSwivelVelocity = float(desiredState.neckSwivel-currentState.neckSwivel)/desiredState.duration;
  float neckTiltVelocity = float(desiredState.neckTilt-currentState.neckTilt)/desiredState.duration;
  float leftEyeBrightnessVelocity = float(desiredState.leftEyeBrightness-currentState.leftEyeBrightness)/desiredState.duration;
  float rightEyeBrightnessVelocity = float(desiredState.rightEyeBrightness-currentState.rightEyeBrightness)/desiredState.duration;

  for(int t=0;t < desiredState.duration; t++) {
    HeadEvent temp_event;
    // neck swivel
    if(desiredState.neckSwivel != currentState.neckSwivel)
      temp_event.neckSwivel = currentState.neckSwivel + (neckSwivelVelocity*t);
    if(desiredState.neckTilt != currentState.neckTilt)
      temp_event.neckTilt = currentState.neckTilt + (neckTiltVelocity*t);
    if(desiredState.leftEyeColor != currentState.leftEyeColor) 
       memcpy(temp_event.leftEyeColor, desiredState.leftEyeColor, sizeof(head->defaultColor));
    if(desiredState.leftEyeBrightness != currentState.leftEyeBrightness)
      temp_event.leftEyeBrightness = currentState.leftEyeBrightness + (leftEyeBrightnessVelocity*t);
    if(desiredState.rightEyeColor != currentState.rightEyeColor) 
       memcpy(temp_event.rightEyeColor, desiredState.rightEyeColor, sizeof(head->defaultColor));
    if(desiredState.rightEyeBrightness != currentState.rightEyeBrightness)
      temp_event.rightEyeBrightness = currentState.rightEyeBrightness + (rightEyeBrightnessVelocity*t);

    head->events.push_back(temp_event);

    if(mu_freeRam() < 500) {
      Serial.println(F("Error, cannot add more to queue because of memory"));
      return;
    }
  }
}

char buf[100] = "\0";
int buf_index = 0;
bool buildEvent = false;
int cycle = 0;
void loop() {

  int receivedValue;
  if(buildEvent == false && cycle == CYCLESYNC) {
    head->processQueue();
  }
  if(cycle == CYCLESYNC) {
    cycle = 0;
  }
  cycle++;
  if(Serial.available() > 0) {
    buildEvent = true;
    receivedValue = Serial.read();
    
    if(receivedValue != 'E') {
      buf[buf_index] = receivedValue;
      buf_index++;
    }
    else {
      processEvent(buf, buf_index);

      buildEvent = false;
      buf_index = 0;
      buf[0] = '\0';
    }
  }
}



