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
  renderGoBack(isBaseLevel) {
    let icon;
    if(isBaseLevel)
      icon = <Icon name='bars' size={24}/>;
    else
      icon = <Icon name='chevron-left' size={24}/>;
    return(
      <View style={{flexDirection: 'row', alignItems: 'center'}}>
        {icon}
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
          {this.props.showGoBack ? this.renderGoBack(this.props.isBaseLevel) : null}
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eee',
  },
  title: {
    textAlign: 'center',
    marginTop: 4,
    color: '#000',
    fontSize: 20,
    alignSelf: 'center'
  },
  leftItem: {
    position: 'absolute',
    top: isIphoneX() ? 40 : 20,
    left: 10,
    height: 44,
    width: 59,
    justifyContent: 'center',
  },
  rightItem: {
    position: 'absolute',
    top: isIphoneX() ? 40 : 20,
    right: 0,
    height: 44,
    width: 59,
    alignItems: 'center',
    justifyContent: 'center'
  },
});