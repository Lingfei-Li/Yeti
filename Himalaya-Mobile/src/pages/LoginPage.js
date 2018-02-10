/**
 * Created by Yida Yin on 1/4/18
 */

import React from 'react';
import {
  Button,
  StyleSheet,
  Text,
  View,
  ImageBackground,
} from 'react-native';
import {AuthSession} from 'expo';
import {inject, observer} from "mobx-react";

import LambdaAPI from '../LambdaAPI';
import log from '../components/log';


const CLIENT_ID = '1420c3c4-8202-411f-870d-64b6166fd980';

@inject("store")
@observer
export default class LoginPage extends React.Component {
  constructor(props) {
    super(props);
  }

  _handlePressAsync = async () => {
    let redirectUrl = AuthSession.getRedirectUrl();
    const authURL =
      `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?` +
      `scope=openid+User.Read+Mail.Read` +
      `&response_type=code` +
      `&client_id=${encodeURIComponent(CLIENT_ID)}` +
      `&redirect_uri=${encodeURIComponent(redirectUrl)}`;

    log.log(`Outlook OAuth URL: ${authURL}`);
    let result = await AuthSession.startAsync({
      authUrl: authURL
    });
    log.log(result);

    if (result && result.type === 'success') {
      const code = result.params.code;
      log.log(`Authorized successfully, code: ${code}`);
      LambdaAPI.uploadOutlookCode(code)
        .then((response) => {
          log.log("Call outlook_oauth, Success! Response: ", response.data);
          // FIXME: Why Response Data is a String...?
          const respData = JSON.parse(response.data);
          this.props.store.email = respData.loginEmail;
          this.props.store.token = respData.token;

          // Navigate to Transaction List View
          this.props.navigation.navigate('TransactionListView')
        })
        .catch((error) => {
          log.log(`Call outlook_oauth, Failed! Status Code: ${error.status}. Error: `, error.response);
        })
    }
  };

  render() {
    return (
      <View style={styles.container}>
        <Button title="Open Outlook Auth" onPress={this._handlePressAsync}/>
        <Button title="Open Transaction List View"
                onPress={() => this.props.navigation.navigate('TransactionListView')}/>
        <Button title="Open Debug View" onPress={() => this.props.navigation.navigate('DebugView')}/>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#B0C1E5',
    alignItems: 'center',
    justifyContent: 'center',
  },
});