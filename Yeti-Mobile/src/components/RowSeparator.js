import React from 'react';
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';


export default class RowSeparator extends React.Component{
  render() {
    return (
      <View style={styles.separator}>

      </View>
    )
  }
}



const styles = StyleSheet.create({
  separator: {
    height: 1,
    width: '100%',
    backgroundColor: '#dddddd'
  },
}) ;

