echo "****************************************************"
echo "****************************************************"
echo ""
echo "Beaglebone Programming Script - 03/14/2019       "
echo ""
echo "This version is aligned with Processor SDK Linux    "
echo "2.0.0 based on the Linux 4.1 kernel.                " 
echo ""

## Set Server IP here. This commande depends on a default gateway
## being set in the server. In Linux isc-dhcp-server, this is
## done with the routers option in /etc/dhcp/dhcpd.conf. In Uniflash,
## this is done in the open-dhcp config file. This address is 
## usually set to the same address as the server to make it
## the default gateway.
SERVER_IP=$(route -n | grep 'UG[ \t]' | awk '{print $2}')

## If server IP is not set correctly, or can't be discovered with 
## with the above command, set it to a defined default.
while [ "${SERVER_IP}" == "" ]
do
	echo "Server IP not found, waiting..."
	sleep 1
	SERVER_IP=$(route -n | grep 'UG[ \t]' | awk '{print $2}')
done
echo "Server IP Is: ${SERVER_IP}"

## Set the name of the flasher script to be fetched.
DEBRICK_SCRIPT="flasher.sh"

## TFTP Customized flasher script from server
echo "Getting ${DEBRICK_SCRIPT} from server: ${SERVER_IP}"
tftp -g -r ${DEBRICK_SCRIPT} ${SERVER_IP}

## Test to make sure that flasher could be downloaded. Exit if not.
if [ $? -ne 0 ]
	then 
		echo "Unable to fetch flasher script! Exiting..."
		killall -s USR2 ledd
		exit 1
fi

## Make the flasher script executable
chmod +x ${DEBRICK_SCRIPT}

## Test to make sure that flasher could be made executable. Exit if not.
if [ $? -ne 0 ]
	then 
		echo "Unable to make flasher script executable. Exiting..."
		killall -s USR2 ledd
		exit 1
fi

echo ""
echo "**************************************************************"
echo "Bird Flash Fetcher is complete. Executing ${DEBRICK_SCRIPT}."
echo ""

## Execute script. Pass SERVER_IP and MAD_ADDR flasher.sh.
echo "Calling Script=${DEBRICK_SCRIPT} with SERVER_IP=${SERVER_IP}"
./${DEBRICK_SCRIPT} ${SERVER_IP} ${MAC_ADDR}
if [ $? -eq 0 ]
then
	echo "${DEBRICK_SCRIPT} was successful"
	killall -s USR1 ledd
else
	echo "${DEBRICK_SCRIPT} failed, see previous lines for error messages"
	killall -s USR2 ledd
fi