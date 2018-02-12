import React from 'react';
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet, TextInput, Button,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';


export default class FilterButton extends React.Component{
  render() {
    return (
      <View style={styles.filterButtonView}>
        <Button
          title="Filter"
          style={styles.filterButton}
          onPress={() => alert('sort by')}
        />
      </View>
    )
  }
}

const styles = StyleSheet.create({
  filterButtonView: {
    width: '20%',
    backgroundColor: '#eee',
  },
  filterButton: {
    backgroundColor: '#ddd',
  },
});