load("tokens.Rd") ## usernames and passwords

######################################################################
# Import data from SQL Server and construct model locally            #
######################################################################
library(RevoScaleR)
conStr <- paste0("Driver={SQL Server};Server=40.70.64.126;Database=LendingClub;uid=",SQL.USER,
                 ";pwd=",SQL.PWD)

# Create the data source
ds <- RxSqlServerData(sqlQuery="SELECT revol_util, int_rate, mths_since_last_record, annual_inc_joint, dti_joint, total_rec_prncp, all_util,is_bad FROM [dbo].[LoanStats] WHERE (ABS(CAST((BINARY_CHECKSUM(id, NEWID())) as int)) % 100) < 75 ", 
                      connectionString=conStr)
df <- rxImport(ds)

# create the model
rxSetComputeContext("local")
dForestModel <- rxDForest(is_bad ~ revol_util + int_rate + mths_since_last_record + 
                            annual_inc_joint + dti_joint + total_rec_prncp + all_util, 
                          df)

## OR, Train remotely
#sqlCC <- RxInSqlServer(connectionString = conStr)
#rxSetComputeContext(sqlCC)
#dForestModel <- rxDForest(is_bad ~ revol_util + int_rate + mths_since_last_record + annual_inc_joint + dti_joint + total_rec_prncp + all_util, 
#                          ds)

######################################################################
# Deploy model object and publish flexible and realtime services     #
######################################################################

library(mrsdeploy)
remoteLogin("http://40.70.64.126:12800", username = DEPLOYR.USER, password = DEPLOYR.PWD)
pause()

## create snapshot for publishing web service
putLocalObject("dForestModel")  
# resume() to verify it has been delivered

## publish flexible R prediction service
snapshot <- createSnapshot("dforest-model-snapshot")
rCode <- "require(RevoScaleR); prediction <- rxPredict(dForestModel, inputData);"
regularService <- "rService"
version <- "1.0"  
regularServiceApi <- publishService(
  name = regularService,
  v = version,  # multiple versions of a service can be managed
  code = rCode, # here a string, could also be a function or script file
  snapshot = snapshot,
  inputs = list(inputData='data.frame'),
  outputs = list(prediction = 'data.frame'),
  alias = 'rService')

testData <- head(df, n=1)
op1 <- regularServiceApi$rService(inputData = testData)
op1$outputParameters$prediction$is_bad_Pred

# Compare with localy-generated prediction
rxPredict(dForestModel, testData)

## publish a realtime prediction service
realtimeService <- "rtService"
version <- "1.0"
rtServiceApi <- publishService(
  serviceType = 'Realtime',
  name = realtimeService,
  v = version,
  code = NULL,
  model = dForestModel,
  alias = 'rtService')

op2 <- rtServiceApi$rtService(inputData = testData)
op2$outputParameters$outputData$is_bad_Pred

## Compare output of realtime and flexible services
all.equal(op1$outputParameters$prediction$is_bad_Pred, 
          op2$outputParameters$outputData$is_bad_Pred)

#####################################################################
#  Call each prediction services one-by-one and measure time taken  #
#####################################################################

nrows <- 50
testData <- head(df, n = nrows)

# measure time taken for regular R service
print(paste("time taken for regular service for" , nrows, "single-row operations."))
system.time(
  for(i in 1:nrows)
  {
    regularServiceApi$rService(inputData = testData[i,])
  }
)

# measure time taken for realtime R service
print(paste("time taken for realtime service for" , nrows, "single-row operations."))
system.time(
  for(i in 1:nrows)
  {
    rtServiceApi$rtService(inputData = testData[i,])
  }
)

remoteLogout()
