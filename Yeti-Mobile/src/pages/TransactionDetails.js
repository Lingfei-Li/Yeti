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
import {timeConverter} from '../utils';


export default class TransactionDetails extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const {item} = this.props.navigation.state.params;
    const confirmed = item.StatusCode === 1;
    return (
      <View style={styles.container}>
        <Header
          title="Transaction Detail"
          showGoBack={true}
          onGoBackPress={() => this.props.navigation.goBack()}
        />
        <View style={{flex: 1, alignItems: 'center'}}>
          <Text style={{fontSize: 22, marginTop: 10}}>{item.FriendName}</Text>
          <Text>id: {item.FriendId}</Text>
          <Text style={{fontSize: 20, fontWeight: 'bold', marginTop: 12, marginBottom: 8}}>{item.Amount}</Text>
          <Text
            style={{color: confirmed ? "red" : "green", marginBottom: 10, fontSize: 18}}
          >
            {confirmed ? "Closed" : "Open"}
          </Text>

          <View style={{flexDirection: 'row', paddingLeft: 10, paddingRight: 10}}>
            <Text style={{color: '#888'}}>Platform: </Text>
            <View style={{flex: 1}}/>
            <Text>{item.TransactionPlatform}</Text>
          </View>
          <View style={{flexDirection: 'row', paddingLeft: 10, paddingRight: 10}}>
            <Text style={{color: '#888'}}>TransactionId: </Text>
            <View style={{flex: 1}}/>
            <Text>{item.TransactionId}</Text>
          </View>
          <View style={{flexDirection: 'row', paddingLeft: 10, paddingRight: 10}}>
            <Text style={{color: '#888'}}>UserId: </Text>
            <View style={{flex: 1}}/>
            <Text>{item.UserId}</Text>
          </View>

          <View style={{flexDirection: 'row', paddingLeft: 10, paddingRight: 10}}>
            <Text style={{color: '#888'}}>Timestamp: </Text>
            <View style={{flex: 1}}/>
            <Text>{timeConverter(item.TransactionUnixTimestamp, true)}</Text>
          </View>

          <View style={{flexDirection: 'row', paddingLeft: 10, paddingRight: 10}}>
            <Text style={{color: '#888'}}>Comments: </Text>
            <View style={{flex: 1}}/>
            <Text>{item.Comments}</Text>
          </View>

          <TouchableOpacity>
            <View style={styles.confirmBtnContainer}>
              <Text style={styles.confirmBtnText}>Close Transaction</Text>
            </View>
          </TouchableOpacity>

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
  confirmBtnContainer: {
    marginTop: 20,
    height: 40,
    backgroundColor: '#ddd',
    opacity: 0.8,
    borderRadius: 5,
    justifyContent: 'center',
    alignItems: 'center'
  },
  confirmBtnText: {
    fontWeight: '800',
    fontSize: 20,
    color: 'rgb(70,160,153)'
  }
});