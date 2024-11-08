const assert = require('assert');
const helper = require('node-red-node-test-helper');
const awsiotv2Node = require('../awsiotv2.js');

helper.init(require.resolve('node-red'));

describe('AWS IoT v2 Node', function () {

    before(function (done) {
        helper.startServer(done);
    });

    after(function (done) {
        helper.stopServer(done);
    });

    afterEach(function () {
        helper.unload();
    });

    it('should be loaded', function (done) {
        const flow = [{ id: 'n1', type: 'awsiotv2', name: 'test name' }];
        helper.load(awsiotv2Node, flow, function () {
            const n1 = helper.getNode('n1');
            assert.strictEqual(n1.name, 'test name');
            done();
        });
    });
});