aws cloudformation deploy ^
   --template-file %1 ^
   --stack-name %2 ^
   --capabilities CAPABILITY_IAM ^
   --parameter-overrides YetiTransactionsTableName=%3 ^
                         YetiLoginsTableName=%4 ^
                         YetiTokensTableName=%5 ^
                         OutlookOAuthClientId=%6 ^
                         OutlookOAuthClientSecret=%7
