/**
 * Created by Yida Yin on 1/10/18
 */

import React, {Component} from 'react';
import {
  View,
  Text,
  Clipboard,
  TouchableOpacity,
  StyleSheet,
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

export default class DebugInfo extends Component {
  render() {
    return (
      <View style={{flex: 1, paddingTop: 0}}>
        <LogView
          inverted={false}
          multiExpanded={true}
          timeStampFormat='HH:mm:ss'
        />

        <View style={styles.buttons}>
          <TouchableOpacity style={styles.closeButton} onPress={() => this.props.navigation.goBack()}>
            <Text style={styles.closeButtonText}>Close</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.closeButton} onPress={copyRawLogs}>
            <Text style={styles.closeButtonText}>Copy</Text>
          </TouchableOpacity>
        </View>
      </View>
    )
  }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000F0'
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