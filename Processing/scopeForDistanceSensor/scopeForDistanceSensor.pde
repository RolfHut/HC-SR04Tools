  /*
 * changes by Rolf Hut:
 * changed to only plot incoming serial data, and only a single variable is displayed
 * Also displays an AR filtered value of the signal in the window.
  
 * Oscilloscope
 * Gives a visual rendering of incomming serial data.
 * 
 * This project is part of Accrochages
 * See http://accrochages.drone.ws
 * 
 * (c) 2008 Sofian Audry (info@sofianaudry.com)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */ 

import processing.serial.*;

int portNumber = 9; //which port to select. Run the 

Serial port;  // Create object from Serial class
float val;      // Data received from the serial port
float[] valuesR;
float dist = 0.0;
float zoom;
byte lf = 10;
float alpha = 0.1;


void setup() 
{
  size(640, 480);
  // Open the port that the board is connected to and use the same speed (9600 bps)
  println(Serial.list());
  port = new Serial(this, Serial.list()[portNumber], 9600);
  port.bufferUntil(lf);
  valuesR = new float[width];
  //values = new float[3];
  zoom = 1.0f;
  smooth();
}

int getY(float val) {
  return (int)(((height/2) - val / 1030.0f * (height))-1);
}

void serialEvent(Serial port) {
  float values = float(port.readString());
  if (!Float.isNaN(values)){
    pushValue(values);
  }
}

//
void pushValue(float valueR) {
  for (int i=0; i<width-1; i++){
    valuesR[i] = valuesR[i+1];
  }
  
  dist = ((1 - alpha) * dist) + (alpha * valueR);
  println(dist);
  valuesR[width-1] = valueR;
}

void drawLines() {
  stroke(255);
  
  int displayWidth = (int) (width / zoom);
  
  int k = valuesR.length - displayWidth;
  
  int x0 = 0;
  int yX0 = getY(valuesR[k]);
  for (int i=1; i<displayWidth; i++) {
    k++;
    int x1 = (int) (i * (width-1) / (displayWidth-1));
    int yX1 = getY(valuesR[k]);
    stroke(255);
    line(x0, yX0, x1, yX1);
    x0 = x1;
    yX0 = yX1;
  }
}

void drawGrid() {
  stroke(255, 0, 0);
  line(0, height/2, width, height/2);
}

void keyReleased() {
  switch (key) {
    case '+':
      zoom *= 2.0f;
      println(zoom);
      if ( (int) (width / zoom) <= 1 )
        zoom /= 2.0f;
      break;
    case '-':
      zoom /= 2.0f;
      if (zoom < 1.0f)
        zoom *= 2.0f;
      break;
  }
}

void drawStats(){
  textSize(32);
  fill(255);
  text(dist,10,32);
}

void draw()
{
  background(0);
  drawGrid();
  drawLines();
  drawStats();
}
