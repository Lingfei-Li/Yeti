aws cloudformation deploy ^
   --template-file %1 ^
   --stack-name %2 ^
   --capabilities CAPABILITY_IAM ^
   --parameter-overrides YetiTransactionsTableName=%3
