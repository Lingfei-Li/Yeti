import React, {Component} from 'react';
import {
    View,
    Text,
    Clipboard,
    TouchableOpacity,
    StyleSheet, Image,
} from 'react-native';
import deviceLog, {LogView} from 'react-native-device-log';


async function copyRawLogs() {
  const rows = await deviceLog.store.getRows();

  const rowsString = rows
    .reverse() // They store comments in reverse order
    .map(row => `${row.timeStamp._i}: ${row.message}`)
    .join('\n');

  Clipboard.setString(rowsString);
}

export default class DebugView extends Component {
  static navigationOptions = ({navigation}) => ({
    header: null
  });

  render() {
    return (
      <View style={{flex: 1, paddingTop: 0}}>
        <LogView
          inverted={false}
          multiExpanded={true}
          timeStampFormat='HH:mm:ss'
        />
      </View>
    )
  }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    // backgroundColor: '#000000F0'
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  closeButton: {
    padding: 16,
    alignItems: 'center'
  },
  closeButtonText: {
    color: '#FE0082'
  }
});