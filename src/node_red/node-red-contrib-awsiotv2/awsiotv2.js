/*module.exports = function(RED) {
    const awsIot = require('aws-iot-device-sdk-v2');
    const fs = require('fs');

    function AwsIotV2Node(config) {
        RED.nodes.createNode(this,config);
        var node = this;
        node.on('input', function(msg) {
            msg.payload = msg.payload.toLowerCase();
            node.send(msg);
        });
    }
    RED.nodes.registerType('awsiotv2', AwsIotV2Node);
}*/



module.exports = function(RED) {

    // require the AWS IoT SDK and file system module
    const awsIot = require('aws-iot-device-sdk-v2');
    const fs = require('fs');

    //The node
    function AwsIotV2Node(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        
        // Get inputs from config
        node.ip = config.ip;
        node.privateKey = config.privateKey;
        node.publicKey = config.publicKey;
        node.caCert = config.caCert;
        node.clientId = config.clientId || 'node-red-client'; // Default client ID

        let client = null;

        // Initialise connection to AWS IoT
        function initializeAwsIotClient() {
            try {
                // Create a client bootstrap object
                // takes in the public and private keys
                new awsIot.io.ClientBootstrap();
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

        // Input event handler for the node
        node.on('input', function(msg) {
            if (client) {
                //assign topic and payload
                const topic = msg.topic || 'test/topic';
                const payload = msg.payload || 'Hello from Node-RED!';

                //publish the message
                client.publish(topic, JSON.stringify(payload), 1)
                    //callback for successful publish
                    .then(() => {
                        node.log(`Message published to ${topic}`);
                        msg.payload = `Message sent to ${topic}: ${payload}`;
                        node.send(msg);
                    })
                    .catch((err) => {
                        node.error('Error publishing message: ' + err.message);
                    });
            } else {
                node.error('AWS IoT client not initialized.');
            }
        });

        // Close connection
        node.on('close', function() {
            if (client) {
                client.disconnect()
                    .then(() => node.log('AWS IoT Disconnected'))
                    .catch((err) => node.error('Error disconnecting: ' + err.message));
            }
        });


        // Initialise the client on node creation
        initializeAwsIotClient();
    }

    // Register the node
    RED.nodes.registerType('awsiotv2', AwsIotV2Node, {
        inputs: 1,
        outputs: 1,
        category: 'AWS IoT',
        //set categories and input values
        defaults: {
            name: { value: '' },
            ip: { value: '' },
            privateKey: { value: '', type: 'text' },
            publicKey: { value: '', type: 'text' },
            caCert: { value: '', type: 'text' },
            clientId: { value: 'node-red-client', type: 'text' }
        },
        credentials: {
            privateKey: { type: 'password' },
            publicKey: { type: 'password' },
            caCert: { type: 'password' }
        }
    });
};

