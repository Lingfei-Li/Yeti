import React from 'react';
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet, TextInput, Button, Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';


export default class LogoTitle extends React.Component{
  render() {

    let titleContent;
    if(this.props.titleText) {
      titleContent = <Text style={styles.titleText}>{this.props.title}</Text>;
    } else {
      titleContent = <Image
        source={require('../resources/assets/himalaya.png')}
        style={[styles.titleImage]}
      />;
    }

    return (
      <View style={styles.titleView}>
        {titleContent}
      </View>
    )
  }
}

const styles = StyleSheet.create({
  titleView: {
  },
  titleText: {
    fontSize: 20,
  },
  titleImage: {
    width: 32,
    height: 32,
  }
});