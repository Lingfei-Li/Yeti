/**
 * Created by Yida Yin on 1/10/18
 */

import deviceLog, {InMemoryAdapter} from 'react-native-device-log';


let logEnabled = true;

deviceLog.init(new InMemoryAdapter(), {
  logToConsole : true,
  logRNErrors : true,
  rowInsertDebounceMs: 0,
  maxNumberToRender : 2000,
  maxNumberToPersist : 2000
});

//noinspection JSAnnotator
export default {
  log(...params) {
    if (!logEnabled) {
      return;
    }
    console.log(...params);
    return deviceLog.log(...params);
  },
  info(...params) {
    if (!logEnabled) {
      return;
    }
    console.info(...params);
    return deviceLog.info(...params);
  },
  warn(...params) {
    if (!logEnabled) {
      return;
    }
    //eslint-disable-next-line no-console
    console.warn(...params);
    return deviceLog.info(...params);
  },

  enableLog() {
    deviceLog.log('Logging has been turned on');
    logEnabled = true;
  },
  disableLog() {
    logEnabled = false;
  }
};