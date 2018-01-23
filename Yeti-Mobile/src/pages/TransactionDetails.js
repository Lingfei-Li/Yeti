/**
 * Created by Yida Yin on 1/5/18
 */

import React from 'react';
import {
  Text,
  View,
  FlatList,
  ScrollView,
  TouchableOpacity,
  Alert,
  StyleSheet,
} from 'react-native';
import {inject, observer} from "mobx-react";
import Icon from 'react-native-vector-icons/Entypo';

import Header from '../components/Header';
import LambdaAPI from '../LambdaAPI';
import log from '../components/log';
import {timeConverter} from '../utils';


@inject("store")
@observer
export default class TransactionDetails extends React.Component {
  constructor(props) {
    super(props);
  }

  _handleStatusChange = () => {
    const {item} = this.props.navigation.state.params;
    const {StatusCode, TransactionId, TransactionPlatform} = item;
    const {email, token} = this.props.store;
    if (StatusCode === 0) {
      LambdaAPI.closeTransaction(email, token, TransactionId, TransactionPlatform)
        .then((rsp) => {
          log.log(rsp.data);
          this.props.store.closeTransaction(TransactionId, TransactionPlatform);
        })
        .catch((error) => {
          log.log(error.response);
        });
    } else if (StatusCode === 1) {
      LambdaAPI.reopenTransaction(email, token, TransactionId, TransactionPlatform)
        .then((rsp) => {
          log.log(rsp.data);
          this.props.store.reopenTransaction(TransactionId, TransactionPlatform);
        })
        .catch((error) => {
          log.log(error.response);
        });
    } else {
      log.log(`Unknown statusCode. ${StatusCode}`)
    }
  };

  _handleConfirmBtnClicked = () => {
    const {item} = this.props.navigation.state.params;
    const {StatusCode} = item;

    const title = StatusCode === 0 ? 'Close Transaction' : "Reopen Transaction";
    const text = StatusCode === 0 ? 'Are you sure to close this transaction?' : "Are you sure to reopen this transaction?";

    Alert.alert(
      title,
      text,
      [
        {text: 'Yes', onPress: this._handleStatusChange},
        {text: 'No', onPress: () => log.log('Cancel Pressed'), style: 'cancel'},
      ],
      { cancelable: false }
    );
  };

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
        <ScrollView style={{flex: 1, width: '100%'}}>
          <View style={{flex: 1, alignItems: 'center'}}>
            <Text style={{fontSize: 22, marginTop: 10}}>{item.FriendName}</Text>
            <Text>id: {item.FriendId}</Text>
            <Text style={{fontSize: 20, fontWeight: 'bold', marginTop: 12, marginBottom: 8}}>$ {item.Amount}</Text>
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

            <TouchableOpacity
              onPress={this._handleConfirmBtnClicked}
            >
              <View style={styles.confirmBtnContainer}>
                <Text style={styles.confirmBtnText}>{confirmed ? "Reopen Transaction" : "Close Transaction"}</Text>
              </View>
            </TouchableOpacity>
          </View>
        </ScrollView>
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
    width: 220,
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