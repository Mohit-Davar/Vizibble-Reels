// Narration script + timing sheet. Frame-perfect visual synchronization.
// Every code step, wiring cue, and serial print hits its exact visual cue frame-by-frame.
// Word timestamps provide real-time electric gold karaoke pop-ins in Captions.tsx.

export type WordTiming = { word: string; start: number; end: number };

export type NarrationLine = {
  scene: string;
  start: number;
  end: number;
  text: string;
  caption?: boolean;
  words?: WordTiming[];
};

export const NARRATION: NarrationLine[] = [
  {scene: 'hook', start: 0.5, end: 1.046, text: "Want to measure", words: [{"word":"Want","start":0.5,"end":0.697},{"word":"to","start":0.721,"end":0.767},{"word":"measure","start":0.802,"end":1.046}]},
  {scene: 'hook', start: 1.08, end: 1.998, text: "temperature and humidity", words: [{"word":"temperature","start":1.08,"end":1.44},{"word":"and","start":1.475,"end":1.557},{"word":"humidity","start":1.615,"end":1.998}]},
  {scene: 'hook', start: 2.033, end: 3.658, text: "with your ESP32?", words: [{"word":"with","start":2.033,"end":2.149},{"word":"your","start":2.183,"end":2.3},{"word":"ESP32?","start":2.369,"end":3.658}]},
  {scene: 'hardware', start: 4.5, end: 4.999, text: "You only need", words: [{"word":"You","start":4.5,"end":4.663},{"word":"only","start":4.697,"end":4.825},{"word":"need","start":4.86,"end":4.999}]},
  {scene: 'hardware', start: 5.022, end: 5.928, text: "two parts: an", words: [{"word":"two","start":5.022,"end":5.173},{"word":"parts:","start":5.243,"end":5.707},{"word":"an","start":5.824,"end":5.928}]},
  {scene: 'hardware', start: 6.009, end: 7.879, text: "ESP32-S3 board, and", words: [{"word":"ESP32-S3","start":6.009,"end":7.17},{"word":"board,","start":7.24,"end":7.565},{"word":"and","start":7.739,"end":7.879}]},
  {scene: 'hardware', start: 7.925, end: 9.562, text: "a DHT11 sensor.", words: [{"word":"a","start":7.925,"end":7.96},{"word":"DHT11","start":8.041,"end":8.831},{"word":"sensor.","start":8.9,"end":9.562}]},
  {scene: 'wiring', start: 9.8, end: 10.88, text: "VCC connects to", words: [{"word":"VCC","start":9.8,"end":10.322},{"word":"connects","start":10.473,"end":10.764},{"word":"to","start":10.81,"end":10.88}]},
  {scene: 'wiring', start: 11.007, end: 12.911, text: "3.3 volts. Next,", words: [{"word":"3.3","start":11.007,"end":11.634},{"word":"volts.","start":11.716,"end":12.215},{"word":"Next,","start":12.656,"end":12.911}]},
  {scene: 'wiring', start: 12.935, end: 13.318, text: "data goes to", words: [{"word":"data","start":12.935,"end":13.086},{"word":"goes","start":13.12,"end":13.237},{"word":"to","start":13.271,"end":13.318}]},
  {scene: 'wiring', start: 13.376, end: 14.618, text: "GPIO 4. And", words: [{"word":"GPIO","start":13.376,"end":13.817},{"word":"4.","start":13.898,"end":14.316},{"word":"And","start":14.49,"end":14.618}]},
  {scene: 'wiring', start: 14.665, end: 15.245, text: "ground goes right", words: [{"word":"ground","start":14.665,"end":14.862},{"word":"goes","start":14.908,"end":15.048},{"word":"right","start":15.106,"end":15.245}]},
  {scene: 'wiring', start: 15.28, end: 15.977, text: "to ground.", words: [{"word":"to","start":15.28,"end":15.326},{"word":"ground.","start":15.373,"end":15.977}]},
  {scene: 'code', start: 18.4, end: 18.946, text: "First, in the", words: [{"word":"First,","start":18.4,"end":18.76},{"word":"in","start":18.783,"end":18.841},{"word":"the","start":18.876,"end":18.946}]},
  {scene: 'code', start: 18.98, end: 20.559, text: "Arduino IDE, install", words: [{"word":"Arduino","start":18.98,"end":19.364},{"word":"IDE,","start":19.422,"end":19.921},{"word":"install","start":20.165,"end":20.559}]},
  {scene: 'code', start: 20.618, end: 21.686, text: "the Adafruit DHT", words: [{"word":"the","start":20.618,"end":20.687},{"word":"Adafruit","start":20.78,"end":21.233},{"word":"DHT","start":21.268,"end":21.686}]},
  {scene: 'code', start: 21.802, end: 22.533, text: "library.", words: [{"word":"library.","start":21.802,"end":22.533}]},
  {scene: 'code', start: 21.8, end: 22.857, text: "Define the DHT11", words: [{"word":"Define","start":21.8,"end":22.125},{"word":"the","start":22.148,"end":22.218},{"word":"DHT11","start":22.253,"end":22.857}]},
  {scene: 'code', start: 22.926, end: 24.122, text: "on GPIO 4.", words: [{"word":"on","start":22.926,"end":22.996},{"word":"GPIO","start":23.054,"end":23.495},{"word":"4.","start":23.541,"end":24.122}]},
  {scene: 'code', start: 25.8, end: 26.589, text: "Next, start the", words: [{"word":"Next,","start":25.8,"end":26.23},{"word":"start","start":26.311,"end":26.497},{"word":"the","start":26.52,"end":26.589}]},
  {scene: 'code', start: 26.624, end: 27.843, text: "sensor inside setup.", words: [{"word":"sensor","start":26.624,"end":26.903},{"word":"inside","start":26.949,"end":27.251},{"word":"setup.","start":27.274,"end":27.843}]},
  {scene: 'code', start: 29.5, end: 30.359, text: "Then, read temperature", words: [{"word":"Then,","start":29.5,"end":29.767},{"word":"read","start":29.802,"end":29.941},{"word":"temperature","start":29.976,"end":30.359}]},
  {scene: 'code', start: 30.394, end: 31.149, text: "and humidity in", words: [{"word":"and","start":30.394,"end":30.487},{"word":"humidity","start":30.58,"end":31.056},{"word":"in","start":31.091,"end":31.149}]},
  {scene: 'code', start: 31.207, end: 31.822, text: "loop!", words: [{"word":"loop!","start":31.207,"end":31.822}]},
  {scene: 'serial', start: 33.3, end: 34.113, text: "Upload the code", words: [{"word":"Upload","start":33.3,"end":33.706},{"word":"the","start":33.73,"end":33.799},{"word":"code","start":33.846,"end":34.113}]},
  {scene: 'serial', start: 34.148, end: 34.6, text: "and open the", words: [{"word":"and","start":34.148,"end":34.217},{"word":"open","start":34.275,"end":34.484},{"word":"the","start":34.531,"end":34.6}]},
  {scene: 'serial', start: 34.647, end: 35.483, text: "Serial Monitor.", words: [{"word":"Serial","start":34.647,"end":34.972},{"word":"Monitor.","start":35.018,"end":35.483}]},
  {scene: 'serial', start: 36.5, end: 36.837, text: "You get a", words: [{"word":"You","start":36.5,"end":36.651},{"word":"get","start":36.697,"end":36.79},{"word":"a","start":36.813,"end":36.837}]},
  {scene: 'serial', start: 36.895, end: 37.626, text: "fresh reading every", words: [{"word":"fresh","start":36.895,"end":37.115},{"word":"reading","start":37.173,"end":37.417},{"word":"every","start":37.464,"end":37.626}]},
  {scene: 'serial', start: 37.661, end: 38.59, text: "two seconds!", words: [{"word":"two","start":37.661,"end":37.789},{"word":"seconds!","start":37.847,"end":38.59}]},
  {scene: 'final', start: 40.2, end: 41.059, text: "Just three wires", words: [{"word":"Just","start":40.2,"end":40.455},{"word":"three","start":40.502,"end":40.722},{"word":"wires","start":40.769,"end":41.059}]},
  {scene: 'final', start: 41.094, end: 41.849, text: "and simple code.", words: [{"word":"and","start":41.094,"end":41.164},{"word":"simple","start":41.21,"end":41.477},{"word":"code.","start":41.512,"end":41.849}]},
  {scene: 'final', start: 42.092, end: 42.615, text: "Save this and", words: [{"word":"Save","start":42.092,"end":42.336},{"word":"this","start":42.371,"end":42.499},{"word":"and","start":42.545,"end":42.615}]},
  {scene: 'final', start: 42.673, end: 43.59, text: "follow for more!", caption: false, words: [{"word":"follow","start":42.673,"end":42.894},{"word":"for","start":42.94,"end":43.021},{"word":"more!","start":43.068,"end":43.59}]},
];

export const NARRATION_TEXT = NARRATION.map((l) => l.text).join(' ');
