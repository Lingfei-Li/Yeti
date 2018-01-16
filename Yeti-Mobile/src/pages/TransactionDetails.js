/**
 * Created by Yida Yin on 1/5/18
 */

import React from 'react';
import {
  Text,
  View,
  FlatList,
  TouchableOpacity,
  Alert,
  StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/Entypo';

import Header from '../components/Header';
import LambdaAPI from '../LambdaAPI';


export default class TransactionDetails extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const {item} = this.props.navigation.state.params;
    return (
      <View style={styles.container}>
        <Header
          title={item.FriendId}
          showGoBack={true}
          onGoBackPress={() => this.props.navigation.goBack()}
        />
        <View style={{flex: 1}}>
          <Text>{JSON.stringify(item)}</Text>
        </View>
      </View>
    )
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  separator: {
    height: 1,
    width: '100%',
    backgroundColor: '#dddddd'
  },
});