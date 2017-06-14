library(mrsdeploy)
remoteLogin("http://40.70.64.126:12800", username = DEPLOYR.USER, password = DEPLOYR.PWD)


regularService <- "rService"
realtimeService <- "rtService"
version <- "1.0"

#######################################################################
# Clean up - delete the services                                      #
#######################################################################

deleteService(regularService, version)
deleteService(realtimeService, version)

remoteLogout()
