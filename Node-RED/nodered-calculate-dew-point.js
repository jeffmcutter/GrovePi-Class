// Convert the payload as follows:
//   1. Delete all non temperature data points.
//   2. Convert temp from C to F.
//
// Sample payload
// {"timestamp": 1519609945872, "data": {"range": 511, "degrees": 222.0, "temperature": 19.0, "humidity": 47.0}}

temperature = msg.payload.data.temperature;
humidity = msg.payload.data.humidity;

for (var key in msg.payload.data) {
    delete msg.payload.data[key];
}

dewpointc = temperature - ( 100 - humidity ) / 5;
dewpointf = dewpointc * 9 / 5 + 32;

msg.payload.data.dewpoint_c = dewpointc.toFixed(1);
msg.payload.data.dewpoint_f = dewpointf.toFixed(1);

return msg;