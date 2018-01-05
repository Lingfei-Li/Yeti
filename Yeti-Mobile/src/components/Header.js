/**
 * Created by Yida Yin on 1/5/18
 */


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


export default class Header extends React.Component{
  renderGoBack() {
    return(
      <View style={{flexDirection: 'row', alignItems: 'center'}}>
        <Icon name='chevron-left' size={20}/>
        <Text style={{fontSize: 16, marginLeft: 5}}>{this.props.goBackText || 'BACK'}</Text>
      </View>
    )
  }

  render() {
    return (
      <View style={styles.header}>

        <TouchableOpacity
          onPress={this.props.onGoBackPress}
          style={styles.leftItem}
        >
          {this.props.showGoBack ? this.renderGoBack() : null}
        </TouchableOpacity>

        <Text style={[styles.title, this.props.titleStyle]}>{this.props.title || 'Yeti'}</Text>

        <TouchableOpacity
          onPress={this.props.onRightItemPress}
          style={styles.rightItem}
        >
          {this.props.rightItem || null}
        </TouchableOpacity>

      </View>
    )
  }
}

const isIphoneX = () => {
  let d = Dimensions.get('window');
  const { height, width } = d;
  return (
    // This has to be iOS duh
    Platform.OS === 'ios' &&

    // Accounting for the height in either orientation
    (height === 812 || width === 812)
  );
};

const styles = StyleSheet.create({
  header: {
    height: isIphoneX() ? 80 : 64,
    width: '100%',
    paddingTop: isIphoneX() ? 40 : 20,
    paddingLeft: 20,
    paddingRight: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eeeeee'
  },
  title: {
    textAlign: 'center',
    marginTop: 4,
    color: '#666',
    fontSize: 18,
    alignSelf: 'center'
  },
  leftItem: {
    position: 'absolute',
    top: isIphoneX() ? 40 : 20,
    left: 0,
    paddingLeft: 20,
    height: 44,
    width: 84,
    alignItems: 'center',
    justifyContent: 'center'
  },
  rightItem: {
    position: 'absolute',
    top: isIphoneX() ? 40 : 20,
    right: 0,
    paddingRight: 10,
    height: 44,
    width: 59,
    alignItems: 'center',
    justifyContent: 'center'
  },
});