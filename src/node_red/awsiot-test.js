const awsIot = require('aws-iot-device-sdk-v2');

let node = {
    ip: "a1mcw1hchqljw1-ats.iot.eu-north-1.amazonaws.com",
    privateKey: "E:\\theob\\Documents\\PythonProjects\\HeatSeekers\\aws\\env\\dev\\private.pem.key",
    publicKey: "E:\\theob\\Documents\\PythonProjects\\HeatSeekers\\aws\\env\\dev\\public.pem.key",
    caCert: "E:\\theob\\Documents\\PythonProjects\\HeatSeekers\\aws\\env\\dev\\RootCA1.pem",
    clientId: 'node-red-client', // Default client ID
    error: console.log,
    log: console.log,
    status: console.log,
};
let client = null;

// Get inputs from config


function initialiseAwsIotClient() {
    try {
        // Create a client bootstrap object
        // takes in the public and private keys
        const clientBootstrap = new awsIot.io.ClientBootstrap();
        const configBuilder = awsIot.iot.AwsIotMqttConnectionConfigBuilder
            .new_mtls_builder_from_path(node.publicKey, node.privateKey);
        
        //set the connection configuration
        configBuilder.with_certificate_authority_from_path(undefined, node.caCert);
        configBuilder.with_clean_session(false);
        configBuilder.with_client_id(node.clientId);
        configBuilder.with_endpoint(node.ip);

        const config = configBuilder.build();
        client = new awsIot.mqtt.MqttClient(clientBootstrap);
        const connection = client.new_connection(config);
        
        // connect using the connection object
        connection.connect()
            //callback for successful connection
            .then(() => {
                node.log('AWS IoT Connection Established');
                node.status({ fill: 'green', shape: 'dot', text: 'connected' });
            })
            .catch((err) => {
                node.error('Failed to connect: ' + err.toString());
                node.status({ fill: 'red', shape: 'ring', text: 'disconnected' });
            });

    } catch (err) {
        node.error('Error initializing AWS IoT Client: ' + err.message);
        node.status({ fill: 'red', shape: 'ring', text: 'error' });
    }
}
function connect() {

}

initialiseAwsIotClient();